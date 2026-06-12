# Current State

## Purpose

This document separates the project into three buckets:

- implemented now
- partially implemented
- planned only

It is intended to reduce confusion between older prototype documentation,
current code behavior, and longer-term research goals.

## Implemented Now

### World And Ecology

- A `100x100` grid world is implemented in [world/environment.py](/C:/artificial-evolution/world/environment.py).
- The world is divided into four ecological zones:
  - `safe_low_food`
  - `safe_high_food`
  - `danger_high_food`
  - `danger_low_food`
- Day/night cycles reduce effective vision.
- Seasons change plant-food spawn rates.
- Plant food spawns continuously with zone-based density.
- Large animals spawn as herds in dangerous, food-rich zones.
- Environmental danger can damage agent durability.

### Body System

- Body construction uses a fixed `TOTAL_BODY_COST = 100` budget.
- Morphology dimensions are implemented:
  - `sensor_units`
  - `muscle_units`
  - `armor_units`
  - `brain_units`
- Continuous and hidden traits are implemented:
  - `brain_capacity`
  - `memory_retention`
  - `planning_focus`
  - `cooperation_drive`
  - `parenting_instinct`
  - `curiosity`
  - `fear`
  - `aggression`
  - `metabolism_rate`
  - `plant_efficiency`
  - `meat_efficiency`
  - `reproduction_drive`
  - `reproduction_investment`
- Archetype-backed body generation is implemented in [agents/body.py](/C:/artificial-evolution/agents/body.py).

### Agent Life Cycle

- Agents have life stages:
  - `child`
  - `juvenile`
  - `adult`
  - `old`
- Agents lose energy from metabolism, movement, and brain load.
- Agents die from:
  - energy depletion
  - durability depletion
  - child isolation in severe cases
  - lifespan completion
- Reproduction is gated by:
  - age
  - energy
  - durability
  - adult status
  - nest proximity
  - minimum nest food storage

### Family, Settlement, And Social Systems

- Parent-child lineage tracking is implemented.
- Children track `parent_id`; parents track `children_ids`.
- Bond strength between related agents is implemented.
- Child support logic is implemented.
- Parent/caretaker search and protection behavior is implemented.
- Cooperative groups form dynamically for sufficiently social/cognitive agents.
- Persistent role preference is implemented, including roles such as:
  - `hunter`
  - `gatherer`
  - `protector`
  - `caretaker`
  - `crafter`
  - `planner`
  - `scout`
- Nests are implemented as settlement anchors.
- Nests support:
  - safe radius effects
  - food storage
  - material storage
  - child protection registration

### Memory, Food, Hunting, And Tools

- Memory for danger, food, safe zones, and nest locations is implemented.
- Food processing supports:
  - `raw_plant`
  - `cooked_plant`
  - `raw_meat`
  - `cooked_meat`
- Cooking is implemented as a food-processing bonus rather than a separate station system.
- Large-animal hunting is implemented for coordinated groups.
- Material gathering is implemented with:
  - `wood`
  - `stone`
  - `fiber`
- Tier 1 tools are implemented:
  - `knife`
  - `spear`
  - `sickle`
- Tool durability and tool consumption are implemented.

### Experiment Framework

- The CLI entry point is implemented in [main.py](/C:/artificial-evolution/main.py).
- Three experiment modes are implemented:
  - `prototype`
  - `distinct-search`
  - `massive-lineage`
- Experiment logs and summary artifacts are written to [data](/C:/artificial-evolution/data).
- Historical experiment tracking is implemented in [data/experiment_history.json](/C:/artificial-evolution/data/experiment_history.json).
- Trait-variant expansion around successful templates is implemented in [simulation/runner.py](/C:/artificial-evolution/simulation/runner.py).

## Partially Implemented

### Evolution

- The project has lineage dynamics and survival selection pressure.
- However, there is no fully endogenous mutation-and-selection loop inside the simulation.
- New successful variants are currently expanded externally by search logic in `runner.py`, not produced by inherited mutation during reproduction.

### Emergence Diversity

- The system does produce multiple lineage-capable body types in the final Phase 1 search.
- However, most successful bodies remain concentrated in a very narrow morphology corridor.
- Diversity is currently much stronger in trait-space than in morphology-space.

