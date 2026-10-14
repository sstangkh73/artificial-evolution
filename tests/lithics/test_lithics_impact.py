"""Step 4 (a): hammer kinetic energy -> peak Hertz force (Johnson 1985 sec. 11.4)."""
import math

import numpy as np
import pytest
from scipy.integrate import quad

from lithics import impact
from lithics.materials import load_material

GLASS = load_material("glass_soda_lime")
GRANITE = load_material("granite")
E_STAR = impact.contact_modulus(GRANITE, GLASS)
R = 0.02


def test_duration_coefficient_matches_integral_and_johnson():
    integral, _ = quad(lambda x: 1.0 / math.sqrt(1.0 - x ** 2.5), 0.0, 1.0)
    assert impact.DURATION_COEFF == pytest.approx(2.0 * integral, rel=1e-8)
    assert round(impact.DURATION_COEFF, 2) == 2.94  # Johnson 1985 eq. 11.24


def test_hand_computed_values():
    # m = 1/3 kg (0.5 kg hammer on 1 kg core), v = 5 m/s
    m = 0.5 * 1.0 / 1.5
    h = impact.hertz_impact(m, 5.0, R, E_STAR)
    d = (15 * m * 25 / (16 * E_STAR * math.sqrt(R))) ** 0.4
    assert h.max_approach_m == pytest.approx(d, rel=1e-12)
    assert h.max_force_n == pytest.approx(4 / 3 * E_STAR * math.sqrt(R) * d ** 1.5, rel=1e-12)
    # stored energy at the peak equals the relative kinetic energy
    assert h.elastic_energy_j == pytest.approx(0.5 * m * 25, rel=1e-12)
    # peak force consistent with the static Hertz solution at that force
    from lithics.contact import hertz_sphere_flat
    s = hertz_sphere_flat(h.max_force_n, R, E_STAR)
    assert s.approach_m == pytest.approx(h.max_approach_m, rel=1e-10)
    assert s.max_pressure_pa == pytest.approx(h.max_pressure_pa, rel=1e-10)


def test_scaling_exponents():
    a = impact.hertz_impact(0.3, 2.0, R, E_STAR)
    b = impact.hertz_impact(0.3, 4.0, R, E_STAR)
    assert b.max_force_n / a.max_force_n == pytest.approx(2.0 ** 1.2, rel=1e-12)
    assert b.duration_s / a.duration_s == pytest.approx(2.0 ** -0.2, rel=1e-12)
    c = impact.hertz_impact(0.6, 2.0, R, E_STAR)
    assert c.max_force_n / a.max_force_n == pytest.approx(2.0 ** 0.6, rel=1e-12)


@pytest.mark.parametrize("mh,mc", [(0.5, 1.0), (1.0, 0.2)])
def test_ode_free_core_matches_analytic(mh, mc):
    """Independent oracle: integrate the two-body equations directly."""
    sup = impact.hand_held(0.0)  # free core
    r = impact.lumped_impact(mh, 5.0, R, E_STAR, mc, sup)
    h = impact.hertz_impact(impact.reduced_mass(mh, mc), 5.0, R, E_STAR)
    assert r.max_force_n == pytest.approx(h.max_force_n, rel=1e-5)
    assert r.max_approach_m == pytest.approx(h.max_approach_m, rel=1e-6)
    assert r.duration_s == pytest.approx(h.duration_s, rel=1e-5)
    assert r.energy_error < 1e-7
    # elastic collision: momentum and energy conserved -> classical exit speeds
    vh = (mh - mc) / (mh + mc) * 5.0
    vc = 2 * mh / (mh + mc) * 5.0
    assert r.hammer_velocity_after_m_s == pytest.approx(vh, abs=1e-5)
    assert r.core_velocity_after_m_s == pytest.approx(vc, abs=1e-5)


@pytest.mark.parametrize("k", [1e3, 5e4, 1e6])
@pytest.mark.parametrize("mh,mc,v", [(0.5, 1.0, 5.0), (1.0, 0.1, 1.0)])
def test_hand_stiffness_barely_matters(k, mh, mc, v):
    free = impact.hertz_impact(impact.reduced_mass(mh, mc), v, R, E_STAR)
    r = impact.lumped_impact(mh, v, R, E_STAR, mc, impact.hand_held(k))
    assert r.max_force_n == pytest.approx(free.max_force_n, rel=5e-3)
    assert r.energy_error < 1e-7


