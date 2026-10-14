"""Phase-field model of brittle fracture (AT1) on ``fem2d`` meshes.

The damage d (0 intact, 1 broken) is a nodal field with the same bilinear
shape functions as the displacement. The total energy is (Bourdin, Francfort &
Marigo 2000, J. Mech. Phys. Solids 48:797; AT1 form of Pham, Amor, Marigo &
Maurini 2011, Int. J. Damage Mech. 20:618):

    E(u, d) = int g(d) psi+(eps) + psi-(eps) dV
              + 3 G_c / 8 * int ( d / l + l |grad d|^2 ) dV

with g(d) = (1 - k)(1 - d)^2 + k, k = ``RESIDUAL_STIFFNESS`` (numerical, keeps
the stiffness matrix regular). With the AT1 dissipation the material stays
undamaged (purely elastic) until a 1D bar reaches the stress

    sigma_c = sqrt(3 G_c E / (8 l))      (Tanne, Li, Bourdin, Marigo & Maurini
                                           2018, J. Mech. Phys. Solids 110:80)

(in the limit k -> 0; with k the threshold driving force carries a factor
1/(1 - k), a relative change of 1e-6), so the length l is fixed by the
material, not chosen: ``regularization_length`` returns
l = 3 G_c E / (8 sigma_t^2) with sigma_t the tensile strength and
G_c = K_IC^2 / E', E' = E/(1 - nu^2) in plane strain, axisymmetric and 3D,
E' = E in plane stress (``material_constants``).

Energy split psi = psi+ + psi- (only psi+ drives damage, so compression does
not break the material):
- ``"spectral"``: Miehe, Hofacker & Welschinger 2010, Comput. Methods Appl.
  Mech. Eng. 199:2765, psi+ = lam/2 <tr e>+^2 + mu sum <e_i>+^2.
- ``"voldev"``: Amor, Marigo & Maurini 2009, J. Mech. Phys. Solids 57:1209,
  psi+ = K/2 <tr e>+^2 + mu e_dev:e_dev.
- ``"none"``: psi+ = psi (no split).
The out-of-plane strain is 0 in plane strain, the hoop strain in
axisymmetric, and -nu/(1-nu)(e_xx + e_yy) in plane stress (sigma_zz = 0).
The displacement problem uses the "hybrid" isotropic degradation g(d) of the
whole stress (Ambati, Gerasimov & De Lorenzis 2015, Comput. Mech. 55:383), so
each displacement solve stays linear and reuses ``fem2d.solve``. With a split
this is NOT a minimisation of E(u, d) above: the u-step minimises
int g(d) psi dV instead, so the scheme is the non-variational hybrid model
of Ambati et al. (for split ``"none"`` both coincide).

Solution by staggered iteration (alternate minimisation of Bourdin et al.
2000 for split ``"none"``): solve u with d fixed, then d with u fixed as the
bound-constrained quadratic problem
d_prev <= d <= 1 (irreversibility), repeat until d stops changing. The bound
problem is solved by a primal-dual active set method (Hintermueller, Ito &
Kunisch 2002, SIAM J. Optim. 13:865).
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from . import fem2d
from .materials import Material

SPLITS = ("spectral", "voldev", "none")
RESIDUAL_STIFFNESS = 1e-6  # numerical, not a material property
C_W = 8.0 / 3.0  # AT1 normalisation c_w = 4 int_0^1 sqrt(w(d)) dd with w(d) = d


def regularization_length(g_c: float, youngs_pa: float, tensile_strength_pa: float) -> float:
    """AT1 length l = 3 G_c E / (8 sigma_t^2) (Tanne et al. 2018, eq. for the
    1D critical stress sigma_c = sqrt(3 G_c E / (8 l)))."""
    if g_c <= 0 or youngs_pa <= 0 or tensile_strength_pa <= 0:
        raise ValueError("G_c, E and sigma_t must be positive")
    return 3.0 * g_c * youngs_pa / (8.0 * tensile_strength_pa ** 2)


def material_constants(material: Material, mode: str) -> tuple[float, float]:
    """(G_c, l) of a material for a ``fem2d`` mode: G_c = K_IC^2 / E' with
    E' = E in plane stress and E / (1 - nu^2) otherwise (Irwin; Anderson 2017,
    Fracture Mechanics, ch. 2), and l from ``regularization_length``."""
    fem2d._check_mode(mode)
    E = material.youngs_modulus_pa
    e_prime = E if mode == "plane_stress" else E / (1.0 - material.poisson_ratio ** 2)
    g_c = material.fracture_toughness_pa_sqrt_m ** 2 / e_prime
    return g_c, regularization_length(g_c, E, material.tensile_strength_pa)


def degradation(d: np.ndarray) -> np.ndarray:
    d = np.asarray(d, dtype=float)
    return (1.0 - RESIDUAL_STIFFNESS) * (1.0 - d) ** 2 + RESIDUAL_STIFFNESS


def _shape_values(xi: float, eta: float) -> np.ndarray:
    return (1 + fem2d._XI * xi) * (1 + fem2d._ETA * eta) / 4.0


def at_gauss_points(mesh: fem2d.Mesh2D, d: np.ndarray) -> np.ndarray:
    """Nodal field interpolated to the Gauss points, shape (n_el, 4)."""
    de = np.asarray(d, dtype=float)[mesh.elements]
    return np.stack([de @ _shape_values(xi, eta) for xi, eta in fem2d.GAUSS_POINTS], axis=1)


def _lame(mesh: fem2d.Mesh2D):
    E, nu = mesh.youngs_pa, mesh.poisson
    return E * nu / ((1 + nu) * (1 - 2 * nu)), E / (2 * (1 + nu))


def _strain_3d(B: np.ndarray, ue: np.ndarray, mode: str, nu: np.ndarray):
    """Normal strains (e1, e2, e3) in the mesh axes plus the in-plane
    engineering shear g12. e3 is out of plane: 0 in plane strain, the hoop
    strain in axisymmetric, -nu/(1-nu)(e1 + e2) in plane stress."""
    e = np.einsum("eki,ei->ek", B, ue)
    if mode == "axisymmetric":
        return e[:, 0], e[:, 1], e[:, 2], e[:, 3]
    e3 = -nu / (1.0 - nu) * (e[:, 0] + e[:, 1]) if mode == "plane_stress" else np.zeros(len(e))
    return e[:, 0], e[:, 1], e3, e[:, 2]


def energy_split(mesh: fem2d.Mesh2D, mode: str, u: np.ndarray, split: str = "spectral"):
    """(psi+, psi-) in J/m^3 at the Gauss points, each (n_el, 4)."""
    fem2d._check_mode(mode)
    if split not in SPLITS:
        raise ValueError(f"split must be one of {SPLITS}")
    ue = np.asarray(u, dtype=float)[fem2d._element_dofs(mesh)]
    lam, mu = _lame(mesh)
    D = fem2d.constitutive(mesh.youngs_pa, mesh.poisson, mode)
    pos = np.zeros((len(mesh.elements), 4))
    neg = np.zeros_like(pos)
    for g, (xi, eta) in enumerate(fem2d.GAUSS_POINTS):
        B, _ = fem2d._b_matrices(mesh, mode, xi, eta)
        if split == "none":
            strain = np.einsum("eki,ei->ek", B, ue)
            pos[:, g] = 0.5 * np.einsum("ek,ekl,el->e", strain, D, strain)
            continue
        e1, e2, e3, g12 = _strain_3d(B, ue, mode, mesh.poisson)
        tr = e1 + e2 + e3
        if split == "spectral":
            mean, rad = 0.5 * (e1 + e2), np.sqrt((0.5 * (e1 - e2)) ** 2 + (0.5 * g12) ** 2)
            principal = (mean + rad, mean - rad, e3)
            pos[:, g] = 0.5 * lam * np.maximum(tr, 0) ** 2 + mu * sum(np.maximum(p, 0) ** 2 for p in principal)
            neg[:, g] = 0.5 * lam * np.minimum(tr, 0) ** 2 + mu * sum(np.minimum(p, 0) ** 2 for p in principal)
        else:
            K = lam + 2.0 * mu / 3.0
            dev = sum((e - tr / 3.0) ** 2 for e in (e1, e2, e3)) + 0.5 * g12 ** 2
            pos[:, g] = 0.5 * K * np.maximum(tr, 0) ** 2 + mu * dev
            neg[:, g] = 0.5 * K * np.minimum(tr, 0) ** 2
    return pos, neg


def _per_element(value, n: int) -> np.ndarray:
    return np.broadcast_to(np.asarray(value, dtype=float), (n,))


def damage_system(mesh: fem2d.Mesh2D, mode: str, psi_plus: np.ndarray, g_c, length_m):
    """Matrix A and vector b of the damage energy 1/2 d.A.d - b.d (+ const)
    for fixed psi+ (n_el, 4). ``g_c`` and ``length_m`` are scalars or one
    value per element."""
    ne = len(mesh.elements)
    gc, ell = _per_element(g_c, ne), _per_element(length_m, ne)
    if np.any(gc <= 0) or np.any(ell <= 0):
        raise ValueError("G_c and l must be positive")
    k = 1.0 - RESIDUAL_STIFFNESS
    Ae = np.zeros((ne, 4, 4))
    be = np.zeros((ne, 4))
    for g, (xi, eta) in enumerate(fem2d.GAUSS_POINTS):
        B, w = fem2d._b_matrices(mesh, mode, xi, eta)
        N = _shape_values(xi, eta)
        dNdx, dNdy = B[:, 0, 0::2], B[:, 1, 1::2]
        grad = np.einsum("ei,ej->eij", dNdx, dNdx) + np.einsum("ei,ej->eij", dNdy, dNdy)
        coef = 2.0 * k * psi_plus[:, g]
        Ae += (coef[:, None, None] * np.outer(N, N)[None]
               + (2.0 * gc * ell / C_W)[:, None, None] * grad) * w[:, None, None]
        be += ((coef - gc / (C_W * ell))[:, None] * N[None, :]) * w[:, None]
    e = mesh.elements
    rows = np.repeat(e, 4, axis=1).ravel()
    cols = np.tile(e, (1, 4)).ravel()
    n = len(mesh.nodes)
    A = sp.coo_matrix((Ae.ravel(), (rows, cols)), shape=(n, n)).tocsr()
    b = np.zeros(n)
    np.add.at(b, e.ravel(), be.ravel())
    return A, b


@dataclass(frozen=True)
class BoundSolve:
    d: np.ndarray
    iterations: int
    converged: bool


def solve_bounded(A: sp.csr_matrix, b: np.ndarray, lower: np.ndarray, upper: np.ndarray,
                  x0: np.ndarray | None = None, max_iter: int = 100) -> BoundSolve:
    """min 1/2 x.A.x - b.x subject to lower <= x <= upper (A symmetric
    positive definite), primal-dual active set (Hintermueller et al. 2002).
    Stops when the active sets repeat; the result satisfies the bounds exactly."""
    lower = np.asarray(lower, dtype=float)
    upper = np.asarray(upper, dtype=float)
    if np.any(lower > upper):
        raise ValueError("lower bound above upper bound")
    x = np.clip(lower if x0 is None else np.asarray(x0, dtype=float), lower, upper)
    c = float(A.diagonal().mean())
    prev = None
    A = A.tocsr()
    for it in range(1, max_iter + 1):
        lam = A @ x - b  # gradient: >= 0 at the lower bound, <= 0 at the upper
        at_low = lam + c * (lower - x) > 0
        at_up = (lam + c * (upper - x) < 0) & ~at_low
        key = (at_low.tobytes(), at_up.tobytes())
        if key == prev:
            return BoundSolve(x, it - 1, True)
        prev = key
        x = np.where(at_low, lower, np.where(at_up, upper, x))
        free = ~(at_low | at_up)
        if free.any():
            fixed = ~free
            rhs = b[free] - A[free][:, fixed] @ x[fixed]
            x[free] = spla.spsolve(A[free][:, free].tocsc(), rhs)
    return BoundSolve(np.clip(x, lower, upper), max_iter, False)


def solve_damage(mesh: fem2d.Mesh2D, mode: str, psi_plus: np.ndarray, g_c, length_m,
                 lower: np.ndarray, x0: np.ndarray | None = None) -> BoundSolve:
    A, b = damage_system(mesh, mode, psi_plus, g_c, length_m)
    return solve_bounded(A, b, lower, np.ones(len(mesh.nodes)), x0)


def fracture_energy(mesh: fem2d.Mesh2D, mode: str, d: np.ndarray, g_c, length_m) -> float:
    """3 G_c / 8 int (d / l + l |grad d|^2) dV in J. Planar modes include
    ``mesh.thickness_m``; axisymmetric integrates over the full revolution."""
    ne = len(mesh.elements)
    gc, ell = _per_element(g_c, ne), _per_element(length_m, ne)
    de = np.asarray(d, dtype=float)[mesh.elements]
    total = 0.0
    for xi, eta in fem2d.GAUSS_POINTS:
        B, w = fem2d._b_matrices(mesh, mode, xi, eta)
        dval = de @ _shape_values(xi, eta)
        gx, gy = (B[:, 0, 0::2] * de).sum(1), (B[:, 1, 1::2] * de).sum(1)
        total += float(np.sum(gc / C_W * (dval / ell + ell * (gx ** 2 + gy ** 2)) * w))
    return total


def elastic_energy(mesh: fem2d.Mesh2D, mode: str, u: np.ndarray, d: np.ndarray,
                   split: str = "spectral") -> float:
    """int g(d) psi+ + psi- dV in J (same weights as ``fracture_energy``).
    This is the energy the damage step sees; the hybrid u-step uses
    int g(d) psi dV instead (see module docstring)."""
    pos, neg = energy_split(mesh, mode, u, split)
    gq = degradation(at_gauss_points(mesh, d))
    total = 0.0
    for g, (xi, eta) in enumerate(fem2d.GAUSS_POINTS):
        _, w = fem2d._b_matrices(mesh, mode, xi, eta)
        total += float(np.sum((gq[:, g] * pos[:, g] + neg[:, g]) * w))
    return total


@dataclass(frozen=True)
class StepResult:
    u: np.ndarray
    d: np.ndarray
    iterations: int
    converged: bool
    max_change: float
    inner_converged: bool  # every bound-constrained damage solve converged


def staggered_step(
    mesh: fem2d.Mesh2D,
    mode: str,
    d_prev: np.ndarray,
    g_c,
    length_m,
    fixed_dofs: np.ndarray,
    fixed_values: np.ndarray | float = 0.0,
    forces: np.ndarray | None = None,
    split: str = "spectral",
    tol: float = 1e-3,
    max_iter: int = 300,
) -> StepResult:
    """One load step: alternate u and d solves with d >= ``d_prev``, until the
    largest nodal change of d is below ``tol``. Returns u solved with the
    final d. ``converged`` needs both that and converged damage solves. Note: hybrid degradation also softens compressed broken
    material (Ambati et al. 2015); crack faces are not prevented from
    overlapping in the displacement solve."""
    d_prev = np.asarray(d_prev, dtype=float)
    if d_prev.shape != (len(mesh.nodes),) or np.any(d_prev < 0) or np.any(d_prev > 1):
        raise ValueError("d_prev must be a nodal field in [0, 1]")
    d = d_prev.copy()
    change = math.inf
    inner_ok = True
    it = 0
    while it < max_iter:
        it += 1
        u = fem2d.solve(mesh, mode, fixed_dofs, fixed_values, forces,
                        stiffness_scale=degradation(at_gauss_points(mesh, d)))
        pos, _ = energy_split(mesh, mode, u, split)
        res = solve_damage(mesh, mode, pos, g_c, length_m, d_prev, d)
        inner_ok = inner_ok and res.converged
        change = float(np.max(np.abs(res.d - d)))
        d = res.d
        if change < tol:
            break
    u = fem2d.solve(mesh, mode, fixed_dofs, fixed_values, forces,
                    stiffness_scale=degradation(at_gauss_points(mesh, d)))
    return StepResult(u, d, it, change < tol and inner_ok, change, inner_ok)
