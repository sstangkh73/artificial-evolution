# Literature evidence matrix

Last screened: 2026-09-14

This ledger separates sources whose full text was inspected from sources seen
only at title or abstract level. A source is eligible for a manuscript claim only
when the exact claim has been checked against the full text. The links below are
source or publisher copies used during screening; the bibliography uses DOI links
where available.

## Sources cleared for current manuscript claims

| Source | Full-text evidence inspected | Claim it can support | Boundary |
|---|---|---|---|
| Chrisman (1992) | AAAI proceedings PDF, especially pp. 183–184 and conclusion | Perceptual aliasing occurs when the same immediate percept corresponds to states requiring different responses; internal state or added distinctions can address incomplete perception | The paper learns predictive distinctions. It does not support saying that the present agents discovered resource age |
| Dall et al. (2005) | Full seven-page review | Ecological information must be assessed through its usefulness and consequences for decisions, not ambiguity reduction alone | The review discusses organismal and evolutionary function. It does not make the present simulation outcome a fitness effect |
| Donaldson-Matasci et al. (2010) | Full 12-page Oikos article | Information-theoretic quantity and decision-theoretic/fitness value are distinct; fitness value is defined through an optimized response and long-run fitness consequences | The present fixed learner, survival outcome, and no-birth E-series do not meet this formal fitness-value definition |
| Giannakakis et al. (2025) | Full preprint corresponding to the published *Artificial Life* article | In an embodied foraging model, environmental/task structure and architectural constraints affect evolved local learning rules and their performance | Their model evolves plasticity rules and uses food values directly; it does not test temporal toxicity, resource-age aliasing, or a capacity-matched sham |
| Grimm et al. (2020) | Full 20-page JASSS article | ODD provides a standardized structure for describing agent-based and other simulation models and aims to improve clarity and replication | ODD documentation improves reporting but does not itself validate a model |

## Candidate sources not yet cleared for manuscript claims

| Source | Screening completed | Why it remains useful | Required action |
|---|---|---|---|
| Stephens (1989), *Variance and the Value of Information* | Publisher abstract and metadata | Directly links payoff structure and resource subtypes to the value of attending to a cue | Obtain and inspect full text before citing the detailed theoretical result |
| Kaelbling, Littman, and Cassandra (1998) | Publisher abstract and author-hosted metadata | Canonical POMDP treatment of action under partial observability | Inspect the full relevant sections before using beyond basic bibliographic context |
| Schmidt, Dall, and van Gils (2010) | Abstract and metadata | Broad ecology-of-information synthesis | Inspect full text and distinguish its definitions from Dall et al. (2005) |
| Sulikowski (2017) | Abstract and selected full-text extract | Foraging choices combine energetic, ingestion, opportunity, and information tradeoffs | Inspect the full article and trace any specific claim to the cited primary studies |
| Agarwala, Chiel, and Thomas (2010) | arXiv abstract | A close theoretical parallel: maximizing information can fail to maximize food utility | Establish publication status and inspect the entire manuscript before deciding whether a preprint citation adds value |
| Borg and Channon (2020) | Publisher abstract | Artificial-life foraging study separating access to social information from behavioral/performance consequences | Inspect full text; use only if the social-information distinction sharpens the related-work section |

## Novelty boundary after screening

The literature already establishes perceptual aliasing, formal values of
information, and sensitivity of embodied learning to task structure. The present
paper should therefore claim a narrower contribution:

1. a controlled failure produced when one food-type value aliases safe and toxic
   resource ages;
2. causal restoration of discrimination by a resource-age key against a
   capacity-matched information-free sham;
3. separation of restored discrimination from survival benefit under a fixed
   embodied learner; and
4. a preregistered payoff manipulation showing an endpoint-dependent attenuation
   of survival cost, with a separate toxicity-regime replication.

## References verified at full-text level

Chrisman, L. (1992). Reinforcement learning with perceptual aliasing: The perceptual distinctions approach. In *Proceedings of the Tenth National Conference on Artificial Intelligence* (pp. 183–188). AAAI Press. https://cdn.aaai.org/AAAI/1992/AAAI92-029.pdf

Dall, S. R. X., Giraldeau, L.-A., Olsson, O., McNamara, J. M., & Stephens, D. W. (2005). Information and its use by animals in evolutionary ecology. *Trends in Ecology & Evolution, 20*(4), 187–193. https://doi.org/10.1016/j.tree.2005.01.010

Donaldson-Matasci, M. C., Bergstrom, C. T., & Lachmann, M. (2010). The fitness value of information. *Oikos, 119*(2), 219–230. https://doi.org/10.1111/j.1600-0706.2009.17781.x

Giannakakis, E., Khajehabdollahi, S., & Levina, A. (2025). Network bottlenecks and task structure control the evolution of interpretable learning rules in a foraging agent. *Artificial Life, 31*(2), 177–194. https://doi.org/10.1162/artl_a_00458

Grimm, V., Railsback, S. F., Vincenot, C. E., Berger, U., Gallagher, C., DeAngelis, D. L., Edmonds, B., Ge, J., Giske, J., Groeneveld, J., Johnston, A. S. A., Miles, A., Nabe-Nielsen, J., Polhill, J. G., Radchuk, V., Rohwäder, M.-S., Stillman, R. A., Thiele, J. C., & Ayllón, D. (2020). The ODD protocol for describing agent-based and other simulation models: A second update to improve clarity, replication, and structural realism. *Journal of Artificial Societies and Social Simulation, 23*(2), Article 7. https://doi.org/10.18564/jasss.4259
