"""Step 4 part (c): planar contact, strike of a 2D section, pieces (V10)."""
import math

import numpy as np
import pytest

from lithics import fem2d, impact
from lithics import indentation as ind
from lithics import phasefield as pf
from lithics import strike2d as s2
from lithics.materials import load_material
from lithics.stone import Stone, make_core, phases_of

GLASS = load_material("glass_soda_lime")
GRANITE = load_material("granite")
E_PRIME = GLASS.youngs_modulus_pa / (1 - GLASS.poisson_ratio ** 2)
GC, ELL = pf.material_constants(GLASS, "plane_strain")
THICK = 1e-3


def _block(h, nx, ny):
    return Stone(cells=np.ones((ny, nx), dtype=int), phases=phases_of(GLASS), cell_size_m=h,
                 material_name=GLASS.name, thickness_m=THICK)


# ---------------------------------------------------------------- contact

@pytest.fixture(scope="module", params=["hand", "anvil"])
def line_contact(request):
    h, R = 15e-6, 10e-3
    st = _block(h, 200, 100)  # 3 mm x 1.5 mm
    mesh = fem2d.build_mesh(st)
    K = fem2d.assemble(mesh, "plane_strain")
    masses = s2.lumped_masses(mesh, np.full(len(mesh.elements), GLASS.density_kg_m3))
    top = (1.5e-3, 1.5e-3)
    inds = [s2.make_indenter(mesh, top, (0.0, -1.0), R)]
    if request.param == "hand":
        mphi = s2.rigid_modes(mesh, masses, ("x", "y", "rot"))
    else:  # flat rigid anvil under the block
        inds.append(s2.make_indenter(mesh, top, (0.0, 1.0), 1e3, moves=False, reach_m=1e3))
        mphi = s2.rigid_modes(mesh, masses, ("t", "rot"), tangent=(1.0, 0.0))
    delta = 3e-6
    u, forces, act = s2.contact_solve(K, mphi, inds, delta, [np.zeros(len(i.nodes), bool) for i in inds],
                                      mesh.nodes, free_direction=None if request.param == "hand" else (0.0, -1.0))
    return request.param, h, R, delta, mesh, K, mphi, inds, u, forces, act


def test_gauged_saddle_matches_direct_sparse_solve():
    # the Schur solve on the pinned factor equals a direct solve of the
    # bordered system, for a free body (hand: x, y, rot) and a body held
    # along one axis (anvil: t, rot + one contact row)
    import scipy.sparse as sp
    import scipy.sparse.linalg as spla

    mesh = fem2d.build_mesh(_block(0.1e-3, 12, 7))
    K = fem2d.assemble(mesh, "plane_strain")
    masses = s2.lumped_masses(mesh, np.full(len(mesh.elements), GLASS.density_kg_m3))
    rng = np.random.default_rng(0)
    for kinds in (("x", "y", "rot"), ("t", "rot")):
        D = s2.rigid_modes(mesh, masses, kinds, tangent=(1.0, 0.0))
        if kinds[0] == "t":
            col = np.zeros((mesh.n_dof, 1))
            col[1] = 1.0
            D = np.hstack([D, col])
        D = D / np.linalg.norm(D, axis=0) * K.diagonal().mean()
        f = rng.standard_normal(mesh.n_dof)
        r = rng.standard_normal(D.shape[1]) * 1e-6 * K.diagonal().mean()
        A = sp.bmat([[K, sp.csc_matrix(D)], [sp.csc_matrix(D).T, None]], format="csc")
        want = spla.spsolve(A, np.concatenate([f, r]))
        u, y = s2._GaugedSaddle(K, mesh.nodes).solve(D, f, r)
        assert np.abs(u - want[:mesh.n_dof]).max() <= 1e-10 * np.abs(want[:mesh.n_dof]).max()
        assert np.abs(y - want[mesh.n_dof:]).max() <= 1e-10 * np.abs(want[mesh.n_dof:]).max()


