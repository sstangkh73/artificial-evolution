# ODD Model Description — Draft

**Model:** Artificial Evolution temporal-toxicity foraging study

**ODD version followed:** Grimm et al. (2020), https://doi.org/10.18564/jasss.4259

**Status:** structure only; every placeholder must be completed and checked against the frozen code before submission.

## 1. Purpose and patterns

Describe the narrow purpose of the model, the patterns used to evaluate fitness for purpose, and the claims the model cannot support.

Required patterns:

- safe-versus-toxic encounter rates by true food age
- learned value by representation key
- lifespan/RMST and cause of death
- toxin exposure and damage
- resource availability and starvation

## 2. Entities, state variables, and scales

Document agents, food resources, plants, grid cells, the environment, simulation ticks, spatial scale, and every state variable that enters the E1–E6 mechanisms.

**[Insert machine-checked state-variable table with source-file pointers.]**

## 3. Process overview and scheduling

State the exact within-tick order for sensing, movement, encounters, food choice, ingestion, value updating, toxin effects, maintenance, aging, death, plant dynamics, and telemetry.

**[Generate from the frozen run-loop implementation; do not infer ordering from function names.]**

## 4. Design concepts

### Basic principles

Explain outcome-grounded food-value learning, temporal toxicity, and the resource trade-off.

### Emergence

Identify which behavioral and survival patterns emerge from interactions and which behaviors are supplied directly by the experimenter.

### Adaptation and objectives

State that the within-lifetime value rule is fixed and that no optimal policy is claimed.

### Learning

Give the update equation, learning rate, initialization/first-taste rule, pickiness threshold, and B1/B2/B3 key definitions.

### Prediction, sensing, and interaction

Document the information available to each arm. Food age is supplied to B2; agents do not discover it.

### Stochasticity

List all random draws, RNG streams, seed propagation, and any deterministic sham-key mapping.

### Observation

Define every manuscript outcome and how agent-level values are aggregated to the run/seed inferential unit.

## 5. Initialization

Provide the complete initialization table for world, agents, plants, foods, body plan, genes, founder variation, and RNG state.

## 6. Input data

State whether external data are used. Describe all experiment specifications as controlled model inputs.

## 7. Submodels

Provide equations and implementation references for:

- gross and realized food energy, including integer rounding order
- toxin potency as a function of food age
- tolerance, acute energy penalty, chronic damage, and death
- food-value learning and choice
- B3 sham-key construction
- plant/resource renewal and decay
- maintenance, aging, starvation, and censoring

## Verification and validation supplement

Separate code verification from model validation:

- unit and regression tests
- frozen-spec/provenance guards
- controlled mechanism tests
- full-ecology calibration criteria
- regime transfer and sensitivity analyses
- known mismatches between the model and biological foraging
