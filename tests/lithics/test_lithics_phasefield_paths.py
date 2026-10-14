"""Phase-field fracture, step 3 part b: crack paths are not tied to the grid.
A centre crack in a square plate (side 30 l, uniform h = l / 4) is loaded by
boundary displacements of a homogeneous uniaxial stress state. Load
magnitudes are chosen above the infinite-plate Griffith load so the crack
runs in one step; the direction of growth is measured, not prescribed."""
import math

import numpy as np

from lithics import contact
from lithics import phasefield as pf
from lithics.materials import load_material

GLASS = load_material("glass_soda_lime")
E, NU = GLASS.youngs_modulus_pa, GLASS.poisson_ratio
GC, ELL = pf.material_constants(GLASS, "plane_strain")
KIC = GLASS.fracture_toughness_pa_sqrt_m
HALF_CRACK = 4 * ELL


def _grow(crack_deg: float, load_deg: float, stress_pa: float, max_iter: int):
    h = ELL / 4
    n = 120
    g = (np.arange(n + 1) - n / 2) * h
    m = contact.tensor_mesh(g, g, E, NU)
    X, Y = m.nodes[:, 0], m.nodes[:, 1]
    t = math.radians(crack_deg)
    s = X * math.cos(t) + Y * math.sin(t)
    q = -X * math.sin(t) + Y * math.cos(t)
    dist = np.hypot(s - np.clip(s, -HALF_CRACK, HALF_CRACK), q)
    # starter crack: broken band |q| <= h, then the AT1 profile (1 - x / 2l)^2
    d0 = np.where(dist <= h, 1.0, np.clip(1 - (dist - h) / (2 * ELL), 0, 1) ** 2)
    p = math.radians(load_deg)
    sig = stress_pa * np.outer([math.cos(p), math.sin(p)], [math.cos(p), math.sin(p)])
    eps = (1 + NU) / E * sig - NU * (1 + NU) / E * np.trace(sig) * np.eye(2)  # plane strain
    bnd = np.nonzero((np.abs(X) > g[-1] - 1e-12) | (np.abs(Y) > g[-1] - 1e-12))[0]
    ub = m.nodes[bnd] @ eps.T
    fixed = np.concatenate([2 * bnd, 2 * bnd + 1])
    r = pf.staggered_step(m, "plane_strain", d0, GC, ELL, fixed,
                          np.concatenate([ub[:, 0], ub[:, 1]]), max_iter=max_iter)
    grown = (r.d > 0.9) & (dist > 3 * ELL)
    branches = []
    for side in (1, -1):
        P = m.nodes[grown & (side * s > 0)]
        assert len(P) >= 20, "crack did not grow"
        c = P - P.mean(axis=0)
        axis = np.linalg.eigh(c.T @ c)[1][:, -1]
        angle = math.degrees(math.atan2(axis[1], axis[0])) % 180.0  # whole branch (PCA)
        tip = side * HALF_CRACK * np.array([math.cos(t), math.sin(t)])
        r_tip = np.hypot(P[:, 0] - tip[0], P[:, 1] - tip[1])
        chord = P[(r_tip > ELL) & (r_tip < 5 * ELL)].mean(axis=0) - tip
        near_tip = math.degrees(math.atan2(chord[1], chord[0])) % 180.0  # first 1-5 l
        reach = np.hypot(P[:, 0], P[:, 1]).max()
        branches.append((angle, near_tip, reach))
    return r, branches


def _angle_gap(a: float, b: float) -> float:
    return abs((a - b + 90.0) % 180.0 - 90.0)


def test_mode_i_crack_off_grid_runs_along_its_own_line():
    """Crack at 30 deg to the grid, tension normal to it (pure mode I in an
    infinite plate): the crack must keep its own 30 deg line, not turn to a
    grid axis (0 or 90 deg) or the diagonal (45 deg)."""
    stress = 1.3 * KIC / math.sqrt(math.pi * HALF_CRACK)
    r, branches = _grow(30.0, 120.0, stress, max_iter=150)
    assert r.max_change < 1e-3  # the outer staggered loop has settled
    for angle, near_tip, reach in branches:
        assert _angle_gap(angle, 30.0) < 3.0
        assert _angle_gap(near_tip, 30.0) < 3.0
        assert reach > HALF_CRACK + 6 * ELL


def mts_kink_deg(beta_deg: float) -> float:
    """Kink angle of the maximum tangential stress criterion (Erdogan & Sih
    1963) for a crack at beta to the tension axis in an infinite plate:
    K_I ~ sin^2 beta, K_II ~ sin beta cos beta,
    theta_0 = 2 atan[(1 - sqrt(1 + 8 r^2)) / (4 r)], r = K_II / K_I."""
    b = math.radians(beta_deg)
    r = math.cos(b) / math.sin(b)
    return math.degrees(2 * math.atan((1 - math.sqrt(1 + 8 * r * r)) / (4 * r)))


def test_inclined_crack_turns_normal_to_tension():
    """Crack at 45 deg, tension along y (mixed mode, K_II = K_I). MTS kinks
    the crack to 45 - 53.1 = -8.1 deg, and further growth tends to 0 deg
    (normal to the tension). The first 1-5 l of each branch must be within
    4 deg of the MTS kink, and the whole branch between the kink and 0 deg
    (5 deg margin). MTS is an infinite-plate, sharp-crack result; the plate
    here is finite with clamped edges and a diffuse starter crack, so the
    4 deg margin covers that, it is not a measured error bar."""
    kink = 45.0 + mts_kink_deg(45.0)
    assert math.isclose(kink, -8.13, abs_tol=0.01)
    stress = 1.6 * KIC / math.sqrt(math.pi * HALF_CRACK)
    r, branches = _grow(45.0, 90.0, stress, max_iter=60)
    assert r.converged
    for angle, near_tip, reach in branches:
        signed = (angle + 90.0) % 180.0 - 90.0
        assert kink - 5.0 < signed < 5.0
        assert _angle_gap(near_tip, kink) < 4.0
        assert reach > HALF_CRACK + 6 * ELL
