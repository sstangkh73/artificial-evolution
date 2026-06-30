# Research Summary — Artificial Life Simulation for Emergent Adaptive Behavior

**Student:** Chisanupong Injun (Grade 10 / M.4), Dibuk Phang-nga Wittayayon School, Phang-nga, Thailand
**Email:** chisanupong.injun@gmail.com
**Code (open):** https://github.com/sstangkh73/artificial-evolution
**Updated:** 30 June 2026 · *(replaces the 23 June 2026 advisor summary; all numbers below are from the report archive in the repository)*

---

## Research question

> Can adaptive, knowledge-like behavior **emerge** from an agent's interaction with a simulated ecology, when the agent is **not** given predefined semantic labels, explicit instructions about resource use, or a hand-authored task-reward function?

**One-line honest status:** the project has solid, controlled evidence for **experience-based learning** and **ecological interaction**, and an **honestly unsolved** problem in **long-run population sustainability**. It does *not* yet claim intentional farming, social transmission, or open-ended evolution.

---

## Part 1 — What the project has established (strengths, with reason + data)

Each item lists the **claim**, **why it is credible** (control/method), and the **data**. Every claim also states its scope limit, because the project's rule is: *a pattern is not promoted to "knowledge" until controls rule out simpler explanations (food hotspots, hunger pressure, deterministic movement, shared corridors).*

**1. A working ecology substrate exists — not just an idea.**
- *Reason:* a full seed → plant → fruit → consumed cycle runs and is logged, in a tuned 100×100 world.
- *Data:* Phase 1 passed 5/5 seeds; per run ≈ 139.0 germinated seeds, 33.6 mature plants, 68.6 fruiting events, 47.8 plant-food consumptions.
- *Scope:* this establishes the substrate only — no cognition claim.

**2. Reward-place learning is measurable and large.**
- *Reason:* a strict *leave-then-return* metric compared against a random-position baseline, so "returning to food" cannot be explained by chance position.
- *Data:* Phase 2 passed 3/3 seeds; mean owner return lift **41.7×** (per-seed 52.7× / 38.7× / 33.7×).
- *Scope:* shows place memory, not semantic understanding.

**3. Experience-based food-value learning — the strongest current result, and now hardened with controls + statistics.**
- *Reason:* the baseline architecture is *value-blind* at eating time (it eats whatever fits the mouth). When experience-based value memory is enabled, agents learn the energy value of foods and stop eating the low-value one. The result survives three independent controls:
  - **Per-agent causality (A1):** of 12 agents, 10 learned to skip the low-value seed — and **0/12 skipped it without first having tasted the better food**. Behavior change is bound to direct individual experience, agent by agent.
  - **Mechanism control (A5):** same seed, same config, only the memory switch differs. Memory **on** → 10/12 skip (108 seed meals, 2,163 skips); memory **off** → **0/12 skip** (382 seed meals, 0 skips); plant meals identical 52 = 52. The behavior disappears when the mechanism is removed, so it is the mechanism — not the seed or config.
  - **Quantitative threshold (A2):** agents learn seed = 50 ≪ plant = 250, and skip seed because it falls below a learned threshold (125), not because of a "bad" label.
- *Data (learning curve, low-value meals per 1k ticks):*

  | window | value-blind | value-learning |
  |---|---:|---:|
  | 0–1k | 591 | 236 |
  | 1–2k | 613 | 105 |
  | 2–3k | 370 | 15 |
  | 3–4k | 336 | 5 |
  | 4–5k | 392 | 5 |
  | 5–6k | 334 | 5 |

  Learning is **population-wide, not a single lucky agent** (10/10 who tasted both foods learned; mean time-to-learn 14.1 ticks, range 2–59).
- *Scope:* individual experience-based learning only; **not** social transmission.

**4. Agent actions can enter delayed ecological chains (proto-farming substrate).**
- *Reason:* agent-moved seeds were tracked through the full seed → plant → fruit → consumed chain against a control.
- *Data:* Phase 3 passed 3/3 seeds; ≈ 162.3 moved seeds/run, 16.3 completed moved-seed chains, moved/control lift **1.40×**.
- *Scope:* a **proto-farming substrate** — agents influence future food. This is explicitly *not* a claim of intentional or understood farming.

**5. An evolutionary (neuroevolution) controller works as a proof of concept.**
- *Reason:* a neural controller (1,281-parameter genome) is evolved by a genetic algorithm with tournament selection and elitism, evaluated across held-out seeds.
- *Data:* over 12 generations (population 30), best fitness rose to 30.0 — the harness improves controllers over generations.
- *Scope:* proof of concept that the neuroevolution loop functions; not yet a large-scale evolved-behavior result.

**6. Method discipline is itself a result.**
- *Reason / data:* 67/67 automated tests pass; movement RNG is now bound to the experiment seed (fixed 26 June), making multi-seed replication valid; new instrumentation is opt-in and byte-identical by default. The project treats **negative results as evidence** and writes an explicit "can claim / cannot claim" box for every result.

