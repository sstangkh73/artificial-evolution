# Literature evidence matrix

Last screened: 2026-09-15

This ledger records the evidence actually inspected for every academic source
cited in the manuscript and the boundary of the claim taken from it. Evidence
level is stated explicitly: metadata or abstract screening is used only for
broad orientation, whereas detailed methodological or empirical claims require
inspection of the relevant full-text sections. Links are the repository,
publisher, or accessible author copies used during screening; the bibliography
uses DOI links where available.

## Sources cleared for current manuscript claims

| Source | Evidence inspected | Claim used in the manuscript | Boundary |
|---|---|---|---|
| Borg and Channon (2020) | Full 54-page accepted manuscript in the Keele repository: model and action definitions on manuscript pp. 17–21; Results on pp. 22–30; Discussion and Conclusion on pp. 31–33 | Social-information inputs produced persistent movement differences even where task performance was similar, supporting separate measurement of behavioral response and task benefit | The model evolves social-information use in populations. It does not establish the mechanism or survival value of resource-age information in the present fixed learner |
| Bullinaria (2017) | Full 43-page author-hosted accepted manuscript: Introduction and life-history framework on pp. 2–9; direct and imitative learning frameworks on pp. 10–21; combined-learning results and discussion on pp. 22–28 | The model studies interactions between direct and imitative learning within life-history evolution, where learning parameters and population traits evolve | The manuscript uses this as a population-level comparison; it does not transfer Bullinaria's specific meme, protection, or life-history mechanisms to the present no-birth experiments |
| Chrisman (1992) | AAAI proceedings PDF, especially pp. 183–184 and conclusion | Perceptual aliasing occurs when the same immediate percept corresponds to states requiring different responses; internal state or added distinctions can address incomplete perception | The paper learns predictive distinctions. It does not support saying that the present agents discovered resource age |
| Dall et al. (2005) | Full seven-page review | Ecological information must be assessed through its usefulness and consequences for decisions, not ambiguity reduction alone | The review discusses organismal and evolutionary function. It does not make the present simulation outcome a fitness effect |
| Donaldson-Matasci et al. (2010) | Full 12-page *Oikos* article | Information-theoretic quantity and decision-theoretic fitness value are distinct; fitness value is defined through an optimized response and long-run fitness consequences | The present fixed learner, survival outcome, and no-birth E-series do not meet this formal fitness-value definition |
| Dorin and Stepney (2024) | Full publisher article text in *Artificial Life* | Artificial Life studies living or life-like processes through synthetic systems and recognizes multiple forms, including simulated and embodied systems | The source supports field placement. It does not classify the present agents as living |
| Gershenson et al. (2020) | Full publisher article text in *Artificial Life* | Self-organization analysis must identify how organization relates to interactions among components | The age cue, value key, policy, and ecological settings here are supplied by the experimenter, so the manuscript does not claim that these components self-organized |
| Giannakakis et al. (2025) | Full preprint corresponding to the published *Artificial Life* article | In an embodied foraging model, task structure and architectural constraints affect evolved local learning rules and performance | Their model evolves plasticity rules and does not test temporal toxicity, resource-age aliasing, or a capacity-matched sham |
| Grimm et al. (2020) | Full 20-page JASSS article | ODD provides a standardized structure for describing agent-based and other simulation models and aims to improve clarity and replication | ODD documentation improves reporting but does not itself validate a model |
| Ha (2019) | Full publisher article text in *Artificial Life* | Reinforcement learning can evaluate and improve embodied agent design in a task-dependent setting | The present work holds morphology and learner structure fixed apart from the registered representation manipulation |
| McCallum (1996) | University of Rochester repository record and abstract; repository file availability confirmed | Selective perception can remove irrelevant distinctions, whereas memory can augment a state representation when crucial features are hidden | Used as a broad hidden-state/representation precedent, not as evidence that the present agents discover resource age or use McCallum's algorithms |
| Provenza (1995) | Utah State University repository metadata and abstract; publisher full-text link confirmed | Post-ingestive consequences can condition food preference and intake, with nutrient adequacy and toxin-related malaise affecting learned preference | Used as biological motivation only; the present numerical update is not a physiological model of ruminant learning |
| Stephens and Krebs (1986) | JSTOR and Princeton University Press book metadata and description | Classic foraging theory frames item acceptance as part of an energetic decision problem with background opportunities and constraints | No claim is made that the present fixed threshold is an optimal-foraging solution; no chapter-specific empirical claim is taken from metadata alone |
| Cipollini and Levey (1997) | Full accessible article text plus Wiley/ESA publisher metadata; Introduction, experimental design, discussion, and conclusion inspected | Fruit secondary metabolites can affect vertebrate fruit choice, and nutrient-toxin titration can test their joint influence | Used to motivate a stylized nutrient-toxin analogy, not the model's exact toxic-safe-toxic age profile, coefficients, or universality |
| Scholz et al. (2017) | Full open-access PNAS article, including model assumptions, results, and discussion | A data-driven sequential-decision model couples feeding as information sampling with nutrient intake and produces speed-accuracy and exploration-exploitation trade-offs | Their organism estimates ambient food availability; the present agents learn post-ingestive item values and receive resource age directly in B2 |

## Candidate sources not used for current manuscript claims

