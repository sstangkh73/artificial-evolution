"""Proof-of-concept brittle fracture of a 2D stone section (plane strain).

Nothing here encodes "tools". A stone is a grid of material cells. A strike is
a force applied over a small patch at an angle. Linear elastic FEM gives the
stress field; elements whose maximum principal (tensile) stress exceeds the
material's tensile strength fail and are removed, the stress is re-solved,
and this repeats until nothing more fails. Whatever pieces are left are
measured afterwards: their mass, and the most acute edge angle on their
outline. Sharpness is therefore a measured geometric outcome, not an input.

Strength comes from linear elastic fracture mechanics with an inherent flaw
size a0 (Griffith/Irwin): sigma_f = K_IC / sqrt(pi * a0).

Dimension-agnostic interface: `Stone` holds an integer cell grid of any
dimension; only the 2D CST element is implemented here. 3D (linear tets) is
the planned deep-check path, reusing the Formula Ultimate tetrahedral solver.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math

import numpy as np

try:  # scipy makes the solve sparse; dense numpy works for small grids.
    from scipy.sparse import coo_matrix
    from scipy.sparse.linalg import spsolve
except ImportError:  # pragma: no cover
    coo_matrix = None


@dataclass(frozen=True)
class Material:
    name: str
    youngs_modulus_pa: float
    poisson_ratio: float
    density_kg_m3: float
    toughness_pa_sqrt_m: float  # K_IC
    flaw_size_m: float  # a0, inherent flaw (grain-scale)

    @property
    def tensile_strength_pa(self) -> float:
        return self.toughness_pa_sqrt_m / math.sqrt(math.pi * self.flaw_size_m)


@dataclass
class Stone:
    cells: np.ndarray  # int grid, 0 = empty, k = materials[k-1]
    materials: tuple[Material, ...]
    cell_size_m: float
    thickness_m: float = 0.03  # out-of-plane depth for plane strain (2D only)
    meta: dict = field(default_factory=dict)

    @property
    def dim(self) -> int:
        return self.cells.ndim


# --------------------------------------------------------------------------
# Mesh: each filled cell -> 2 triangles (alternating diagonal to limit bias)
# --------------------------------------------------------------------------


def build_mesh(stone: Stone):
    if stone.dim != 2:
        raise NotImplementedError("3D path: linear tetrahedra (planned)")
    ny, nx = stone.cells.shape
    h = stone.cell_size_m
    node_id = -np.ones((ny + 1, nx + 1), dtype=np.int64)
    nodes, tris, tri_mat, tri_cell = [], [], [], []

    def nid(j, i):
        if node_id[j, i] < 0:
            node_id[j, i] = len(nodes)
            nodes.append((i * h, j * h))
        return node_id[j, i]

    for j in range(ny):
        for i in range(nx):
            m = stone.cells[j, i]
            if m == 0:
                continue
            a, b, c, d = nid(j, i), nid(j, i + 1), nid(j + 1, i + 1), nid(j + 1, i)
            pair = ((a, b, c), (a, c, d)) if (i + j) % 2 == 0 else ((a, b, d), (b, c, d))
            for t in pair:
                tris.append(t)
                tri_mat.append(m - 1)
                tri_cell.append((j, i))
    return np.array(nodes, float), np.array(tris, np.int64), np.array(tri_mat), np.array(tri_cell)


def _d_matrix(mat: Material) -> np.ndarray:
    e, v = mat.youngs_modulus_pa, mat.poisson_ratio
    f = e / ((1 + v) * (1 - 2 * v))
    return f * np.array([[1 - v, v, 0], [v, 1 - v, 0], [0, 0, (1 - 2 * v) / 2]])


def _b_matrices(nodes, tris):
    p = nodes[tris]  # (n,3,2)
    x, y = p[..., 0], p[..., 1]
    area = 0.5 * ((x[:, 1] - x[:, 0]) * (y[:, 2] - y[:, 0]) - (x[:, 2] - x[:, 0]) * (y[:, 1] - y[:, 0]))
    bcoef = np.stack([y[:, 1] - y[:, 2], y[:, 2] - y[:, 0], y[:, 0] - y[:, 1]], axis=1)
    ccoef = np.stack([x[:, 2] - x[:, 1], x[:, 0] - x[:, 2], x[:, 1] - x[:, 0]], axis=1)
    b = np.zeros((len(tris), 3, 6))
    b[:, 0, 0::2] = bcoef
    b[:, 1, 1::2] = ccoef
    b[:, 2, 0::2] = ccoef
    b[:, 2, 1::2] = bcoef
    b /= (2 * area)[:, None, None]
    return b, np.abs(area)


def solve_stress(stone: Stone, nodes, tris, tri_mat, alive, fixed_nodes, loads):
    """Plane-strain linear elastic solve. Returns principal stress per element."""
    t = stone.thickness_m
    idx = np.flatnonzero(alive)
    b, area = _b_matrices(nodes, tris[idx])
    dmats = np.stack([_d_matrix(m) for m in stone.materials])[tri_mat[idx]]
    ke = np.einsum("nki,nkl,nlj->nij", b, dmats, b) * (area * t)[:, None, None]
    dofs = np.stack([2 * tris[idx], 2 * tris[idx] + 1], axis=2).reshape(len(idx), 6)
    ndof = 2 * len(nodes)
    rows = np.repeat(dofs, 6, axis=1).ravel()
    cols = np.tile(dofs, (1, 6)).ravel()
    f = np.zeros(ndof)
    for node, (fx, fy) in loads.items():
        f[2 * node] += fx
        f[2 * node + 1] += fy
    used = np.zeros(ndof, bool)
    used[dofs.ravel()] = True
    fixed = np.zeros(ndof, bool)
    for node in fixed_nodes:
        fixed[2 * node] = fixed[2 * node + 1] = True
    free = np.flatnonzero(used & ~fixed)
    u = np.zeros(ndof)
    if coo_matrix is not None:
        k = coo_matrix((ke.ravel(), (rows, cols)), shape=(ndof, ndof)).tocsr()
        kff = k[free][:, free]
        # Pieces cut off from the supports are rigid-body free; a tiny
        # ground spring keeps the system solvable without affecting stress
        # in supported material.
        kff = kff + coo_matrix((np.full(len(free), 1e-9 * ke.max()), (range(len(free)), range(len(free)))), shape=kff.shape)
        u[free] = spsolve(kff.tocsc(), f[free])
    else:
        k = np.zeros((ndof, ndof))
        np.add.at(k, (rows, cols), ke.ravel())
        kff = k[np.ix_(free, free)] + np.eye(len(free)) * 1e-9 * ke.max()
        u[free] = np.linalg.solve(kff, f[free])
    strain = np.einsum("nij,nj->ni", b, u[dofs])
    stress = np.einsum("nij,nj->ni", dmats, strain)
    sx, sy, txy = stress.T
    c = (sx + sy) / 2
    r = np.sqrt(((sx - sy) / 2) ** 2 + txy**2)
    s1 = np.full(len(tris), np.nan)
    s1[idx] = c + r
    return s1


# --------------------------------------------------------------------------
# A strike and its aftermath
# --------------------------------------------------------------------------


@dataclass
class StrikeResult:
    failed_elements: int
    iterations: int
    pieces: list[dict]
    solve_seconds: float


def _surface_nodes_near(nodes, tris, alive, point, radius):
    used = np.unique(tris[alive])
    d = np.linalg.norm(nodes[used] - np.asarray(point), axis=1)
    return used[d <= radius]


def strike(stone: Stone, point_m, angle_deg: float, force_n: float, support_point_m, support_radius_m=None,
           patch_radius_m=None, max_iterations: int = 60, fail_fraction: float = 0.25,
           nonlocal_radius_m: float | None = None) -> StrikeResult:
    """Quasi-static strike. angle_deg is measured from +x; the force points
    along (cos, sin). Supports are the nodes near support_point_m (the anvil
    or hand). Elements fail when sigma_1 > tensile strength; each round the
    worst `fail_fraction` of failing elements are removed (progressive
    failure), until nothing fails or max_iterations.

    Physical lengths (contact patch, support, nonlocal radius) are given in
    metres so that refining the mesh does not change the physics. With
    nonlocal_radius_m, the failure test uses sigma_1 averaged over that
    radius (a material length), which removes the mesh dependence of a
    purely local criterion."""
    import time

    nodes, tris, tri_mat, tri_cell = build_mesh(stone)
    h = stone.cell_size_m
    patch_radius_m = patch_radius_m or 1.6 * h
    support_radius_m = support_radius_m or 4 * h
    alive = np.ones(len(tris), bool)
    centroids = nodes[tris].mean(axis=1)
    neighbours = None
    if nonlocal_radius_m:
        from scipy.spatial import cKDTree
        tree = cKDTree(centroids)
        neighbours = tree.query_ball_point(centroids, nonlocal_radius_m)
    strength = np.array([m.tensile_strength_pa for m in stone.materials])[tri_mat]
    fixed = set(_surface_nodes_near(nodes, tris, alive, support_point_m, support_radius_m).tolist())
    patch = _surface_nodes_near(nodes, tris, alive, point_m, patch_radius_m)
    direction = np.array([math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))])
    loads = {int(n): tuple(direction * force_n / len(patch)) for n in patch}
    failed = 0
    started = time.perf_counter()
    it = 0
    for it in range(1, max_iterations + 1):
        s1 = solve_stress(stone, nodes, tris, tri_mat, alive, fixed, loads)
        if neighbours is not None:
            s_alive = np.where(alive, s1, np.nan)
            s1 = np.array([np.nanmean(s_alive[nb]) if alive[e] else np.nan for e, nb in enumerate(neighbours)])
        ratio = np.where(alive, s1 / strength, -np.inf)
        over = np.flatnonzero(ratio > 1.0)
        if len(over) == 0:
            break
        k = max(1, int(math.ceil(fail_fraction * len(over))))
        worst = over[np.argsort(ratio[over])[-k:]]
        alive[worst] = False
        failed += len(worst)
        # Loaded nodes that lost all their elements stop carrying load.
        live_nodes = set(np.unique(tris[alive]).tolist())
        loads = {n: v for n, v in loads.items() if n in live_nodes}
        if not loads:
            break
    elapsed = time.perf_counter() - started
    pieces = measure_pieces(stone, nodes, tris, tri_mat, alive)
    return StrikeResult(failed, it, pieces, elapsed)


# --------------------------------------------------------------------------
# Measurement (analyst side): pieces, mass, edge angle
# --------------------------------------------------------------------------


def _components(tris, alive):
    idx = np.flatnonzero(alive)
    parent = {int(e): int(e) for e in idx}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    edge_owner: dict[tuple[int, int], int] = {}
    for e in idx:
        t = tris[e]
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            key = (min(a, b), max(a, b))
            if key in edge_owner:
                ra, rb = find(int(e)), find(edge_owner[key])
                if ra != rb:
                    parent[ra] = rb
            else:
                edge_owner[key] = int(e)
    groups: dict[int, list[int]] = {}
    for e in idx:
        groups.setdefault(find(int(e)), []).append(int(e))
    return list(groups.values())


def _boundary_loops(tris, elements):
    count: dict[tuple[int, int], int] = {}
    directed = {}
    for e in elements:
        t = tris[e]
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            key = (min(a, b), max(a, b))
            count[key] = count.get(key, 0) + 1
            directed[key] = (int(a), int(b))
    nxt = {}
    for key, n in count.items():
        if n == 1:
            a, b = directed[key]
            nxt.setdefault(a, []).append(b)
    loops, seen = [], set()
    for start in list(nxt):
        if start in seen:
            continue
        loop, cur = [], start
        while cur not in seen and cur in nxt:
            seen.add(cur)
            loop.append(cur)
            cur = nxt[cur][0]
        if len(loop) >= 6:
            loops.append(loop)
    return loops


def edge_angles_deg(points: np.ndarray, span: int) -> np.ndarray:
    """Interior angle at each outline vertex, using neighbours `span` steps
    away so that the cell staircase is averaged out. Smaller = sharper."""
    n = len(points)
    out = np.empty(n)
    for i in range(n):
        a = points[(i - span) % n] - points[i]
        b = points[(i + span) % n] - points[i]
        cosang = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-30)
        out[i] = math.degrees(math.acos(max(-1.0, min(1.0, cosang))))
    return out


def measure_pieces(stone, nodes, tris, tri_mat, alive, span: int = 4):
    h, t = stone.cell_size_m, stone.thickness_m
    density = np.array([m.density_kg_m3 for m in stone.materials])
    _, area = _b_matrices(nodes, tris)
    pieces = []
    for elements in _components(tris, alive):
        mass = float(np.sum(area[elements] * density[tri_mat[elements]]) * t)
        loops = _boundary_loops(tris, elements)
        min_angle = None
        if loops:
            outer = max(loops, key=len)
            pts = nodes[outer]
            if len(pts) > 2 * span + 2:
                ang = edge_angles_deg(pts, span)
                # Convex corners only: concave notches are not edges.
                cross = []
                n = len(pts)
                for i in range(n):
                    a = pts[i] - pts[(i - span) % n]
                    b = pts[(i + span) % n] - pts[i]
                    cross.append(a[0] * b[1] - a[1] * b[0])
                convex = np.array(cross) > 0
                if convex.any():
                    min_angle = float(ang[convex].min())
        pieces.append({"elements": len(elements), "mass_kg": mass, "min_edge_angle_deg": min_angle,
                       "resolution_span_m": span * h})
    pieces.sort(key=lambda p: -p["mass_kg"])
    return pieces


def disc_stone(n: int, material: Material, diameter_m: float = 0.10, squash: float = 0.6) -> Stone:
    """An elliptical pebble section, n cells across."""
    j, i = np.mgrid[0:n, 0:n]
    cx = cy = (n - 1) / 2
    inside = ((i - cx) / (n / 2)) ** 2 + ((j - cy) / (n * squash / 2)) ** 2 <= 1.0
    return Stone(inside.astype(np.int64), (material,), diameter_m / n)
