# Immortal Discovery Run Analysis

วันที่รัน: 2026-06-08
Run: `experiment_049_immortal_discovery`
Manifest: `data/research_runs/experiment_049_immortal_discovery/manifest.json`
Dashboard: `data/dashboards/immortal_discovery/experiment_049_immortal_discovery/index.html`

## Setup

- Mode: `immortal-discovery`
- Seed: `7`
- Body: `body_8`
- Founders: `50`
- Founder sex mix: `25 male + 25 female`
- Immortal agents: `true`
- Max ticks requested/final tick: `8000`
- Max population: `250`
- Intervention rule: agents cannot die from energy, durability, child isolation, age, or old age; no new behavioral teaching was added.

## Primary Observation

The run did not produce population expansion despite immortality.

- Peak population: `56`
- Total births: `6`
- Matured children: `6`
- Final population: `56`
- Generation depth: founders + generation 1 only
- Extinction: no

The key pattern is not population boom. It is a long stable reproductive lock combined with delayed material discovery.

## Turning Points

### Tick 1: Immediate Settlement And First Birth Wave

- `3` nests were built.
- `6` births occurred.
- Population moved from `50` to `56`.

Interpretation: initial conditions allow a very short first reproductive wave, but not a continuing one.

### Tick 62: Reproductive Lock Begins

- First child matured at tick `62`.
- Gen1 female reproduction failures began immediately.
- Main failure reason: `low_energy|no_mate`.

Reproduction failure totals:

- `low_energy|no_mate`: `29985`
- `low_energy`: `1768`
- `low_energy|not_near_nest|no_mate`: `2`
- `low_energy|not_near_nest|nest_food_low|no_mate`: `1`

Interpretation: immortality prevents death but does not solve the fertility/replacement bottleneck. Agents remain alive but energetically and spatially unable to reproduce.

### Tick 947: Hearth Regime Appears

- First `tend_hearth` at tick `947`.
- `26` hearth maintenance events by run end.
- `213` hearth state events.

Interpretation: long life allows slow material/environmental maintenance behavior to appear even after reproduction stalls.

### Tick 3014-3043: Material Technology Breakthrough

- First `experiment_object` at tick `3014`.
- First `technology_emerged` at tick `3043`, classified as `proto_composite_type_a`.
- Total `experiment_object`: `13`
- Total `technology_emerged`: `11`
- Object use events: `85`

Interpretation: the most interesting transition is delayed technology emergence after demographic stagnation. The society stops growing, but material culture still appears.

## Learning And Communication Proxies

Agent-level outcomes:

- All `56` agents remained immortal.
- Mean memory sites per agent: `23`
- Max memory sites: `23`
- Mean friend count: `55`
- Max friend count: `55`
- Technology-building agents: `3`
- Total cooked plant meals: `5733`
- Food sharing events: `1814`
- Raw object collection events: `1875`

Interpretation:

- Agents formed a fully connected social-memory/contact graph by the end.
- They shared food and collected objects heavily.
- This is not yet proof of language. It is evidence of social contact and shared behavioral state under current rule-based communication proxies.

## Evidence Supporting Discovery

- Technology emerged without adding a direct teaching rule in this run.
- Material collection preceded object experimentation.
- Hearth maintenance preceded object experimentation.
- Objects were used repeatedly before technology classification.
- Social contact was high across the population.

## Evidence Against Strong Learning Claims

- Population did not adapt reproductively after the first wave.
- No generation 2 emerged.
- No explicit message token or language channel exists yet.
- High memory/contact metrics may partly reflect immortal agents living long enough to saturate memory and friend lists.
- Stored food partly reflects nest/world support, so food surplus must be interpreted cautiously.

## Possible Causes

- Immortality removes death but leaves agents stuck at very low energy.
- Reproduction still requires energy, nest proximity, nest food, mate availability, and cooldown.
- Gen1 sex/spatial distribution produced female adults with low energy and no mate.
- The current social/contact system shares memory but does not create explicit mate coordination.
- Material discovery needs long time, so it appears only after normal mortal runs would already have ended.

## Alternative Causes

- The result may be specific to `body_8`.
- The initial cluster may have caused immediate early births and then resource depletion.
- The technology breakthrough may depend on nest support and material accumulation rather than autonomous conceptual discovery.
- Since this is one seed, the timing of the technology transition may have high variance.

## Recommended Verification

- Repeat this mode on `body_14`.
- Run one sensory-control immortal condition.
- Add message-token communication before claiming language.
- Run ablation with technology disabled to see whether objects affect energy/reproduction.
- Run ablation with memory disabled or shuffled to test whether memory is functional.
- Add per-agent mate-distance telemetry to inspect why `no_mate` persists despite full social contact.

## Current Scientific Statement

This run shows:

> Immortality alone does not create open-ended population growth. It reveals a reproductive lock, but it also gives enough time for delayed material discovery to appear. The most interesting transition is technology emerging in a demographically stagnant immortal society.