### Technology And Economy

- Tier 1 tools exist and affect behavior.
- Nest food and material storage exist.
- However, the economy is still shallow:
  - no explicit carrying capacity for nests beyond simple counters
  - no crafted infrastructure upgrades
  - no exchange or trade mechanics
  - no true production chain beyond gather -> store -> craft -> consume

### Cooking And Food Logistics

- Cooking no longer exists as a trait-only energy transformation step.
- Food can become cooked only if external heat exists at the agent location.
- Automatic food sharing and redistribution are disabled in substrate-first runs.
- There is still no complete transport inventory, spoilage, or full production-chain model.

### Hunting And Ecology

- Herd prey, guards, calves, and scattering are implemented.
- However, there is no broader predator-prey ecosystem with multiple competing species and adaptive coevolution.

### Documentation Alignment

- Some documents still describe older prototype scope and should not be treated as the latest system description.
- The codebase currently contains a more advanced settlement/family/trait simulation than [README.md](/C:/artificial-evolution/README.md) and [docs/SIMULATION_ARCHITECTURE.md](/C:/artificial-evolution/docs/SIMULATION_ARCHITECTURE.md) imply.

### Visualization

- Research figures have been generated into [data/figures](/C:/artificial-evolution/data/figures).
- The in-repo visualization module itself is still only a placeholder in [visualization/__init__.py](/C:/artificial-evolution/visualization/__init__.py).

## Planned Only

### True In-Simulation Evolution

- Inherited mutation during reproduction
- Long-run selection across many generations
- Genome or trait mutation as part of the normal birth process
- Emergent diversification without externally generated trait-variant sweeps

### Richer Social Complexity

- Stable communication protocols
- Negotiation, reciprocity, or alliance systems
- Inter-group conflict beyond indirect competition
- Territorial politics or organized warfare

### Richer Economy And Settlement Growth

- Settlement upgrades
- Larger-scale resource specialization
- Multi-step production chains
- Trade and exchange
- Farming or cultivation
- Durable settlement infrastructure

### Richer Ecology

- Multiple prey and predator species
- Disease
- Accumulated injury systems
- More realistic habitat obstacles or terrain types
- Coevolution between ecological niches

### Reproduction Realism

- Sexual reproduction
- Multi-parent inheritance
- More realistic heredity rules

### Runtime Visualization

- Population timelines
- Spatial heatmaps
- Settlement snapshots
- Per-tick replayable traces

## Known Mismatches Between Docs And Code

- [README.md](/C:/artificial-evolution/README.md) understates the current implementation.
- [docs/SIMULATION_ARCHITECTURE.md](/C:/artificial-evolution/docs/SIMULATION_ARCHITECTURE.md) lists several systems as future work even though they already exist.
- [docs/REAL_WORLD_ASSUMPTIONS.md](/C:/artificial-evolution/docs/REAL_WORLD_ASSUMPTIONS.md) mentions effectively non-traversable terrain pressure, but the current `is_walkable()` logic only checks map bounds.
- Some older data files such as [data/prototype_results.json](/C:/artificial-evolution/data/prototype_results.json) and [data/run_log.txt](/C:/artificial-evolution/data/run_log.txt) reflect earlier system states and should not be used as the latest reference without qualification.

## Recommended Source Of Truth

Use these as the primary current references:

- [agents/agent.py](/C:/artificial-evolution/agents/agent.py)
- [agents/body.py](/C:/artificial-evolution/agents/body.py)
- [world/environment.py](/C:/artificial-evolution/world/environment.py)
- [simulation/runner.py](/C:/artificial-evolution/simulation/runner.py)
- [data/experiment_history.json](/C:/artificial-evolution/data/experiment_history.json)
- [data/experiments/experiment_026.md](/C:/artificial-evolution/data/experiments/experiment_026.md)
- [data/experiments/experiment_031.md](/C:/artificial-evolution/data/experiments/experiment_031.md)
- [phase1_report/artificial_evolution_phase1_summary_en.docx](/C:/artificial-evolution/phase1_report/artificial_evolution_phase1_summary_en.docx)
- [phase1_report/artificial_evolution_phase1_summary_th.docx](/C:/artificial-evolution/phase1_report/artificial_evolution_phase1_summary_th.docx)
