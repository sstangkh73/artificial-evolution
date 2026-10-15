"""Fracture of a 2D stone section under a blow: planar contact + phase field.

Step 4 part (c). The stone section (``Stone`` with dim=2) is meshed cell by
cell (``fem2d.build_mesh``) and solved in plane strain with thickness
``stone.thickness_m``. The hammer is the equivalent rigid indenter of
``indentation`` (R' = R E'_core / E*, Johnson 1985 sec. 4.2), here a rigid
cylinder along the out-of-plane axis with a parabolic profile (small slope),
frictionless and unilateral. It moves along the unit vector ``direction``
through the point ``contact_point_m``; the work it does on the section is
limited by the energy budget with ``indentation.budget_loop``.

How the section is held (quasi-static, as in ``indentation``):

- ``hand``: the stone is free; the blow is balanced by the inertia of the
  stone (inertia relief: D'Alembert body force -rho (a + alpha x r) of a rigid
  acceleration (a, alpha) that balances the contact force and moment). The
  displacement gauge is sum m_i u_i = 0 and the rigid rotation of the lumped
  masses is 0, so the approach is measured from the centre of mass, as d1 =
  x_hammer - x_core in ``impact.lumped_impact``. The hand spring is left out
  (its force is < 0.5 % of the peak in ``impact`` tests).
  With this gauge 1/2 u.K.u = 1/2 sum lambda_i g_i: the work of the contact
  forces on the relative displacement is the stored energy.
- ``anvil``: a second rigid indenter, fixed, pushing along -direction on the
  line through ``contact_point_m`` (bipolar / passive-hammer geometry), with
  its own equivalent radius R'_a = R_a E'_core / E*_ca. Translation along the
  tangent and rotation are balanced by inertia relief as above.

Assumptions (02 sec. 4.5): plane strain with the whole budget of the 3D blow
in the section of thickness ``stone.thickness_m``; the contact law of the
section is line contact (cylinder), not the sphere of ``impact``.

Pieces: a cell is on a crack when the largest damage at its four nodes is at
least ``D_BROKEN``. The phase field resolves a crack only to within its
length l, and the quasi-static blow ends (``RELEASE_FRACTION``) while the
last ligament ahead of a crack tip can still be partly damaged; so a cell with
d >= ``D_PROCESS`` within l of a crack cell (centre distance) is also cut
(numerical rule, 02 sec. 4.5). Diffuse damage far from a crack never cuts.
Intact cells are grouped into face-connected components
(4-neighbour: corner contact carries no material face); each broken cell joins
the component of the nearest intact cell (Euclidean distance between cell
centres), so every filled cell ends in exactly one piece and mass is kept.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy import ndimage

from . import fem2d
from . import phasefield as pf
from .indentation import IndentResult, budget_loop
from .stone import Stone

MODE = "plane_strain"
# numerical choice: g(0.95) = 0.0025, the band carries < 0.3 % of the intact stiffness
D_BROKEN = 0.95
# numerical choice: the blow ends when the hammer force has fallen below 1 %
# of its peak (the section no longer resists the indenter, e.g. the struck
# part has broken off; a force drop is not by itself proof of separation, see
# ``split_pieces``). The rest of the budget is not absorbed by the section and
# is not tracked (no kinetic energy of pieces in this quasi-static model)
RELEASE_FRACTION = 0.01
# numerical choice: AT1 profile value (1 - x/2l)^2 at x = 0.59 l
D_PROCESS = 0.5


@dataclass(frozen=True)
class Indenter:
    """Rigid parabolic indenter moving along ``normal`` (unit, into the body)."""

    nodes: np.ndarray  # candidate surface nodes
    normal: np.ndarray  # (2,)
    s: np.ndarray  # lateral coordinate of the candidates (m)
    target0: np.ndarray  # normal displacement imposed at approach 0 (m)
    moves: bool  # True: approach = delta; False: fixed (approach 0)


def make_indenter(mesh: fem2d.Mesh2D, origin_m, normal, radius_m: float, moves: bool = True,
                  reach_m: float | None = None) -> Indenter:
    """Indenter profile q(s) = tip - s^2 / (2 R) in the frame (s, q) with q
    along ``normal`` from ``origin_m``; the tip starts where it first touches
    a boundary node with |s| <= ``reach_m`` (default R). Node i is pushed to
    n.u_i >= tip + delta - s_i^2/(2R) - q_i."""
    n = np.asarray(normal, dtype=float)
    n = n / np.linalg.norm(n)
    t = np.array([-n[1], n[0]])
    edges, _ = fem2d.boundary_edges(mesh)
    nodes = np.unique(edges)
    rel = mesh.nodes[nodes] - np.asarray(origin_m, dtype=float)[:2]
    s, q = rel @ t, rel @ n
    keep = np.abs(s) <= (radius_m if reach_m is None else reach_m)
    if not keep.any():
        raise ValueError("no surface node within reach of the indenter line")
    nodes, s, q = nodes[keep], s[keep], q[keep]
    tip = float(np.min(q + s ** 2 / (2.0 * radius_m)))
    return Indenter(nodes=nodes, normal=n, s=s, target0=tip - s ** 2 / (2.0 * radius_m) - q, moves=moves)


def lumped_masses(mesh: fem2d.Mesh2D, density: np.ndarray) -> np.ndarray:
    """Nodal masses (kg): each element's mass split equally to its 4 nodes."""
    m_el = density * mesh.h ** 2 * mesh.thickness_m
    m = np.zeros(len(mesh.nodes))
    np.add.at(m, mesh.elements.ravel(), np.repeat(m_el / 4.0, 4))
    return m


