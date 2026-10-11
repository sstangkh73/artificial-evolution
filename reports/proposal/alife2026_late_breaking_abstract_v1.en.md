# ALIFE 2026 — Late-Breaking Abstract (DRAFT v1)

> Target: The 2026 Artificial Life Conference (Waterloo, Canada), Late-Breaking Abstract track.
> Deadline: 20 July 2026. Max 2 pages excluding references. Non-anonymous. Poster presentation.
> Status: DRAFT v1 — verify the ⚠️ items in "Notes to verify" at the bottom before submitting.

---

## Value Without Labels: Emergent Food-Value Discrimination and Neuroevolution in an Uninformed Artificial-Life World

**Chisanupong Injun¹** (advisor: Baphit Mangkala¹)
¹ Dibuk Phang-nga Wittayayon School, Phang-nga, Thailand
Contact: GohnGarafalo260@hotmail.com

**Keywords:** artificial life; uninformed environment; emergent behavior; experience-based value learning; neuroevolution; agent-based simulation

### 1. Motivation
Most contemporary machine learning acquires competence from human-provided labels or hand-specified reward functions, so an agent learns only what a designer already knows how to specify. We ask a complementary question in the spirit of Artificial Life: placed in an *uninformed* world — governed only by physics, with no pre-assigned meaning for any object — can an embodied agent acquire meaningful, value-sensitive behavior from experience alone? We report early results from *Artificial Evolution*, a from-scratch, pure-Python agent-based simulation built on the principle "the world does not announce meaning; let physics and experience decide."

### 2. System
The environment is a 2D world with a plant→seed→fruit resource cycle and a metabolic-physics layer: an object is edible only if it fits an agent's mouth (a size gate) and yields energy only in proportion to what the agent's body can digest. Each agent is driven by a neural network with two input streams — a local vision grid (carrying no object labels) and scalar interoceptive/environmental signals such as energy — and two output heads (movement; and an object action: none / eat / pick / drop). Crucially, eating is by default *value-blind*: an agent consumes any size-fitting item it stands on, and its memory stores only positions, never food types or values.

### 3. Result 1 — within-lifetime value discrimination is absent by default, but emerges when a learning substrate is added
We placed an edible *low-value* food (≈1 energy unit, small enough to fit any mouth) alongside high-value fruit (≈5 energy units).

- **Value-blind baseline.** Low-value intake stays flat (~330–600 items per 1000 ticks) for the agent's entire life and never declines toward zero. A 3–7× preference for high-value food is present from the very first time window — an instantaneous sensory foraging gradient, not learning.
- **Experience-driven value learning.** We added a per-agent running estimate (exponential moving average) of the energy *actually obtained* from each food type, plus an optimal-diet rule (taste an unknown type once; thereafter skip a type whose learned value falls below a fraction of the best value known). Agents correctly learn the two food values (≈1.0 vs ≈5.0) and low-value intake then follows a textbook acquisition curve, falling from 236 to ~5 items per 1000 ticks. This avoidance is *learned from realized energy, not hard-coded*, and appears with no artificial forcing once the agent is not starving.

### 4. Result 2 — behavior improves across generations by selection (neuroevolution)
Using explicit generational selection (elitism, tournament selection, crossover, and mutation) with fitness defined as food energy gathered, mean population fitness rose from a random-genome baseline of **2.07** to **10.2** (≈4.9×) over 12 generations (median fitness 0→8; best individual reaching 38) — a selection-driven learning curve rather than a designed control policy. This is a preliminary ("smoke-scale") run.

### 5. A shared bottleneck (reported as a negative result)
Both behaviors are gated by the same constraint: the agent's energy economy. Under the default economy, metabolic drain overwhelms intake (≈5 vs ≈0.01 energy per tick), agents are chronically starving, and a survival rule ("eat anything when starving") masks the learned avoidance — so value discrimination becomes visible only once the economy is made healthy and agents are sated. We report this masking explicitly rather than presenting only the regime in which the result appears.

### 6. Discussion
These early results support the uninformed-world thesis: value-sensitive foraging (within a lifetime) and improvement by selection (across generations) can both arise without teaching object meanings, provided the physical and energetic conditions permit. The project's central methodological commitment is scientific honesty: each claim is tested against control baselines (a random-agent control and a no-mechanism control in the same world and seed) and reported together with its limitations and negative results.

### 7. Limitations and ongoing work
Present results are deterministic n=1 (the movement RNG was not tied to the experiment seed); a fix enabling genuine multi-seed replication is now in place, and confirmatory 20–30-seed runs with confidence intervals and effect sizes are planned. The energy surplus used to expose learning currently relies on coarse multipliers rather than a principled rebalance; the low-value food is a synthetic probe; the neuroevolution run is smoke-scale; and a self-sustaining multi-generation population is not yet achieved. Next steps: a realistic energy rebalance, multi-seed confirmation, and an emergent-communication experiment (a neural signal channel with receiver-blind and signal-shuffle controls is already implemented).

### References
_(format per the ISAL/ALIFE template; verify)_
1. Langton, C. G. (1989). Artificial Life. In *Artificial Life* (pp. 1–47). Addison-Wesley.
2. Bedau, M. A., et al. (2000). Open Problems in Artificial Life. *Artificial Life*, 6(4), 363–376.
3. Ackley, D., & Littman, M. (1991). Interactions between Learning and Evolution. In *Artificial Life II*.

---

## Notes to verify before submitting
- ⚠️ **Author line:** confirm English spelling of your name and your advisor's name, and whether the advisor should be a co-author or an acknowledgment.
- ⚠️ **School name romanization:** "Dibuk Phang-nga Wittayayon School" — confirm the official English name.
- ⚠️ **Contact email:** using the one on file — replace if you prefer another.
- ⚠️ **Neuroevolution details:** if you want to state population size and number of evaluation worlds, confirm them from the run config (`data/neuroevolution_smoke_2026-06-27.json`). Text currently states only "12 generations," which is exact.
- ⚠️ **Numbers are from your own reports** (`reports/food_value_learning_paper_2026-06-19.th.md`, `data/neuroevolution_smoke_2026-06-27.json`) — baseline ~330–600, learned-curve 236→5, drain≈5 vs intake≈0.01, values ≈1.0/≈5.0, fitness 2.07→10.2 (≈4.9×). Re-check each reads correctly to you.
- ⚠️ **A figure helps a poster abstract.** Fig. 4 (the learning curve) from your paper is the strongest single visual — consider embedding it if the template allows.
- ⚠️ **References:** replace/extend with the papers you have actually read from `papers/` and format them to the template.