def test_dual_contact_gives_the_same_active_sets(line_contact):
    # the cycle-safe fallback (exact dual by NNLS, Brent on the free
    # translation for the anvil) reproduces the converged active sets
    kind, _, _, delta, mesh, K, mphi, inds, _, _, act = line_contact
    B = mphi / np.linalg.norm(mphi, axis=0) * K.diagonal().mean()
    targets = [i.target0 + (delta if i.moves else 0.0) for i in inds]
    cand = [a | (np.abs(i.s) <= 0.3e-3) for i, a in zip(inds, act)]  # contact plus free nodes
    assert all(c.sum() > a.sum() for c, a in zip(cand, act))
    got = s2._dual_actives(s2._GaugedSaddle(K, mesh.nodes), B, None if kind == "hand" else (0.0, -1.0),
                           inds, targets, cand)
    for g, a in zip(got, act):
        assert np.array_equal(g, a)


class _AlwaysSeen:
    def __contains__(self, key):
        return True

    def add(self, key):
        pass


def test_contact_solve_dual_branch_ends_with_the_same_solution(line_contact, monkeypatch):
    # force the cycle branch from the first iteration: the candidates start
    # at the tip nodes only and must grow until no node penetrates
    kind, _, _, delta, mesh, K, mphi, inds, u, forces, act = line_contact
    monkeypatch.setattr(s2, "set", _AlwaysSeen, raising=False)
    u2, f2, a2 = s2.contact_solve(K, mphi, inds, delta, [np.zeros(len(i.nodes), bool) for i in inds],
                                  mesh.nodes, free_direction=None if kind == "hand" else (0.0, -1.0))
    for a, b in zip(act, a2):
        assert np.array_equal(a, b)
    assert np.abs(u2 - u).max() <= 1e-9 * np.abs(u).max()
    for f, g in zip(forces, f2):
        assert np.allclose(f, g, rtol=0, atol=1e-9 * f.sum())


def test_gauged_saddle_on_damaged_stiffness():
    # a band of nearly broken cells (g(d) ~ 1e-4) across the block: the
    # pinned factor with refinement still matches the direct solve
    import scipy.sparse as sp
    import scipy.sparse.linalg as spla

    mesh = fem2d.build_mesh(_block(0.1e-3, 12, 7))
    scale = np.ones(len(mesh.elements))
    scale[mesh.cell_index[:, 1] == 6] = pf.degradation(0.99)
    K = fem2d.assemble(mesh, "plane_strain", scale)
    masses = s2.lumped_masses(mesh, np.full(len(mesh.elements), GLASS.density_kg_m3))
    D = s2.rigid_modes(mesh, masses, ("x", "y", "rot"))
    D = D / np.linalg.norm(D, axis=0) * K.diagonal().mean()
    f = np.random.default_rng(1).standard_normal(mesh.n_dof)
    A = sp.bmat([[K, sp.csc_matrix(D)], [sp.csc_matrix(D).T, None]], format="csc")
    want = spla.spsolve(A, np.concatenate([f, np.zeros(3)]))
    u, _ = s2._GaugedSaddle(K, mesh.nodes).solve(D, f, np.zeros(3))
    assert np.abs(u - want[:mesh.n_dof]).max() <= 1e-8 * np.abs(want[:mesh.n_dof]).max()


def test_line_contact_width_and_pressure_match_hertz_2d(line_contact):
    # rigid cylinder on an elastic half-plane (Johnson 1985 sec. 4.3):
    # a^2 = 4 P' R / (pi E'), p(s) = p0 sqrt(1 - s^2/a^2), p0 = 2 P' / (pi a)
    _, h, R, _, _, _, _, inds, _, forces, act = line_contact
    p_line = forces[0].sum() / THICK
    a_th = math.sqrt(4 * p_line * R / (math.pi * E_PRIME))
    a_node = np.abs(inds[0].s[act[0]]).max()  # outermost node in contact
    assert a_node / h > 8.5  # contact resolved by 9 cells per side
    assert a_node <= a_th * (1 + 1e-9) and a_th <= a_node + h
    on = np.flatnonzero(act[0])
    centre = on[np.argmin(np.abs(inds[0].s[on]))]
    p_centre = forces[0][centre] / (h * THICK)
    assert p_centre == pytest.approx(2 * p_line / (math.pi * a_th), rel=0.03)
    assert np.all(forces[0] >= 0)