def rigid_modes(mesh: fem2d.Mesh2D, masses: np.ndarray, kinds: tuple[str, ...], tangent=None) -> np.ndarray:
    """Columns M phi of the rigid modes in ``kinds`` ('x', 'y', 't' along
    ``tangent``, 'rot' about the centre of mass), shape (n_dof, k)."""
    c = masses @ mesh.nodes / masses.sum()
    cols = []
    for kind in kinds:
        phi = np.zeros((len(mesh.nodes), 2))
        if kind == "x":
            phi[:, 0] = 1.0
        elif kind == "y":
            phi[:, 1] = 1.0
        elif kind == "t":
            phi[:] = np.asarray(tangent, dtype=float)
        elif kind == "rot":
            phi[:, 0] = -(mesh.nodes[:, 1] - c[1])
            phi[:, 1] = mesh.nodes[:, 0] - c[0]
        else:
            raise ValueError(f"unknown rigid mode {kind!r}")
        cols.append((masses[:, None] * phi).ravel())
    return np.stack(cols, axis=1)


def _constraint_matrix(n_dof: int, indenters, actives) -> sp.csc_matrix:
    rows, cols, vals = [], [], []
    j = 0
    for ind, act in zip(indenters, actives):
        for node in ind.nodes[act]:
            rows += [2 * node, 2 * node + 1]
            cols += [j, j]
            vals += [ind.normal[0], ind.normal[1]]
            j += 1
    return sp.csc_matrix((vals, (rows, cols)), shape=(n_dof, j))


