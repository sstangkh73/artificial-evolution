# Cover Letter

September 1, 2026

Professor Alan Dorin and Professor Susan Stepney

Co-Editors-in-Chief, *Artificial Life*

Dear Professors Dorin and Stepney,

Please consider the manuscript **“When Intermittent Safety Lures the Learner: Sufficiency and Limits of Experience-Based Food Valuation in an Artificial Ecology”** as an Article for *Artificial Life*.

This submission is a complete reconception and substantial expansion of the Letter previously submitted as ARTL-2026-0228, “When Intermittent Safety Lures the Learner: Temporal Toxicity Under Perceptual Aliasing,” which was declined before external review. The editorial comments stated that the cover letter did not explain the work in a stand-alone manner and that the Introduction did not engage the relevant literature, especially work published in *Artificial Life*, with sufficient depth. The new manuscript responds directly by presenting the research as a 6,000-word Article, adding a full stationary-learning experiment from the project's completed internal evidence, expanding the theoretical framing, and positioning the contribution against Artificial-Life research on learning, embodiment, emergence, environmental structure, and food-versus-poison adaptation.

The scientific problem is whether an artificial organism can acquire useful food selectivity from its own metabolic consequences without being given semantic labels—and where that strategy fails. The agent stores food value from the net energy realized after ingestion. This energy is computed by the same metabolism model that changes the agent's energetic state; the environment does not provide labels such as “good food,” “bad food,” “toxic,” or “safe age.” The learning capacity is designed, but the contents of memory and the resulting preference are acquired through individual experience.

The Article contains two linked studies. In Study 1, 50-agent spatial artificial ecologies were run for 3,000 ticks under ten paired random seeds with the value-memory mechanism disabled or enabled. Enabling memory reduced lower-value food consumption from a mean of 1,945.3 to 423.0 meals per run. The mean paired reduction was 1,522.3 meals, with a 95% *t* interval of 1,340.7–1,703.9; every pair favored learning, and an exact two-sided paired sign-flip test gave *p* = 0.001953. Of 500 treatment agents, 491 experienced both focal foods and all 491 subsequently skipped the lower-value food; no agent skipped it before experiencing the higher-value comparator. The matched memory-disabled runs produced no skipping.

Study 2 asks what happens when a single observable food type hides temporally different safety states. Fresh fruit yielded approximately 2 net energy units, aged fruit 10, and a consistently safe staple 5. If toxic fresh encounters occur with probability *p*, a converged type-only estimate is `10 - 8p`, so the mixed resource outranks the staple whenever *p* < 0.625. Across 30 seed/runs, 100 agents per seed, and 40 opportunities per agent, 63.3% ± 1.3 percentage points of agents using the simulation gate ranked fruit above the staple at 30% toxicity. This inversion—the **lure**—also appeared with epsilon-greedy, softmax, and greedy sample-average learners. In a toxic-safe-toxic age profile, safe-window discrimination was exactly zero because age was unavailable to the policy.

The manuscript fits *Artificial Life* because it uses a synthesized software ecology to test a mechanistic question about life-like adaptive behavior. It does not present reinforcement learning merely as a benchmark optimizer. It studies how body-grounded consequence, designed learning architecture, environmental regularity, and perceptual representation jointly determine what behavior can emerge in an artificial organism. The revised Introduction and Discussion engage work in *Artificial Life* by Dorin and Stepney; Gershenson and colleagues; Sasaki and Tokoro; Bullinaria; Giannakakis, Khajehabdollahi, and Levina; Ha; and Garbus and Pollack. The Article's positive-control-to-boundary arc complements that literature: stationary value learning establishes what local experience can accomplish, while hidden temporal state identifies an information constraint that prevents state-sensitive adaptation.

The claims are intentionally bounded. The experiments demonstrate within-lifetime value-guided behavior and a representational failure. They do not demonstrate semantic understanding, social transmission, evolved learning rules, mortality cost, reproductive cost, selection, or evolutionary fitness. A full-ecology comparison of type-only, type-by-age, and age-aware deferral policies is identified as the next experiment rather than reported as completed.

Source-data tables, completed paired runs, analysis scripts, toxin harnesses, and minimum reproducibility code accompany the draft package. Before journal submission, the archive will be tied to a tagged release and assigned a persistent public DOI. The work uses only software agents and involves no human participants, human data, animals, or biological specimens.

The manuscript is original, is not published, and is not under review elsewhere. A version of the shorter temporal-toxicity Letter was submitted only to *Artificial Life* as ARTL-2026-0228 and received no external peer review. The present Article adds the stationary experiment, substantially revises the framing and analysis, and replaces the former Letter rather than being submitted concurrently.

OpenAI Codex (OpenAI; accessed September 1, 2026) assisted with literature discovery, evidence auditing, statistical and claim-boundary review, manuscript restructuring, and drafting. It is not an author. I will verify every citation, analysis, claim, and sentence and accept full responsibility for the submitted work.

Thank you for considering this Article.

Sincerely,

Chisanupong Injun

Deebuk Phangnga Wittayayon School

Phang Nga 82000, Thailand

Email: chisanupong.injun@gmail.com

ORCID: https://orcid.org/0009-0000-2979-1916