def test_line_contact_equilibrium_gauge_and_energy(line_contact):
    kind, _, _, delta, mesh, K, mphi, inds, u, forces, act = line_contact
    # no penetration anywhere, compressive forces only
    for i, (ind_, f, a) in enumerate(zip(inds, forces, act)):
        un = u[2 * ind_.nodes] * ind_.normal[0] + u[2 * ind_.nodes + 1] * ind_.normal[1]
        target = ind_.target0 + (delta if ind_.moves else 0.0)
        assert np.all(un >= target - 1e-9 * delta)
        assert np.all(f >= -1e-12 * np.abs(f).sum()) and np.all(f[~a] == 0)
        assert np.allclose(un[a], target[a], rtol=0, atol=1e-12 * delta)
    # gauge: mass-weighted rigid components of u vanish
    assert np.abs(mphi.T @ u).max() <= 1e-9 * np.abs(mphi).sum(axis=0).max() * np.abs(u).max()
    # 1/2 u.K.u = 1/2 sum lambda_i g_i (inertia forces do no work on u)
    work = sum(float(f @ (ind_.target0 + (delta if ind_.moves else 0.0))) for ind_, f in zip(inds, forces))
    assert 0.5 * float(u @ (K @ u)) == pytest.approx(0.5 * work, rel=1e-8)
    if kind == "anvil":  # normal equilibrium: anvil reaction = hammer force
        assert forces[1].sum() == pytest.approx(forces[0].sum(), rel=1e-9)
    # each indenter touches its own face: hammer the top (y = 1.5 mm) near
    # the strike line, anvil the bottom (y = 0)
    y = mesh.nodes[:, 1]
    hit = inds[0].nodes[act[0]]
    assert hit.size and np.allclose(y[hit], 1.5e-3) and np.abs(mesh.nodes[hit, 0] - 1.5e-3).max() < 0.2e-3
    if kind == "anvil":
        assert act[1].any() and np.allclose(y[inds[1].nodes[act[1]]], 0.0)


# ----------------------------------------------------------------- pieces

def _plate():
    return _block(ELL / 2, 40, 20)


def _split(st, node_d):
    mesh = fem2d.build_mesh(st)
    return mesh, s2.split_pieces(st, mesh, node_d(mesh.nodes / st.cell_size_m), ELL)


def _assert_partition(st, piece_of_cell, pieces):
    filled = st.cells > 0
    assert np.all((piece_of_cell >= 0) == filled)
    assert sum(p.n_cells for p in pieces) == st.n_cells
    assert sum(p.mass_kg for p in pieces) == pytest.approx(st.mass_kg, rel=1e-12)
    got = np.concatenate([p.cell_centers_m() for p in pieces])
    want = st.cell_centers_m()
    key = lambda c: c[np.lexsort((c[:, 1], c[:, 0]))]
    assert np.allclose(key(got), key(want), rtol=0, atol=1e-6 * st.cell_size_m)
    masses = [p.mass_kg for p in pieces]
    assert masses == sorted(masses, reverse=True)


def test_crack_through_gives_two_pieces_and_keeps_mass():
    st = _plate()
    _, (cd, owner, pieces) = _split(st, lambda ij: np.where(np.isclose(ij[:, 0], 25), 1.0, 0.0))
    assert len(pieces) == 2
    _assert_partition(st, owner, pieces)
    assert {p.n_cells for p in pieces} == {25 * 20, 15 * 20}  # crack cells go to the nearest side
    assert cd.max() == 1.0


def test_ligament_within_l_is_cut_but_diffuse_or_short_damage_is_not():
    st = _plate()
    # ridge d = 1 down to y = 2h (= l), partly damaged ligament (0.7) below
    lig = lambda ij: np.where(np.isclose(ij[:, 0], 25), np.where(ij[:, 1] >= 2, 1.0, 0.7), 0.0)
    _, (_, owner, pieces) = _split(st, lig)
    assert len(pieces) == 2
    _assert_partition(st, owner, pieces)
    # same ligament damage without any crack ridge: diffuse damage never cuts
    _, (_, _, pieces) = _split(st, lambda ij: np.where(np.isclose(ij[:, 0], 25), 0.7, 0.0))
    assert len(pieces) == 1
    # ridge stops 6h = 3l above the bottom with an intact ligament: one piece
    _, (_, _, pieces) = _split(st, lambda ij: np.where(np.isclose(ij[:, 0], 25) & (ij[:, 1] >= 6), 1.0, 0.0))
    assert len(pieces) == 1