class _GaugedSaddle:
    """Solver for saddle systems [[K, D], [D^T, 0]] [u; y] = [f; r] with the
    stiffness K of a free body (singular: rigid modes) and few dense
    constraint columns D (n, m).

    K is factorised once as K~ = K + E E^T, E = sqrt(mean diag K) on three
    pinned dofs (u_x, u_y of the node nearest the centroid, and the dof of the
    farthest node that best resists rotation about it), which is sparse and
    nonsingular. With z = E^T u the system becomes K~ u = f - D y + E z, so
    u = K~^-1 (f - D y + E z) and the m + 3 unknowns (y, z) solve a small dense
    system (Schur complement; the bordered matrix with dense rows of
    inertia relief fills in badly in a sparse LU). One step of iterative
    refinement on the full residual follows. The solution is that of the
    original system; the pins only enter the factorisation."""

    def __init__(self, K: sp.spmatrix, nodes: np.ndarray):
        n = K.shape[0]
        self.K = K.tocsr()
        c = nodes.mean(axis=0)
        p0 = int(np.argmin(np.linalg.norm(nodes - c, axis=1)))
        arm = nodes - nodes[p0]
        p1 = int(np.argmax(np.linalg.norm(arm, axis=1)))
        dof1 = 2 * p1 + int(np.argmax(np.abs([-arm[p1, 1], arm[p1, 0]])))
        dofs = [2 * p0, 2 * p0 + 1, dof1]
        self.E = np.zeros((n, 3))
        self.E[dofs, [0, 1, 2]] = math.sqrt(float(K.diagonal().mean()))
        Es = sp.csc_matrix(self.E)
        self.lu = spla.splu((K + Es @ Es.T).tocsc(), permc_spec="MMD_AT_PLUS_A")
        self.XE = self.lu.solve(self.E)

    def solve(self, D: np.ndarray, f: np.ndarray, r: np.ndarray):
        """(u, y); ``f`` (n,) or (n, k), ``r`` (m,) or (m, k)."""
        import scipy.linalg as sla

        m = D.shape[1]
        XD = self.lu.solve(np.ascontiguousarray(D)) if m else np.zeros((D.shape[0], 0))
        S = np.block([[-D.T @ XD, D.T @ self.XE], [-self.E.T @ XD, self.E.T @ self.XE - np.eye(3)]])
        fac = sla.lu_factor(S)

        def once(f_, r_):
            Xf = self.lu.solve(f_)
            yz = sla.lu_solve(fac, np.concatenate([r_ - D.T @ Xf, -self.E.T @ Xf]))
            return Xf - XD @ yz[:m] + self.XE @ yz[m:], yz[:m]

        f = np.asarray(f, dtype=float)
        r = np.asarray(r, dtype=float)
        u, y = once(f, r)
        # iterative refinement until the residual of the original system is
        # small: 1e-10 relative to max(|K u|, |D y|, |f|) and to |D| |u|
        for _ in range(5):
            res_f, res_r = f - self.K @ u - D @ y, r - D.T @ u
            size = max(np.abs(self.K @ u).max(), np.abs(D @ y).max(), np.abs(f).max(), 1e-300)
            size_r = max(np.abs(D).max() * np.abs(u).max() if m else 0.0, np.abs(r).max() if r.size else 0.0, 1e-300)
            if np.abs(res_f).max() <= 1e-10 * size and (not m or np.abs(res_r).max() <= 1e-10 * size_r):
                return u, y
            du, dy = once(res_f, res_r)
            u, y = u + du, y + dy
        raise RuntimeError("saddle solve: residual above 1e-10 after refinement (ill-conditioned K)")