---

## Part 2 — Where the project is honestly stuck (the open problem)

**The blocker: a mortal population still goes extinct over the long run.** What makes this scientifically interesting is that the root cause has been *progressively localized with evidence*, not hand-waved:

1. First suspected **fecundity** (too few births) → ruled out: female fecundity reached near-replacement.
2. Then **demographic dynamics** → delayed density dependence produced boom–crash oscillation, but tuning it did not save the population.
3. Then **foraging access** → measured directly: agents sense food only within ~4 cells while realistic food is sparser, so at realistic density **0% of agents sense food** and intake collapses (drain:intake ≈ 453:1).
4. **Option ก (June 28) solved foraging access** — a seed-rain plant economy woke the plant lifecycle (0 → ~6,800 fruits) and a decoupled "smell" sensing radius raised the sensing fraction 0.04 → 0.77 (meal rate ×6.5) on plant-only food, with **no artificial food crutch**. Dispersed agents reached an **energy surplus of 200–550**. Access is no longer the bottleneck — proven by measured surplus.
5. **The bottleneck relocated to a deeper layer: spatial-demographic.** New telemetry (Option ข baseline) shows the honest failure mode clearly: global food looks fine after a crash (food-per-capita rose 5.2 → 19.83) but **local food-per-capita around the cluster is 0.0** — agents starve locally while food sits elsewhere. The current tension:
   - **clustering** (needed to find mates) → local food depletion → local starvation;
   - **dispersal** (needed to eat) → mates too far apart → Allee effect, births fade;
   - plus **synchronized lifespan death** producing a death wave (death-window CV 0.93).
   - Representative baseline: extinct at tick 549, peak population 148, 114 births, deaths = 123 lifespan / 37 starvation / 4 durability.

> This is reported as an **honest negative**: each "failure" sharpened the question and ruled out an alternative, which is exactly how the real bottleneck was found. The current frontier — resolving the clustering ⟂ dispersal tension and de-synchronizing death on a world with a *real* carrying capacity — is the next experiment, not a solved result.

---

## Part 3 — What the project does **not** claim (to be explicit)

- ✗ Intentional farming or semantic understanding of seeds.
- ✗ Social transmission of food knowledge (only individual learning is shown).
- ✗ Stable open-ended evolution across generations (population not yet sustained).
- Some positive results were isolated in tuned or energy-surplus regimes to separate one mechanism at a time; that is stated wherever it applies.

---

## Part 4 — Where I would value an advisor's guidance

1. **Population dynamics / theoretical ecology:** is the clustering ⟂ dispersal tension best framed as a metapopulation / Allee problem, and what minimal mechanism would let a mortal population converge around a real carrying capacity?
2. **Experiment design & statistics:** sharpening the multi-seed confirmatory protocol (effect sizes, confidence intervals, non-parametric tests) so the food-value-learning result is publication-grade.
3. **Framing & scope:** which single result is strongest to lead with for YSC / ISEF and the Junior Young Rising Stars award, and how to scope the claims so they are defensible.

I have a CV, this summary, and a fully open, reproducible codebase with a complete report archive. I would be grateful for even brief feedback, and would welcome the chance to discuss the project further.

---

## Methods note (one paragraph)

Python agent-based artificial-life simulation. The world has a grid environment, food spawning, a plant lifecycle, seeds, energy drain, a metabolism model (food composition → embodied energy, not symbolic reward), day–night and seasonal effects, agent memory, reproduction gates, lineage tracking, and experimental telemetry. Controls used across the project include random-position and current-position baselines, memory ablations, state decoupling, mechanism on/off controls, and multi-seed replication. Reproduction is gated by energy *and* body durability (durability 10 → 0 births; durability 26 → 50 births under the same energy regime), which is why "energy surplus" alone did not immediately yield births.

## Source index (key reports, in the repository)

| Topic | File |
|---|---|
| Phase 1–3 results | `reports/phase3/phase1_to_phase3_research_success_report_2026-06-13.th.md` |
| Phase 4 falsification | `reports/phase4/phase4_1_falsification_summary_2026-06-13.th.md` |
| Phase 5 state decoupling | `reports/phase5/phase5_5_state_decoupled_analysis_2026-06-13.th.md` |
| Food-value learning | `reports/food_value_learning_paper_2026-06-19.th.md` |
| Per-agent food learning | `reports/agent_food_value_individual_tracking_2026-06-23.th.md` |
| Statistical hardening (Tier A) | `reports/tier_a_completion_summary_2026-06-30.th.md` |
| Energy economy | `reports/energy_economy_diagnosis_2026-06-19.th.md` |
| Foraging-access fix (Option ก) | `reports/option_ga_foraging_access_results_2026-06-28.th.md` |
| Spatial-demographic blocker (Option ข) | `reports/option_kho_demographic_telemetry_baseline_report_2026-06-28.th.md` |
| Full competition report | `reports/competition_full_report_artificial_evolution_2026-06-29.th.md` |
