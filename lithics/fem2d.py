"""Linear elastic finite elements on the cell grid of a 2D ``Stone``.

Every filled cell is one bilinear quadrilateral (Q4) element with 2x2 Gauss
integration (standard isoparametric formulation, e.g. Hughes 1987, *The Finite
Element Method*, ch. 3; Zienkiewicz & Taylor 2000, vol. 1, ch. 4 for the
axisymmetric case). Three modes:

- ``plane_strain``: out-of-plane strain is zero; weight = ``stone.thickness_m``.
- ``plane_stress``: out-of-plane stress is zero; weight = ``stone.thickness_m``.
- ``axisymmetric``: x is the radius r (>= 0), y is the axis z; integrals are
  over the full revolution (weight 2*pi*r), so forces are total ring forces.
  Nodes on the axis get u_r = 0 automatically.

DOF ``2*n`` is the x (or r) displacement of node ``n``, ``2*n + 1`` the y (or z)
displacement. Stresses are returned per element at the element centre as
columns (s_xx, s_yy, s_zz, s_xy); s_zz is the out-of-plane (hoop in
axisymmetric) stress. ``stiffness_scale`` multiplies the stiffness, either one
value per element (n_el,) or one per Gauss point (n_el, 4) in the order of
``GAUSS_POINTS`` (used by ``lithics.phasefield`` to degrade broken material).
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from .stone import Stone

MODES = ("plane_strain", "plane_stress", "axisymmetric")

_G = 1.0 / math.sqrt(3.0)
_GAUSS = ((-_G, -_G), (_G, -_G), (_G, _G), (-_G, _G))  # weights all 1
GAUSS_POINTS = _GAUSS
_XI = np.array([-1.0, 1.0, 1.0, -1.0])  # node natural coords, counter-clockwise
_ETA = np.array([-1.0, -1.0, 1.0, 1.0])


@dataclass(frozen=True)
class Mesh2D:
    nodes: np.ndarray  # (n_nodes, 2) coordinates in m
    elements: np.ndarray  # (n_el, 4) node ids, counter-clockwise
    cell_index: np.ndarray | None  # (n_el, 2) (row, col) in stone.cells; None for quad meshes
    youngs_pa: np.ndarray  # (n_el,)
    poisson: np.ndarray  # (n_el,)
    h: float  # cell size, or a typical element size for quad meshes
    thickness_m: float

    @property
    def n_dof(self) -> int:
        return 2 * len(self.nodes)


def quad_mesh(nodes: np.ndarray, elements: np.ndarray, youngs_pa, poisson,
              thickness_m: float = 1.0) -> Mesh2D:
    """Mesh of arbitrary convex quads (used to check the element formulation
    on body-fitted geometry, independent of the cell grid)."""
    nodes = np.asarray(nodes, dtype=float)
    elements = np.asarray(elements, dtype=np.int64)
    ne = len(elements)
    edge = np.linalg.norm(nodes[elements[:, 1]] - nodes[elements[:, 0]], axis=1)
    return Mesh2D(nodes=nodes, elements=elements, cell_index=None,
                  youngs_pa=np.broadcast_to(np.asarray(youngs_pa, dtype=float), (ne,)).copy(),
                  poisson=np.broadcast_to(np.asarray(poisson, dtype=float), (ne,)).copy(),
                  h=float(np.median(edge)), thickness_m=float(thickness_m))


def build_mesh(stone: Stone) -> Mesh2D:
    if stone.dim != 2:
        raise ValueError("fem2d needs a 2D stone")
    cells = stone.cells
    rows, cols = np.nonzero(cells > 0)
    if rows.size == 0:
        raise ValueError("stone has no filled cells")
    ny, nx = cells.shape
    stride = nx + 1
    grid_ids = np.stack(
        [rows * stride + cols, rows * stride + cols + 1,
         (rows + 1) * stride + cols + 1, (rows + 1) * stride + cols], axis=1)
    used, compact = np.unique(grid_ids, return_inverse=True)
    elements = compact.reshape(grid_ids.shape)
    h = stone.cell_size_m
    nodes = np.stack([(used % stride) * h, (used // stride) * h], axis=1) + stone.origin_m[:2]
    ph = cells[rows, cols] - 1
    E = np.array([p.youngs_modulus_pa for p in stone.phases])[ph]
    nu = np.array([p.poisson_ratio for p in stone.phases])[ph]
    return Mesh2D(nodes=nodes, elements=elements, cell_index=np.stack([rows, cols], axis=1),
                  youngs_pa=E, poisson=nu, h=h, thickness_m=stone.thickness_m)


def _check_mode(mode: str) -> None:
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")


def constitutive(E: np.ndarray, nu: np.ndarray, mode: str) -> np.ndarray:
    """Isotropic elasticity matrices, shape (n, 3, 3) or (n, 4, 4) for
    axisymmetric with strain order (e_r, e_z, e_theta, g_rz)."""
    _check_mode(mode)
    E = np.asarray(E, dtype=float)
    nu = np.asarray(nu, dtype=float)
    n = E.size
    if mode == "plane_stress":
        c = E / (1.0 - nu ** 2)
        D = np.zeros((n, 3, 3))
        D[:, 0, 0] = D[:, 1, 1] = c
        D[:, 0, 1] = D[:, 1, 0] = c * nu
        D[:, 2, 2] = c * (1.0 - nu) / 2.0
        return D
    c = E / ((1.0 + nu) * (1.0 - 2.0 * nu))
    k = 3 if mode == "plane_strain" else 4
    D = np.zeros((n, k, k))
    normal = 2 if mode == "plane_strain" else 3
    for a in range(normal):
        for b in range(normal):
            D[:, a, b] = c * (1.0 - nu) if a == b else c * nu
    D[:, k - 1, k - 1] = c * (1.0 - 2.0 * nu) / 2.0
    return D


def _b_matrices(mesh: Mesh2D, mode: str, xi: float, eta: float):
    """Strain-displacement matrices at one natural point for all elements,
    plus the integration weight (|J| * thickness or |J| * 2*pi*r).
    General isoparametric map, so any convex quad works (cells are squares)."""
    N = (1 + _XI * xi) * (1 + _ETA * eta) / 4.0
    dN_dxi = _XI * (1 + _ETA * eta) / 4.0
    dN_deta = _ETA * (1 + _XI * xi) / 4.0
    X = mesh.nodes[mesh.elements]  # (ne, 4, 2)
    j11, j12 = X[:, :, 0] @ dN_dxi, X[:, :, 1] @ dN_dxi  # dx/dxi, dy/dxi
    j21, j22 = X[:, :, 0] @ dN_deta, X[:, :, 1] @ dN_deta
    detj = j11 * j22 - j12 * j21
    if np.any(detj <= 0):
        raise ValueError("element with non-positive Jacobian (node order must be counter-clockwise)")
    dNdx = (j22[:, None] * dN_dxi - j12[:, None] * dN_deta) / detj[:, None]
    dNdy = (-j21[:, None] * dN_dxi + j11[:, None] * dN_deta) / detj[:, None]
    ne = len(mesh.elements)
    k = 4 if mode == "axisymmetric" else 3
    B = np.zeros((ne, k, 8))
    B[:, 0, 0::2] = dNdx
    B[:, 1, 1::2] = dNdy
    B[:, k - 1, 0::2] = dNdy
    B[:, k - 1, 1::2] = dNdx
    if mode == "axisymmetric":
        r = X[:, :, 0] @ N  # (ne,)
        if np.any(r <= 0):
            raise ValueError("axisymmetric quadrature point at r <= 0 (mesh must lie in r >= 0)")
        B[:, 2, 0::2] = N[None, :] / r[:, None]
        w = detj * 2.0 * math.pi * r
    else:
        w = detj * mesh.thickness_m
    return B, w


def _element_dofs(mesh: Mesh2D) -> np.ndarray:
    e = mesh.elements
    return np.stack([2 * e, 2 * e + 1], axis=2).reshape(len(e), 8)


def _gauss_scale(mesh: Mesh2D, stiffness_scale) -> np.ndarray:
    """Stiffness multiplier as (n_el, 4): per-element values are repeated."""
    ne = len(mesh.elements)
    if stiffness_scale is None:
        return np.ones((ne, 4))
    s = np.asarray(stiffness_scale, dtype=float)
    if s.shape == (ne,):
        return np.repeat(s[:, None], 4, axis=1)
    if s.shape == (ne, 4):
        return s
    raise ValueError("stiffness_scale must have shape (n_el,) or (n_el, 4)")


def assemble(mesh: Mesh2D, mode: str, stiffness_scale: np.ndarray | None = None) -> sp.csr_matrix:
    _check_mode(mode)
    if mode == "axisymmetric" and mesh.nodes[:, 0].min() < -1e-12 * mesh.h:
        raise ValueError("axisymmetric mesh must have x = r >= 0")
    D = constitutive(mesh.youngs_pa, mesh.poisson, mode)
    scale = _gauss_scale(mesh, stiffness_scale)
    Ke = np.zeros((len(mesh.elements), 8, 8))
    for g, (xi, eta) in enumerate(_GAUSS):
        B, w = _b_matrices(mesh, mode, xi, eta)
        Ke += np.einsum("eki,ekl,elj->eij", B, D, B) * (w * scale[:, g])[:, None, None]
    dofs = _element_dofs(mesh)
    rows = np.repeat(dofs, 8, axis=1).ravel()
    cols = np.tile(dofs, (1, 8)).ravel()
    K = sp.coo_matrix((Ke.ravel(), (rows, cols)), shape=(mesh.n_dof, mesh.n_dof)).tocsr()
    return K


def solve(
    mesh: Mesh2D,
    mode: str,
    fixed_dofs: np.ndarray,
    fixed_values: np.ndarray | float = 0.0,
    forces: np.ndarray | None = None,
    stiffness_scale: np.ndarray | None = None,
) -> np.ndarray:
    """Displacements (n_dof,) for prescribed DOFs and nodal forces (N)."""
    K = assemble(mesh, mode, stiffness_scale)
    n = mesh.n_dof
    fixed_dofs = np.asarray(fixed_dofs, dtype=np.int64).ravel()
    vals = np.broadcast_to(np.asarray(fixed_values, dtype=float), fixed_dofs.shape)
    u = np.zeros(n)
    u[fixed_dofs] = vals
    is_fixed = np.zeros(n, dtype=bool)
    is_fixed[fixed_dofs] = True
    if mode == "axisymmetric":
        on_axis = np.abs(mesh.nodes[:, 0]) <= 1e-9 * mesh.h
        axis_dofs = 2 * np.nonzero(on_axis)[0]
        if np.any(u[axis_dofs[is_fixed[axis_dofs]]] != 0.0):
            raise ValueError("u_r on the axis must be 0 in axisymmetric mode")
        is_fixed[axis_dofs] = True
    f = np.zeros(n) if forces is None else np.asarray(forces, dtype=float).copy()
    free = np.nonzero(~is_fixed)[0]
    rhs = f[free] - K[free][:, is_fixed] @ u[is_fixed]
    u[free] = spla.spsolve(K[free][:, free].tocsc(), rhs)
    return u


def element_stress(mesh: Mesh2D, mode: str, u: np.ndarray,
                   stiffness_scale: np.ndarray | None = None) -> np.ndarray:
    """Stress per element, columns (s_xx, s_yy, s_zz, s_xy) in Pa: at the
    element centre, or, when ``stiffness_scale`` is given per Gauss point
    (n_el, 4), the mean of the four Gauss-point stresses (each with its own
    scale, as in ``assemble``)."""
    _check_mode(mode)
    D = constitutive(mesh.youngs_pa, mesh.poisson, mode)
    ue = u[_element_dofs(mesh)]
    s_arr = None if stiffness_scale is None else np.asarray(stiffness_scale, dtype=float)
    if s_arr is not None and s_arr.ndim == 2:
        scale = _gauss_scale(mesh, s_arr)
        s = 0.0
        for g, (xi, eta) in enumerate(_GAUSS):
            B, _ = _b_matrices(mesh, mode, xi, eta)
            s = s + scale[:, g, None] * np.einsum("ekl,el->ek", D, np.einsum("eki,ei->ek", B, ue)) / 4.0
    else:
        B, _ = _b_matrices(mesh, mode, 0.0, 0.0)
        if s_arr is not None:
            D = D * _gauss_scale(mesh, s_arr)[:, 0, None, None]
        s = np.einsum("ekl,el->ek", D, np.einsum("eki,ei->ek", B, ue))
    out = np.zeros((len(mesh.elements), 4))
    if mode == "axisymmetric":
        out[:, 0], out[:, 1], out[:, 2], out[:, 3] = s[:, 0], s[:, 1], s[:, 2], s[:, 3]
    else:
        out[:, 0], out[:, 1], out[:, 3] = s[:, 0], s[:, 1], s[:, 2]
        if mode == "plane_strain":
            out[:, 2] = mesh.poisson * (s[:, 0] + s[:, 1])
    return out


def j_integral(mesh: Mesh2D, mode: str, u: np.ndarray, tip_m, r_in_m: float, r_out_m: float) -> float:
    """J (energy release rate, J/m^2) of a straight crack lying along -x from
    ``tip_m``, by the equivalent domain integral (Shih, Moran & Nakamura 1986,
    Int. J. Fract. 30:79; Anderson 2005, *Fracture Mechanics*, 3rd ed., sec. 7.4):

        J = sum over Gauss points of (s_ij du_j/dx - W d_1i) dq/dx_i dA / t

    q = 1 within ``r_in_m`` of the tip, 0 beyond ``r_out_m``, linear in the
    distance between (nodal values, interpolated by the element shapes).
    Planar modes only, no crack-face tractions. Integrates over the elements
    given, so a half model (symmetry plane on the crack line) returns J/2."""
    _check_mode(mode)
    if mode == "axisymmetric":
        raise ValueError("j_integral is for planar modes")
    if not 0 < r_in_m < r_out_m:
        raise ValueError("need 0 < r_in < r_out")
    d = np.linalg.norm(mesh.nodes - np.asarray(tip_m, dtype=float)[None, :2], axis=1)
    q = np.clip((r_out_m - d) / (r_out_m - r_in_m), 0.0, 1.0)[mesh.elements]  # (ne, 4)
    sel = np.any(q > 0, axis=1) & np.any(q < 1, axis=1)
    D = constitutive(mesh.youngs_pa, mesh.poisson, mode)
    ue = u[_element_dofs(mesh)]
    J = 0.0
    for xi, eta in _GAUSS:
        B, w = _b_matrices(mesh, mode, xi, eta)
        dNdx, dNdy = B[:, 0, 0::2], B[:, 1, 1::2]
        strain = np.einsum("eki,ei->ek", B, ue)
        s = np.einsum("ekl,el->ek", D, strain)  # s_xx, s_yy, s_xy
        W = 0.5 * np.einsum("ek,ek->e", s, strain)
        dux_dx, duy_dx = (dNdx * ue[:, 0::2]).sum(1), (dNdx * ue[:, 1::2]).sum(1)
        dq_dx, dq_dy = (dNdx * q).sum(1), (dNdy * q).sum(1)
        integrand = ((s[:, 0] * dux_dx + s[:, 2] * duy_dx - W) * dq_dx
                     + (s[:, 2] * dux_dx + s[:, 1] * duy_dx) * dq_dy)
        J += float(np.sum((integrand * w)[sel]))
    return J / mesh.thickness_m


def boundary_edges(mesh: Mesh2D) -> tuple[np.ndarray, np.ndarray]:
    """Edges used by exactly one element: (n_edges, 2) node pairs ordered
    counter-clockwise around the solid, and (n_edges, 2) outward unit normals."""
    e = mesh.elements
    edges = np.concatenate([e[:, [0, 1]], e[:, [1, 2]], e[:, [2, 3]], e[:, [3, 0]]])
    key = np.sort(edges, axis=1)
    _, inv, counts = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    edges = edges[counts[inv.ravel()] == 1]
    t = mesh.nodes[edges[:, 1]] - mesh.nodes[edges[:, 0]]
    normal = np.stack([t[:, 1], -t[:, 0]], axis=1) / np.linalg.norm(t, axis=1)[:, None]
    return edges, normal


def traction_forces(mesh: Mesh2D, mode: str, edges: np.ndarray, traction_pa) -> np.ndarray:
    """Consistent nodal forces for a traction on the given edges.

    ``traction_pa`` is a (2,) vector applied on every edge, or an (n_edges, 2)
    array. Linear edge shape functions, 2-point Gauss rule; weight is the
    thickness (planar) or 2*pi*r (axisymmetric)."""
    _check_mode(mode)
    edges = np.asarray(edges, dtype=np.int64).reshape(-1, 2)
    t = np.broadcast_to(np.asarray(traction_pa, dtype=float), (len(edges), 2))
    a, b = mesh.nodes[edges[:, 0]], mesh.nodes[edges[:, 1]]
    length = np.linalg.norm(b - a, axis=1)
    f = np.zeros(mesh.n_dof)
    for s in (0.5 - 0.5 * _G, 0.5 + 0.5 * _G):  # Gauss points on [0, 1], weights 1/2
        x = (1 - s) * a + s * b
        w = 0.5 * length * (2.0 * math.pi * x[:, 0] if mode == "axisymmetric" else mesh.thickness_m)
        for node, n_val in ((edges[:, 0], 1 - s), (edges[:, 1], s)):
            np.add.at(f, 2 * node, n_val * w * t[:, 0])
            np.add.at(f, 2 * node + 1, n_val * w * t[:, 1])
    return f
