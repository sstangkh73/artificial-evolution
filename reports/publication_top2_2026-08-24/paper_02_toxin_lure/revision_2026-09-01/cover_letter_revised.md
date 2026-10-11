# Cover Letter

September 1, 2026

Dear Professors Dorin and Stepney,

Please consider the manuscript “When Intermittent Safety Lures an Artificial Forager: Temporal Toxicity Under Perceptual Aliasing” as a Letter for *Artificial Life*.

Artificial-life research asks how life-like adaptive behavior can arise from interactions among an organism, its body, and its environment. Within-lifetime learning is one route to such adaptation: a synthetic organism may attach value to a resource from the energetic consequences of consuming it rather than receive a designer-supplied semantic label. Our manuscript identifies a precise limitation of that process. When a single perceptual food category combines a fresh-toxic state with an aged-safe state, local outcome learning can average the two states and reverse avoidance into preference for the partly toxic food. We call this inversion the **lure**.

The manuscript contributes an analytic condition for the lure and controlled evidence from four illustrative learning rules. With fresh fruit worth approximately 2 net energy units, aged fruit 10, and a consistently safe staple 5, a type-only learner ranks the mixed fruit above the staple whenever the toxic-state frequency is below 62.5%. At 30% toxicity, 63.3% +/- 1.3% of agents using the simulation's value gate were lured; the effect also appeared with epsilon-greedy, softmax, and greedy sample-average learning across 30 independent seed/runs, 100 agents per seed, and 40 encounters per agent. A non-monotonic toxic-safe-toxic age profile additionally shows why a single type value cannot target a hidden safe window.

The work fits the scope of *Artificial Life* because it uses a synthetic organism-environment system to investigate the conditions under which adaptive foraging behavior can, and cannot, emerge from local experience. The revised Introduction now engages directly with work published in *Artificial Life* on learning and evolution in changing environments, direct learning in life-history evolution, evolved plasticity in embodied foragers, emergence, and learned resource behavior. It distinguishes the new lure effect from the established concepts of perceptual aliasing and partial observability.

This is a substantially rewritten version of manuscript ARTL-2026-0228. In response to the editorial decision, the cover letter has been made stand-alone, the Artificial Life context has been stated before the technical mechanism, and the Introduction has been expanded to engage the journal's relevant literature. The empirical claims remain deliberately bounded. The controlled sated experiments establish a representation-level and behavioral failure, not mortality, survival, reproductive, or evolutionary fitness costs. Those outcomes are reserved for a future full-ecology study.

The manuscript is original, is not under consideration elsewhere, and is intended as a Letter of fewer than 2,000 words in its main scientific text. Reproduction code and source-data tables are included as supplementary material. This research received no external funding, and I declare no competing interests.

OpenAI Codex (OpenAI; https://openai.com/codex; accessed September 1, 2026) assisted with literature discovery, evidence auditing, statistical and claim-boundary review, and manuscript drafting. The system is not an author. I reviewed the work and accept full responsibility for the manuscript.

Sincerely,

Chisanupong Injun  
Deebuk Phangnga Wittayayon School  
Phang Nga 82000, Thailand  
chisanupong.injun@gmail.com  
ORCID: https://orcid.org/0009-0000-2979-1916