def _dual_actives(saddle: _GaugedSaddle, B, free_direction, indenters, targets, candidates):
    """Active sets from the dual of the contact problem restricted to the
    ``candidates`` nodes (one bool array per indenter).

    With every rigid mode gauged (columns of ``B`` plus, if given, the unit
    translation phi along ``free_direction``), the contact forces lambda >= 0
    minimise 1/2 lambda.G.lambda - (g - r a).lambda with G = C^T S C (S the
    gauged compliance): the dual of the primal problem, a convex quadratic
    programme (e.g. Kikuchi & Oden 1988, *Contact Problems in Elasticity*,
    ch. 6). It is solved exactly by non-negative least squares on the
    Cholesky factor of G (Lawson & Hanson 1974, *Solving Least Squares
    Problems*, ch. 23), which always terminates. ``free_direction`` is a rigid
    translation held only by the indenters (anvil: the strike line), with
    amplitude r and a = C^T phi; r is the root of a.lambda(r) = 0 (no net
    force along phi, so the gauge column carries no load), a decreasing
    function of r, found by Brent's method.

    G is multiplied by k_ref (a positive scale, for conditioning), so the
    NNLS solution is lambda / k_ref; only its sign pattern is used. A node is
    active when its scaled force exceeds 1e-12 of the largest. The shift
    added to G only if the Cholesky factorisation fails (round-off) changes
    the QP; the active sets are then checked by the caller with the
    original saddle system."""
    from scipy.linalg import cho_factor, solve_triangular
    from scipy.optimize import brentq, nnls

    n = saddle.K.shape[0]
    k_ref = float(saddle.K.diagonal().mean())
    C = _constraint_matrix(n, indenters, candidates).toarray()
    Ball = B
    if free_direction is not None:
        phi = np.tile(np.asarray(free_direction, dtype=float), n // 2)
        a = C.T @ phi
        Ball = np.hstack([B, (phi / np.linalg.norm(phi) * k_ref)[:, None]])
    g = np.concatenate([t[c] for t, c in zip(targets, candidates)])
    X, _ = saddle.solve(Ball, C, np.zeros((Ball.shape[1], C.shape[1])))
    G = k_ref * (C.T @ X)
    G = 0.5 * (G + G.T)
    jitter = 0.0
    while True:  # G is SPD in exact arithmetic; a tiny shift guards round-off
        try:
            L = cho_factor(G + jitter * np.eye(len(G)), lower=True)[0]
            break
        except np.linalg.LinAlgError:
            jitter = max(1e-14 * float(np.trace(G)) / len(G), 10.0 * jitter)
    L = np.tril(L)

    def forces(r):
        b = g - r * a if free_direction is not None else g
        return nnls(L.T, solve_triangular(L, b, lower=True), maxiter=50 * len(g))[0]

    if free_direction is not None:
        scale = float(np.abs(g).max()) + 1e-12
        lo, hi = -scale, scale
        for _ in range(200):
            if forces(lo) @ a > 0:
                break
            lo *= 2.0
        for _ in range(200):
            if forces(hi) @ a < 0:
                break
            hi *= 2.0
        r = brentq(lambda v: forces(v) @ a, lo, hi, xtol=1e-15 * scale, rtol=1e-14)
        lam = forces(r)
    else:
        lam = forces(0.0)
    out, j = [], 0
    floor = 1e-12 * float(lam.max()) if lam.size else 0.0
    for c in candidates:
        act = np.zeros_like(c)
        idx = np.nonzero(c)[0]
        act[idx] = lam[j:j + len(idx)] > floor
        j += len(idx)
        out.append(act)
    return out


def contact_solve(K: sp.spmatrix, mphi: np.ndarray, indenters, delta: float, actives,
                  nodes: np.ndarray, max_iter: int = 100, free_direction=None):
    """Frictionless unilateral contact of rigid indenters with the body and
    inertia relief for the rigid modes in ``mphi``. Saddle system

        K u - C lambda + M phi q = 0,  C^T u = g,  (M phi)^T u = 0

    (lambda >= 0 contact forces along each indenter normal, q the rigid
    accelerations; the columns of M phi are rescaled for conditioning, so the
    solved q is proportional to, not equal to, the acceleration). Active sets start from ``actives``; a node is released if
    its force is tensile and added if it penetrates.
    This update can cycle when the body under an indenter is badly damaged;
    then the active sets come from the exact dual (``_dual_actives``) on the
    nodes seen active so far (``free_direction``: the rigid translation not
    in ``mphi``, held only by the indenters), and nodes that still penetrate
    are added to the candidates (and the dual solved again) until none does;
    the candidates only grow, so this ends. A force counts as tensile below
    -1e-12 of the total (round-off of the saddle solve). ``nodes``:
    mesh node coordinates (to pin the rigid modes in ``_GaugedSaddle``).
    Returns (u, nodal forces per indenter (N, one per candidate node), actives)."""
    n = K.shape[0]
    k_ref = float(K.diagonal().mean())
    B = mphi / np.linalg.norm(mphi, axis=0) * k_ref  # same span, better scaled
    saddle = _GaugedSaddle(K, np.asarray(nodes, dtype=float))
    targets = [ind.target0 + (delta if ind.moves else 0.0) for ind in indenters]
    tol = 1e-12 * max(delta, 1e-9)
    actives = [a.copy() if a.any() else t >= -tol for a, t in zip(actives, targets)]
    seen = set()
    candidates = [a.copy() for a in actives]
    dual = False
    for _ in range(max_iter):
        key = b"".join(a.tobytes() for a in actives)
        if dual or key in seen:  # cycle: take the active sets from the dual
            candidates = [c | a for c, a in zip(candidates, actives)]
            actives = _dual_actives(saddle, B, free_direction, indenters, targets, candidates)
            dual = True
        seen.add(key)
        candidates = [c | a for c, a in zip(candidates, actives)]
        C = _constraint_matrix(n, indenters, actives).toarray() * k_ref
        g = np.concatenate([t[a] for t, a in zip(targets, actives)])
        na = C.shape[1]
        u, y = saddle.solve(np.hstack([-C, B]), np.zeros(n), np.concatenate([-k_ref * g, np.zeros(B.shape[1])]))
        lam = k_ref * y[:na]
        lam_tol = 1e-12 * float(np.abs(lam).sum())
        changed = False
        new, forces, j = [], [], 0
        for ind, act, t, cand in zip(indenters, actives, targets, candidates):
            lam_i = np.zeros(len(ind.nodes))
            k = int(act.sum())
            lam_i[act] = lam[j:j + k]
            j += k
            un = u[2 * ind.nodes] * ind.normal[0] + u[2 * ind.nodes + 1] * ind.normal[1]
            release = act & (lam_i < -lam_tol)
            add = ~act & (un < t - tol)
            if dual:
                # the dual set is exact on the candidates: only nodes outside
                # them may still penetrate (they enlarge the candidates, so
                # this ends); a clearly tensile force means the two solves
                # disagree
                if np.any(lam_i[act] < -1e-8 * float(np.abs(lam).sum())):
                    raise RuntimeError("contact: dual and saddle solutions disagree")
                release = np.zeros_like(act)
                add = add & ~cand
            changed = changed or release.any() or add.any()
            new.append((act & ~release) | add)
            forces.append(lam_i)
        if not changed:
            return u, forces, actives
        actives = new
    raise RuntimeError("contact active set did not converge")


def phase_constants(stone: Stone, mesh: fem2d.Mesh2D):
    """(G_c, l) per element from the phase of each cell (``pf.material_constants``)."""
    gl = np.array([pf.material_constants(p, MODE) for p in stone.phases])
    ph = stone.cells[mesh.cell_index[:, 0], mesh.cell_index[:, 1]] - 1
    return gl[ph, 0], gl[ph, 1]


@dataclass(frozen=True)
class BlowResult:
    mesh: fem2d.Mesh2D
    indent: IndentResult  # approach, force, work, u, d of the hammer indenter
    support_force_n: float  # anvil reaction at the last step (0 for a hand)
    contact_nodes: np.ndarray  # mesh nodes touched by the hammer at the last step
    cell_damage: np.ndarray  # largest nodal d per cell, shape of stone.cells (0 empty)
    piece_of_cell: np.ndarray  # piece index per cell (-1 empty)
    pieces: list  # Stone per piece, heaviest first
    min_h_over_l: float  # mesh resolution of the phase field (cell size / l)


def fracture_blow(stone: Stone, contact_point_m, direction, rigid_radius_m: float, budget_j: float,
                  anvil_rigid_radius_m: float | None = None, split: str = "rankine",
                  n_steps: int = 10, budget_rtol: float = 0.02, tol: float = 1e-3,
                  max_iter: int = 300, progress=None) -> BlowResult:
    """Press the equivalent rigid indenter into ``stone`` until its work
    reaches ``budget_j`` (J, whole section), then split the pieces.
    ``anvil_rigid_radius_m`` None: hand-held (inertia relief in x, y, rot)."""
    if stone.dim != 2:
        raise ValueError("fracture_blow needs a 2D stone")
    if budget_j <= 0:
        raise ValueError("budget must be positive")
    mesh = fem2d.build_mesh(stone)
    n = np.asarray(direction, dtype=float)
    n = n / np.linalg.norm(n)
    g_c, ell = phase_constants(stone, mesh)
    rho = np.array([p.density_kg_m3 for p in stone.phases])
    density = rho[stone.cells[mesh.cell_index[:, 0], mesh.cell_index[:, 1]] - 1]
    masses = lumped_masses(mesh, density)
    hammer = make_indenter(mesh, contact_point_m, n, rigid_radius_m)
    indenters = [hammer]
    if anvil_rigid_radius_m is None:
        mphi = rigid_modes(mesh, masses, ("x", "y", "rot"))
    else:
        indenters.append(make_indenter(mesh, contact_point_m, -n, anvil_rigid_radius_m, moves=False,
                                       reach_m=anvil_rigid_radius_m))
        mphi = rigid_modes(mesh, masses, ("t", "rot"), tangent=(-n[1], n[0]))
    free = None if anvil_rigid_radius_m is None else n
    support = {"force": 0.0, "nodes": np.zeros(0, dtype=int)}

    def solve_u(d, actives, delta):
        K = fem2d.assemble(mesh, MODE, pf.degradation(pf.at_gauss_points(mesh, d)))
        return contact_solve(K, mphi, indenters, delta, actives, mesh.nodes, free_direction=free)

    def step(delta, d_prev, actives):
        d = d_prev.copy()
        inner_ok, change = True, math.inf
        for _ in range(max_iter):
            u, _, actives = solve_u(d, actives, delta)
            pos, _ = pf.energy_split(mesh, MODE, u, split)
            res = pf.solve_damage(mesh, MODE, pos, g_c, ell, d_prev, d)
            inner_ok = inner_ok and res.converged
            change = float(np.max(np.abs(res.d - d)))
            d = res.d
            if change < tol:
                break
        u, forces, actives = solve_u(d, actives, delta)
        support["force"] = float(forces[1].sum()) if len(forces) > 1 else 0.0
        support["nodes"] = hammer.nodes[actives[0]]
        width = float(np.abs(hammer.s[actives[0]]).max()) if actives[0].any() else 0.0
        return u, float(forces[0].sum()), actives, d, change < tol and inner_ok, width

    # step size from the uncracked line contact is not closed-form (log
    # term); use the sphere estimate of ``indent_with_budget`` per unit
    # length as a scale only
    e_prime = float(np.max(mesh.youngs_pa / (1.0 - mesh.poisson ** 2)))
    delta_scale = (15.0 * budget_j / (8.0 * e_prime * math.sqrt(rigid_radius_m))) ** 0.4
    state0 = [np.zeros(len(i.nodes), dtype=bool) for i in indenters]
    indent = budget_loop(mesh, MODE, step, state0, delta_scale / n_steps, budget_j, g_c, ell,
                         n_steps, budget_rtol, None, progress, release_fraction=RELEASE_FRACTION)
    cell_damage, piece_of_cell, pieces = split_pieces(stone, mesh, indent.d, ell)
    return BlowResult(mesh=mesh, indent=indent, support_force_n=support["force"],
                      contact_nodes=support["nodes"],
                      cell_damage=cell_damage, piece_of_cell=piece_of_cell, pieces=pieces,
                      min_h_over_l=float(mesh.h / np.max(ell)))


def split_pieces(stone: Stone, mesh: fem2d.Mesh2D, d: np.ndarray, length_m):
    """(cell damage, piece index per cell, pieces heaviest first); see module
    docstring. ``length_m`` is l per element. Every filled cell belongs to
    exactly one piece."""
    filled = stone.cells > 0
    cell_damage = np.zeros(stone.cells.shape)
    ell = np.zeros(stone.cells.shape)
    rows, cols = mesh.cell_index[:, 0], mesh.cell_index[:, 1]
    cell_damage[rows, cols] = np.asarray(d)[mesh.elements].max(axis=1)
    ell[rows, cols] = np.broadcast_to(np.asarray(length_m, dtype=float), rows.shape)
    crack = filled & (cell_damage >= D_BROKEN)
    near = ndimage.distance_transform_edt(~crack) * stone.cell_size_m <= ell if crack.any() else crack
    intact = filled & ~crack & ~(near & (cell_damage >= D_PROCESS))
    if not intact.any():
        return cell_damage, np.where(filled, 0, -1), [stone.extract(filled)]
    labels, count = ndimage.label(intact, structure=ndimage.generate_binary_structure(2, 1))
    _, nearest = ndimage.distance_transform_edt(~intact, return_indices=True)
    owner = labels[nearest[0], nearest[1]]
    owner = np.where(filled, owner, 0)
    pieces = [stone.extract(owner == k) for k in range(1, count + 1)]
    order = sorted(range(count), key=lambda k: (-pieces[k].mass_kg, k))
    remap = np.full(count + 1, -1)
    remap[[k + 1 for k in order]] = np.arange(count)
    return cell_damage, remap[owner], [pieces[k] for k in order]
