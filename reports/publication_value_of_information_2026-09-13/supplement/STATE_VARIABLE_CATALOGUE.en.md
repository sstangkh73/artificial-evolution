# State-Variable and Process Catalogue

**Code basis:** frozen confirmatory revision `3f1af32f9e37655ed9bee5462526921eff226c8a`.

**Scope:** variables and processes that can alter movement, food exposure, eating, energetic return, toxin cost, damage, or survival in the focal experiments. Counters used only for telemetry are identified as observations rather than causes. Historical code differences are documented in `CODE_VERSION_AUDIT.en.md`.

## Focal execution path

Within a simulation tick, the environment first ages and decays existing food, updates physical and plant fields, and attempts new food and animal spawns. Each live agent then pays base, brain, and maintenance costs; resolves immediate life state; updates affective state; selects an instinct; moves or acts; decides whether to eat food on its current cell; receives post-toxin energy; processes gut contents and danger; resolves life state again; and accumulates aging damage. The run loop supplies matched-seed initialization and removes dead agents after their turns.

Implementation anchors are `Environment.step` (`world/environment.py:827`), `Agent.tick` (`agents/agent.py:218`), and `run_watch` (`scripts/run_long_emergence_watch.py:971`).

## Agent state that can affect focal outcomes

| State | Initialization in focal studies | Update/read path | Consequence |
|---|---|---|---|
| `x`, `y` | `frontier_safe_high_food` placement | movement and cell-local consumption | Determines food and danger exposure |
| `energy` | 140 | base, brain, maintenance, and movement drains; food and toxin energy; starvation resolver | Controls hunger, starvation override, movement survival, and attained follow-up |
| `age` and life stage | deterministic spread over `[61, 200)` for founders | incremented once per agent turn | Changes drain, speed, and vision at old age; distinguishes founder initial age from follow-up |
| `durability` | body-plan durability 10 | environmental danger and hunger pressure | Can cause `durability_depleted` death |
| `damage` | 0 | toxin damage and aging damage | Causes senescence at threshold 100 |
| `starvation_ticks` | 0 | increments on each zero-energy life-state check; resets when energy is positive | Causes starvation at 15 checks; two checks can occur in one simulation tick |
| `hunger_level`, `fear_level`, `cold_level` | affective defaults, then recomputed/smoothed | local food, danger, temperature, moisture, injury, allies, and energy | Selects hunger, fear, cold, or balanced action path |
| `food_value_memory` | empty | first net-energy sample, then EMA with alpha 0.3 | Supplies the accept/skip decision for each representation key |
| `remembered_food_sources` and `remembered_danger` | empty | successful ingestion and danger experience | Provide a fallback movement target and a movement penalty |
| `body` | body plan 37 for every founder except E3 tolerance spread | digestion, toxin tolerance, drains, movement score, speed, vision, repair | Fixed morphology/physiology shared across arms; E3 varies only tolerance |
| `alive`, `completed_lifespan`, `death_reason` | alive, incomplete, null | starvation, durability, senescence, or optional mortality paths | Defines removal and outcome/censoring records |

Telemetry such as `meals_by_type`, `encounters_by_kind_age`, cumulative toxin totals, and component-drain totals observes these processes. Encounter telemetry is deduplicated by `(tick, x, y)` and does not alter choice or the RNG stream.

## Body plan 37

The driver accepts a one-based body index and selects `generate_candidate_body_plans()[body_index - 1]`. Body plan 37 therefore has:

| Component | Value | Derived consequence |
|---|---:|---|
| sensor units | 2 | effective vision 4 before stage/night adjustments |
| muscle units | 2 | movement speed 2 before stage adjustment |
| armor units | 0 | durability 10 |
| brain units | 2 | passive brain drain 2 |
| metabolism rate | 1.06 | rounded base drain 1 before stage and multiplier |
| brain capacity / planning focus / memory retention | 4.1 / 0.9 / 0.88 | cognition 3.64, decision quality 5, memory score 1.085 |
| plant / meat efficiency | 1.04 / 1.08 | enzyme profile affects v2 food energy |
| toxin tolerance | 0.20 | toxin excess is load minus 0.20 when positive |
| body mass / somatic maintenance / repair efficiency / damage resistance | 1.0 / 0.3 / 0.5 / 1.0 | aging and maintenance-energy terms |

E3 replaces only founder `toxin_tolerance`, using a dedicated RNG seeded with `run_seed XOR 0x70583EED`. All other body fields remain shared.

## Food-resource state

`FoodResource` contains `kind`, nominal `energy`, `source`, optional `plant_id`, `created_tick`, and optional seed payload (`world/environment.py:367`). The focal causal fields are:

| State | Role |
|---|---|
| grid position | Eating requires agent and resource to occupy the same cell; movement senses an energy-weighted spatial signal |
| `kind` | Selects metabolism composition and the type component of the learned key |
| `energy` | Weights the movement signal; under metabolism v2 the consumed energy is recomputed from composition and body enzymes |
| `source` | Selects decay rate and plant-lifecycle signal weight |
| `created_tick` | Defines resource age for toxicity, age keys, true-age telemetry, and age-dependent decay |
| presence in `food_positions` | A rejected resource remains available until consumed or decayed and can be re-encountered |