def test_anvil_series_limit():
    """Massless core between hammer and a fixed anvil: both contacts carry the
    same force, so delta = P^(2/3) (K1^(-2/3) + K2^(-2/3)) -> Hertz impact with
    K_eff = (K1^(-2/3) + K2^(-2/3))^(-3/2) and the hammer mass. The error must
    shrink as the core mass goes to zero."""
    r2 = 0.05
    sup = impact.on_anvil(GRANITE, r2)
    k1 = impact.hertz_stiffness(R, E_STAR)
    k2 = impact.hertz_stiffness(r2, impact.contact_modulus(GLASS, GRANITE))
    keff = (k1 ** (-2 / 3) + k2 ** (-2 / 3)) ** -1.5
    # Hertz impact with stiffness keff: delta_max from 1/2 m v^2 = (2/5) keff delta^(5/2)
    p_ref = keff * (0.5 * 0.5 * 25 / (0.4 * keff)) ** 0.6
    errs = []
    for mc in (1e-4, 1e-5, 1e-6):
        r = impact.lumped_impact(0.5, 5.0, R, E_STAR, mc, sup, core_material=GLASS)
        errs.append(abs(r.max_force_n / p_ref - 1))
    # core inertia error falls about as sqrt(m_c): > 2x per decade
    assert errs[0] > 2 * errs[1] > 4 * errs[2]
    assert errs[2] < 2e-3
    assert r.max_support_force_n == pytest.approx(r.max_force_n, rel=1e-3)


def test_anvil_conserves_energy_and_momentum():
    sup = impact.on_anvil(GRANITE, 0.05, anvil_mass_kg=3.0)
    r = impact.lumped_impact(0.5, 5.0, R, E_STAR, 1.0, sup, core_material=GLASS)
    assert r.energy_error < 1e-7
    assert 0 < r.max_elastic_energy_j <= 0.5 * 0.5 * 25 * (1 + 1e-9)
    p = 0.5 * r.hammer_velocity_after_m_s + 1.0 * r.core_velocity_after_m_s + 3.0 * r.anvil_velocity_after_m_s
    assert p == pytest.approx(0.5 * 5.0, rel=1e-6)
    assert r.anvil_velocity_after_m_s > 0
    # anvil backs the core: the peak hammer force exceeds the hand-held case
    hand = impact.lumped_impact(0.5, 5.0, R, E_STAR, 1.0, impact.hand_held())
    assert r.max_force_n > hand.max_force_n


def test_quasi_static_assumption_holds_for_typical_strike():
    # contact time vs longitudinal wave crossing a 5 cm glass core
    h = impact.hertz_impact(impact.reduced_mass(0.5, 1.0), 5.0, R, E_STAR)
    c = math.sqrt(GLASS.youngs_modulus_pa / GLASS.density_kg_m3)
    assert h.duration_s > 10 * (0.05 / c)
    c_hammer = math.sqrt(GRANITE.youngs_modulus_pa / GRANITE.density_kg_m3)
    assert h.duration_s > 10 * (0.05 / c_hammer)


def test_effective_radius():
    assert impact.effective_radius(0.02) == 0.02
    assert impact.effective_radius(0.02, 0.02) == pytest.approx(0.01)
    with pytest.raises(ValueError):
        impact.effective_radius(0.02, 0.0)


def test_bad_inputs():
    with pytest.raises(ValueError):
        impact.hertz_impact(0.0, 1.0, R, E_STAR)
    with pytest.raises(ValueError):
        impact.Support("table")
    with pytest.raises(ValueError):
        impact.on_anvil(GRANITE, 0.0)
    with pytest.raises(ValueError):
        impact.lumped_impact(0.5, 5.0, R, E_STAR, 1.0, impact.on_anvil(GRANITE, 0.05))
    assert np.isfinite(impact.reduced_mass(1.0, math.inf))