| Source | Screening completed | Why it remains useful | Required action |
|---|---|---|---|
| Sasaki and Tokoro (1999) | MIT Press metadata and abstract; publisher page reports that the PDF is unavailable without access | Early *Artificial Life* food-versus-poison learning study under changing environments | Removed from the manuscript and bibliography on 2026-09-15 under rule R3; inspect the full text before any future citation |
| Stephens (1989), *Variance and the Value of Information* | Publisher abstract and metadata | Directly links payoff structure and resource subtypes to the value of attending to a cue | Obtain and inspect full text before citing the detailed theoretical result |
| Kaelbling, Littman, and Cassandra (1998) | Publisher abstract and author-hosted metadata | Canonical POMDP treatment of action under partial observability | Inspect the full relevant sections before using beyond basic bibliographic context |
| Schmidt, Dall, and van Gils (2010) | Abstract and metadata | Broad ecology-of-information synthesis | Inspect full text and distinguish its definitions from Dall et al. (2005) |
| Sulikowski (2017) | Author-hosted abstract and opening full-text sections; complete file was blocked in the current browser | Foraging choices combine energetic, ingestion, opportunity, and information trade-offs | Inspect the complete article before citing; the manuscript currently does not rely on it |
| Agarwala, Chiel, and Thomas (2010) | arXiv abstract | A close theoretical parallel: maximizing information can fail to maximize food utility | Establish publication status and inspect the entire manuscript before deciding whether a preprint citation adds value |

## Novelty boundary after screening

The literature already establishes perceptual aliasing, formal values of
information, sensitivity of embodied learning to task structure, and several
ways in which information access or learning structure can change behavior in
artificial-life systems. The present paper therefore claims a narrower
contribution:

1. a controlled failure produced when one food-type value aliases safe and toxic
   resource ages;
2. causal restoration of discrimination by a resource-age key against a
   capacity-matched information-free sham;
3. separation of restored discrimination from survival benefit under a fixed
   embodied learner; and
4. a preregistered payoff manipulation showing an endpoint-dependent attenuation
   of the registered survival cost, with a separate within-configuration
   replication under monotonic toxicity.

## References and evidence levels

Borg, J. M., & Channon, A. (2020). The effect of social information use without learning on the evolution of social behavior. *Artificial Life, 26*(4), 431–454. https://doi.org/10.1162/artl_a_00328

Bullinaria, J. A. (2017). Imitative and direct learning as interacting factors in life history evolution. *Artificial Life, 23*(3), 374–405. https://doi.org/10.1162/ARTL_a_00237

Chrisman, L. (1992). Reinforcement learning with perceptual aliasing: The perceptual distinctions approach. In *Proceedings of the Tenth National Conference on Artificial Intelligence* (pp. 183–188). AAAI Press. https://cdn.aaai.org/AAAI/1992/AAAI92-029.pdf

Dall, S. R. X., Giraldeau, L.-A., Olsson, O., McNamara, J. M., & Stephens, D. W. (2005). Information and its use by animals in evolutionary ecology. *Trends in Ecology & Evolution, 20*(4), 187–193. https://doi.org/10.1016/j.tree.2005.01.010

Donaldson-Matasci, M. C., Bergstrom, C. T., & Lachmann, M. (2010). The fitness value of information. *Oikos, 119*(2), 219–230. https://doi.org/10.1111/j.1600-0706.2009.17781.x

Dorin, A., & Stepney, S. (2024). What is Artificial Life today, and where should it go? *Artificial Life, 30*(1), 1–15. https://doi.org/10.1162/artl_e_00435

Gershenson, C., Trianni, V., Werfel, J., & Sayama, H. (2020). Self-organization and Artificial Life. *Artificial Life, 26*(3), 391–408. https://doi.org/10.1162/artl_a_00324

Giannakakis, E., Khajehabdollahi, S., & Levina, A. (2025). Network bottlenecks and task structure control the evolution of interpretable learning rules in a foraging agent. *Artificial Life, 31*(2), 177–194. https://doi.org/10.1162/artl_a_00458

Grimm, V., Railsback, S. F., Vincenot, C. E., Berger, U., Gallagher, C., DeAngelis, D. L., Edmonds, B., Ge, J., Giske, J., Groeneveld, J., Johnston, A. S. A., Miles, A., Nabe-Nielsen, J., Polhill, J. G., Radchuk, V., Rohwäder, M.-S., Stillman, R. A., Thiele, J. C., & Ayllón, D. (2020). The ODD protocol for describing agent-based and other simulation models: A second update to improve clarity, replication, and structural realism. *Journal of Artificial Societies and Social Simulation, 23*(2), Article 7. https://doi.org/10.18564/jasss.4259

Ha, D. (2019). Reinforcement learning for improving agent design. *Artificial Life, 25*(4), 352–365. https://doi.org/10.1162/artl_a_00301

McCallum, R. A. (1996). *Reinforcement learning with selective perception and hidden state* (Doctoral dissertation, University of Rochester). http://hdl.handle.net/1802/842

Provenza, F. D. (1995). Postingestive feedback as an elementary determinant of food preference and intake in ruminants. *Journal of Range Management, 48*(1), 2–17. https://doi.org/10.2307/4002498

Stephens, D. W., & Krebs, J. R. (1986). *Foraging theory*. Princeton University Press. https://doi.org/10.2307/j.ctvs32s6b

Cipollini, M. L., & Levey, D. J. (1997). Why are some fruits toxic? Glycoalkaloids in *Solanum* and fruit choice by vertebrates. *Ecology, 78*(3), 782–798. https://doi.org/10.1890/0012-9658(1997)078[0782:WASFTG]2.0.CO;2

Scholz, M., Dinner, A. R., Levine, E., & Biron, D. (2017). Stochastic feeding dynamics arise from the need for information and energy. *Proceedings of the National Academy of Sciences, 114*(35), 9261–9266. https://doi.org/10.1073/pnas.1703958114