# ----------------------------------------------------------------- strike

H_CORE = 60e-6  # = l / 2 for glass


@pytest.fixture(scope="module")
def core():
    return make_core(GLASS, height_m=33 * H_CORE, platform_m=42 * H_CORE, epa_deg=80.0,
                     cell_size_m=H_CORE, depth_m=2e-3)


def _strike(core, speed, support):
    ex, ey = core.meta["edge_m"]
    return impact.strike(core, (ex - 0.5e-3, ey), (0.0, -1.0), 0.05, speed, 5e-3, support)


@pytest.fixture(scope="module")
def split_runs(core):
    return _strike(core, 10.0, impact.hand_held()), _strike(core, 10.0, impact.hand_held())


def test_strike_splits_core_and_conserves_mass(core, split_runs):
    r = split_runs[0]
    assert r.converged
    assert len(r.pieces) >= 2
    _assert_partition(core, r.blow.piece_of_cell, r.pieces)
    for k, p in enumerate(r.pieces):  # pieces keep the cells (phase ids) of the core
        assert p.material_name == core.material_name and p.cell_size_m == core.cell_size_m
        assert np.count_nonzero(r.blow.piece_of_cell == k) == p.n_cells
    assert r.fracture_energy_j > 0
    # the struck part broke off: force fell below 1 % of its peak before the budget was used
    assert r.released and r.work_j < r.budget_j
    f = r.blow.indent.force_n
    assert f[-1] < s2.RELEASE_FRACTION * f.max()
    assert r.quasi_static_ratio > 1 and r.seconds > 0
    # the hammer touches the platform at the given contact point (after the
    # split the loose part may also touch it elsewhere on the platform)
    ex, ey = core.meta["edge_m"]
    hit = r.blow.mesh.nodes[r.blow.contact_nodes]
    assert hit.size and np.allclose(hit[:, 1], core.cells.shape[0] * H_CORE)
    assert np.abs(hit[:, 0] - (ex - 0.5e-3)).min() < H_CORE


def test_strike_is_deterministic_v10(split_runs):
    a, b = split_runs
    for f in ("d", "u", "work_j", "force_n", "approach_m", "fracture_energy_steps_j", "step_converged"):
        assert np.array_equal(getattr(a.blow.indent, f), getattr(b.blow.indent, f)), f
    for f in ("cell_damage", "piece_of_cell", "contact_nodes"):
        assert np.array_equal(getattr(a.blow, f), getattr(b.blow, f)), f
    assert a.budget_j == b.budget_j and a.fracture_energy_j == b.fracture_energy_j
    assert a.blow.support_force_n == b.blow.support_force_n
    for p, q in zip(a.pieces, b.pieces):
        assert np.array_equal(p.cells, q.cells) and np.array_equal(p.origin_m, q.origin_m)


def test_strike_below_cracking_is_elastic_and_uses_the_budget(core):
    r = _strike(core, 2.0, impact.hand_held())
    assert r.converged and not r.released
    assert r.blow.indent.d.max() == 0.0 and r.fracture_energy_j == 0.0
    assert len(r.pieces) == 1 and r.pieces[0].n_cells == core.n_cells
    assert abs(r.work_j / r.budget_j - 1) <= 0.02
    assert r.blow.indent.elastic_energy_j == pytest.approx(r.work_j, rel=0.03)
    # hand-held budget = core share of the relative kinetic energy of a free
    # two-body impact (Johnson 1985 sec. 11.4); the hand spring takes < 1 %
    e_star = impact.contact_modulus(GRANITE, GLASS)
    free = 0.5 * impact.reduced_mass(0.05, core.mass_kg) * 2.0 ** 2
    assert r.budget_j == pytest.approx(ind.core_energy_share(e_star, GLASS) * free, rel=0.01)
    assert r.rigid_radius_m == pytest.approx(ind.equivalent_rigid_radius(5e-3, e_star, GLASS), rel=1e-12)
    # the hand spring stiffness (an assumption, impact.DEFAULT_HAND_STIFFNESS_N_M,
    # left out of the FE) changes the budget of this 23 mg core by < 0.5 %
    # from 0 (free) to 1e5 N/m; at 1e6 N/m it is +2 % (02 sec. 4.5)
    for k in (0.0, 1e5):
        assert _strike(core, 2.0, impact.hand_held(k)).budget_j == pytest.approx(r.budget_j, rel=0.005)