Raw plant is supplied by wild spawning and plant lifecycle. Raw fruit is attempted by the toxin-study process. Both processes reject occupied or out-of-bounds cells. Stochastic decay depends on source and resource age before new spawns occur.

## Environment state and fixed access settings

| State or setting | Focal value/path | Consequence |
|---|---|---|
| `tick_count` | starts 0 and increments before updates | Drives resource age, day/night, season, decay, and plant timing |
| `width`, `height` | 100 × 100 for E1–E3/E5/E6/T2-RB; driver defaults for E4 are also 100 × 100 | Bounds movement and spawn positions |
| `zone_map` and fertility/physical grids | generated during `Environment.__post_init__` from map dimensions and model equations | Affect danger, wild-food placement, plant establishment, and affective state |
| `food_positions` | mutable position→resource dictionary | Source of local consumption and continuous food signal |
| `max_food` | 2,000 for the base process; low-value/toxin processes use a `3 × max_food` hard cap | Limits standing resources |
| wild-food schedule | 4 attempts/tick, multiplier 0.70, bootstrap 300 ticks, post-bootstrap multiplier 0.10 | Maintains staple supply with seasonal, fertility, and food-pressure modifiers |
| initial plants / natural seed rain | 2,500 / 12 attempts per tick in all toxin studies | Maintains renewable staple background |
| raw-fruit attempts | 20 per tick in toxin studies | Supplies the risky resource; actual placements can be fewer |
| food decay | ambient/wild 0.006 base chance; other sources 0.0015 in archived driver settings; age term capped at 0.018 | Controls persistence and resource-age distribution |
| continuous food detection | threshold 0.01, horizon 200 | Sums `resource.energy × source_weight / (Manhattan distance + 1)^2` only when each contribution meets the threshold |
| movement scoring | food signal × urgency, minus danger weighted by body avoidance, plus gather drive and small seeded noise | Chooses among shuffled cardinal directions only if the best candidate improves on the current cell |
| metabolic drain multiplier | 0.2 normally; 0.5 in E5/T2-RB; 0.05 in E4 | Multiplies base, brain, and movement energy costs |
| food-energy multipliers | global 1 except E4's 50; E6 raw-fruit multiplier 0.4–1.0 | Sets the energetic opportunity cost of rejection |
| toxin profile and scale | specified per arm | Converts resource age to potency, then toxin load to acute energy and chronic damage |

The full code-fixed ecology settings at every historical run revision are in `experiment_code_fixed_settings.csv`. CLI-controlled values and their origins are in `experiment_parameter_matrix.csv` and `experiment_parameter_origins.csv`.

## Movement and food-choice rules

1. Energy at or below 58 makes hunger dominant. A hungry agent first attempts food on its current cell.
2. If no food is eaten, it scores cardinal moves using the continuous food signal, local danger, gather drive, and seeded tie noise. Body-plan speed determines displacement and the drain multiplier prices the distance moved.
3. When the live gradient cannot improve the score, the agent can return toward a remembered food source; otherwise it uses a danger-weighted fallback.
4. Consumption requires a resource in the current cell and sufficient gape. With learning enabled, an unseen key is sampled once. A known key is accepted if its learned value is at least `0.6 × best_known`; energy at or below 6 overrides rejection.
5. B1 uses food kind as the key. B2 appends the capped resource-age bin. B3 appends a deterministic scrambled bin with the same nominal range. B4 replaces learned choice with a realized-toxin test while retaining the starvation override.
6. Metabolism v2 computes digestible energy from food composition, mass, and the body's enzyme profile. The global multiplier is applied next, then E6's raw-fruit-only multiplier.
7. Toxin costs are applied before learning and energy credit. The EMA therefore learns the bite's post-acute-toxin net energy. Chronic toxin damage is added immediately to `damage`.

## Inactive or non-identifying branches

The focal specifications leave neural control, scaffolded construction/social support, home fidelity, continuous reproduction, stochastic mortality, and oracle perception disabled. The B4 oracle is active only in its named E2 arms. E-series runs produced no births, so offspring, mutation, and multi-generation plant-dispersal consequences do not identify the reported survival effects. Large animals and physical fields remain part of the background ecology, but no treatment arm changes their parameters.

## Version and evidence boundary

This catalogue describes the frozen confirmatory implementation. Earlier batches used clean recorded revisions. The version audit shows that intervening focal-code changes added only the opt-in oracle and the opt-in raw-fruit energy control; registered comparisons were made within one revision. The launch exporter verifies archived commands, while result validators verify realized gross food energy, representation settings, batch completeness, and censoring. These are separate checks: a planned setting is not treated as realized evidence until it appears in the archived result metadata or validator output.
