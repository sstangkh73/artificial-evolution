# ALIFE 2026 — Late-Breaking Abstract (DRAFT v3 — red-team fixes)

> Target: The 2026 Artificial Life Conference, Late-Breaking Abstract track. Deadline 20 July 2026. ≤2 pages excl. refs. Poster.
> Change from v1: centered on the age-dependent-toxicity / store-to-detoxify result; food-value learning reduced to one setup sentence; neuroevolution dropped for space (say the word to re-add).
> Change v2→v3 (red-team A/B/C): numbers now multi-seed (30 seeds × 100 agents) with 95% CIs; added a sentence positioning the work against the known POMDP/aliasing frame and stating what is new (the *lure*); added real related work. New figure: `figures/toxin_multiseed_ci.png`.
> Verify the ⚠️ items at the bottom before submitting.

---

## When Detoxification Lures the Learner: Non-Stationary Toxicity Defeats Emergent Value Learning in an Uninformed World

**Chisanupong Injun¹** (advisor: Baphit Mangkala¹)
¹ Dibuk Phang-nga Wittayayon School, Phang-nga, Thailand

**Keywords:** artificial life; uninformed environment; non-stationary reward; perceptual aliasing / partial observability; emergent value learning; food processing; deferred consumption

### Motivation
In an *uninformed* artificial-life world — physics only, no object labels — within-lifetime value learning already produces emergent **avoidance** of low-value food: an agent learns from the energy it actually obtains to skip a poor food type (learned, not hard-coded). We ask what happens when the danger is **non-stationary** — a food that is toxic when fresh but detoxifies with age. This turns eating from a two-way choice (eat / avoid) into a three-way one: eat-now (get poisoned), avoid (waste recoverable energy), or **defer** — see the value, decline to eat now, store it, wait for it to detoxify, then eat it safely later. Deferral is the true optimum, and it is a *delayed-reward* problem.

### System
A 2D world with a plant→seed→fruit cycle and a metabolic-physics layer: food is edible only if it fits an agent's mouth and yields only digestible energy. Neural-network agents perceive an unlabeled local vision grid plus scalar signals; by default eating is *value-blind* (any size-fitting item is consumed) and value learning, when enabled, is a per-type running estimate of realized energy (`food_value_memory[kind]`). We added age-dependent toxicity as opt-in physics: `toxin_detox_ticks` (toxicity decays fresh→safe with age) and a non-monotonic `toxin_safe_window` (toxic → safe → toxic again: unripe → ripe → spoiled). Both default off (byte-identical); test suite 93/93.

### Result 1 — monotonic detox: the learner is *lured into* the poison
With fruit toxic when fresh (net ≈2 energy) and safe when old (≈10), the per-type learner — which cannot perceive an item's age — settles on a single **blended** value (≈7.75, 95% CI ±0.06) and eats fruit of all ages indiscriminately, so ≈50% of its fruit meals are toxic (30 seeds × 100 agents). Counterintuitively, detoxification makes things **worse** than permanent toxicity: because the blended value now exceeds that of the always-safe staple (≈5), **88% ±1% of agents rank the half-toxic fruit as their *best* food and actively seek it** — whereas under static toxicity they would have learned fruit ≈2 < staple ≈5 and avoided it. **Partial, time-varying safety is more dangerous than constant toxicity to a state-blind learner, because it inflates the perceived average value and lures the agent in.**

### Result 2 — non-monotonic "safe window": a simple age rule cannot rescue it
When toxicity returns with over-ripening (toxic at age 0–3, safe 3–7, toxic 7+), the reward-vs-age landscape is a mesa (≈2 / 10 / 2). The per-type learner's probability of eating is **statistically identical inside and outside the safe window** (≈9% vs ≈9%; discrimination 0.0 ±0.0 pts against an ideal of 100 pts; 30 seeds × 100 agents) — it cannot target the safe window (the optimum is to eat *only* within 3–7) — and ~60% ±1% of meals are toxic. Here even an "older = safer" heuristic fails; safe exploitation requires representing the **whole** value(age) curve, not a single per-type number.

### Mechanism
Both failures share one cause: keying value by food *type* collapses two or three hidden age-states that share the same observable label into one averaged value — a perceptual-aliasing / partial-observability limit. Deferral is harder still: its reward (safe energy) arrives only after "store and wait," so an immediate-reward estimator cannot assign temporal credit to "store now to eat later." By construction, individual immediate-reward learning can therefore yield avoidance but not deferral.