def test_strike_on_anvil_balances_hammer_with_support(core):
    sup = impact.on_anvil(GRANITE, 0.05)
    r = _strike(core, 0.05, sup)
    assert r.converged and len(r.pieces) == 1
    assert abs(r.work_j / r.budget_j - 1) <= 0.02
    assert r.blow.support_force_n == pytest.approx(r.blow.indent.force_n[-1], rel=1e-6)
    # budget: core shares of both contacts, bounded by the hammer energy
    e1 = ind.core_energy_share(impact.contact_modulus(GRANITE, GLASS), GLASS)
    e2 = ind.core_energy_share(impact.contact_modulus(GLASS, GRANITE), GLASS)
    h = r.impact
    assert r.budget_j == pytest.approx(float((e1 * h.contact_energy_j + e2 * h.support_energy_j).max()), rel=1e-12)
    assert r.budget_j <= max(e1, e2) * 0.5 * 0.05 * 0.05 ** 2


def test_crack_through_on_anvil_converges_with_monotone_fallback(core, monkeypatch):
    # step 6 (a2): with the bound d >= d_prev the hybrid staggered iterates
    # can oscillate on an anvil once the crack runs (300 iterations, not
    # converged). After MONOTONE_AFTER iterations the bound becomes the
    # previous iterate, so d only grows and the step converges.
    # The stop is "d can no longer decrease", not a fixed point of the
    # original step; ``fallback_gap`` reports the distance (02 sec. 4.5).
    orig = pf.solve_damage
    kinds, run = [], [0]  # run: consecutive calls with the usual bound

    def rec(mesh, mode, pos, g_c, ell, lower, x0=None):
        mono = lower is x0  # fallback passes the iterate as its own bound
        if mono:  # fallback only after MONOTONE_AFTER usual iterations
            assert run[0] >= s2.MONOTONE_AFTER or kinds[-1]
        run[0] = 0 if mono else run[0] + 1
        kinds.append(mono)
        res = orig(mesh, mode, pos, g_c, ell, lower, x0)
        assert np.all(res.d >= lower)  # with mono: iterates never decrease
        return res

    monkeypatch.setattr(s2.pf, "solve_damage", rec)
    r = _strike(core, 0.5, impact.on_anvil(GRANITE, 0.05))
    assert r.converged and bool(np.all(r.blow.indent.step_converged))
    assert len(r.pieces) >= 2 and r.blow.monotone_steps >= 1 and any(kinds)
    assert r.blow.monotone_steps <= r.blow.indent.steps
    assert 0.0 <= r.blow.fallback_gap <= 1.0
    assert abs(r.work_j / r.budget_j - 1) <= 0.02 or r.released
    _assert_partition(core, r.blow.piece_of_cell, r.pieces)


def test_hand_strike_never_needs_the_fallback(split_runs):
    # the hand-held split converges with the bound d >= d_prev alone
    assert split_runs[0].blow.monotone_steps == 0
    assert split_runs[0].blow.fallback_gap == 0.0


def test_strike_needs_a_2d_stone():
    st = make_core(GLASS, height_m=2e-3, platform_m=3e-3, cell_size_m=1e-3, dim=3, depth_m=2e-3)
    with pytest.raises(ValueError):
        impact.strike(st, (2e-3, 2e-3), (0.0, -1.0), 0.05, 1.0, 5e-3, impact.hand_held())