We do **not** claim perceptual aliasing or delayed credit as new — both are classical [4,6]. Our contribution is (i) the **lure**: in an uninformed, emergent-value ALife setting, time-varying detoxification does not merely *evade* avoidance learning, it **inverts** it, making a half-toxic food the learner's top-ranked choice (88% of agents) — so partial safety is more dangerous than constant toxicity; and (ii) framing store-to-detoxify food processing as an *emergence* question for evolution rather than a design target, and locating exactly where within-lifetime learning must give way to representation or selection.

### Ongoing work
We are building the two routes the analysis predicts are required: (i) a freshness **cue** plus a (type × state) value representation, for within-lifetime discrimination; and (ii) **item-level storage** (a larder preserving each item's age) plus **generational selection**, to test whether "store-to-detoxify" deferral — timing consumption to the safe window — *emerges* without being taught. We report the failure results here; the deferral behavior itself is not yet demonstrated.

### Honesty and limitations
Results are from the real simulation in a controlled *sated* regime (removing a foraging/starvation confound) and are **replicated across 30 seeds × 100 agents with 95% confidence intervals** (the failures are robust, not a single-seed artifact). Working in the sated regime is a deliberate choice: it isolates the diet-learning mechanism from an unrelated spatial-foraging bottleneck in the full ecology, so the reported limit is a property of the learner, not of starvation. The low-value and toxic foods are synthetic probes; all mechanisms are opt-in and byte-identical when off. We deliberately foreground the negative and counterintuitive results and separate what is demonstrated (avoidance; the breakdown and the lure) from what is predicted (deferral).

### Related work (one line)
Evolved agents that forage and behave in physics-based worlds are an ALife staple [3]; the open-endedness agenda motivates learning in *uninformed* environments [1,2]. Our failures are instances of two classical results — perceptual aliasing / partial observability [4,5] and the temporal-credit-assignment problem [6] — and the biological parallel is discriminative learned taste aversion [7], where an animal can only condition on food safety if a distinguishing cue is available. The novelty here is the *lure* effect and the emergence framing, not the underlying limits.

### References
_(format per the ISAL/ALIFE template; verify)_
1. Langton, C. G. (1989). Artificial Life. In *Artificial Life* (pp. 1–47). Addison-Wesley.
2. Bedau, M. A., et al. (2000). Open Problems in Artificial Life. *Artificial Life*, 6(4), 363–376.
3. Sims, K. (1994). Evolving Virtual Creatures. *SIGGRAPH '94*, 15–22.
4. Whitehead, S. D., & Ballard, D. H. (1991). Learning to perceive and act by trial and error. *Machine Learning*, 7(1), 45–83.
5. Kaelbling, L. P., Littman, M. L., & Cassandra, A. R. (1998). Planning and acting in partially observable stochastic domains. *Artificial Intelligence*, 101(1–2), 99–134.
6. Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.
7. Garcia, J., & Koelling, R. A. (1966). Relation of cue to consequence in avoidance learning. *Psychonomic Science*, 4, 123–124.

---

## Notes to verify before submitting
- ⚠️ **Author line / school romanization / advisor** — confirm English spelling and whether advisor is co-author or acknowledgment (same as v1).
- ✅ **Numbers now multi-seed (from `scripts/run_toxin_multiseed.py`, 30 seeds × 100 agents, 95% CI):** R1 blend 7.75 ±0.06, 88% ±1% agents lured, 50% ±0% toxic meals, staple 5; R2 P(eat) in-window 9% vs out-window 9% → discrimination 0.0 ±0.0 pts (ideal 100), 60% ±1% toxic; 93/93 tests. Re-run before submitting to confirm.
- ⚠️ **References — READ before final submission:** #3 Sims verified in repo (`papers/siggraph94.pdf`). #4–7 (Whitehead & Ballard; Kaelbling et al.; Sutton & Barto; Garcia & Koelling) are the correct canonical sources but **you must read at least the ones cited in-text ([4] and [6]) yourself** before submitting — do not cite unread.
- ⚠️ **Figures — use the REAL sim figures only:** `figures/toxin_multiseed_ci.png` (headline, multi-seed CI), `figures/store_detox_sim_result.png` (R1 detail), `figures/toxin_window_sim_result.png` (R2 detail). **Do NOT** use the PREDICTED deferral-signature figures as if they were results.
- ⚠️ **Do not claim deferral is demonstrated.** The larder / defer-store / selection are not built — keep them strictly in "Ongoing work / predicted."
- ⚠️ **Neuroevolution dropped** for a tighter single story; say the word to re-add a sentence (selection is a lever you already have and it connects to route R2).
- ⚠️ **Length:** trim the System paragraph first if you exceed 2 pages in the official template.
