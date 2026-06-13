# Concept Proposal

## 1) Project Title

**Studying Experience-Based Knowledge Emergence in Artificial Agents Placed in a Novel Simulated World**

Project category: Applied Science

Keywords: Artificial Life, Agent-Based Simulation, World Discovery, Experience-Based Learning, Emergent Ecological Interaction, Emergent Behavior

---

## 2) Team Members

Team Leader

Name: Mr. Chitsanuphong Inchan (นายชิษณุพงศ์ อินทร์จันทร์)

Grade: Mathayom 4, Deebuk Phangnga Wittayayon School

Advisor

Name: Mr. Baphit Mangkala (นายบพิธ มังคะลา)

School: Deebuk Phangnga Wittayayon School

Affiliation: Secondary Educational Service Area Office Phangnga Phuket Ranong

---

## 3) Background and Rationale

The starting point of this project is a question about artificial intelligence from a different angle: if an artificial agent is placed in a new world without ready-made explanations, without human-provided datasets, and without instructions about what each object is for, how far can the agent build knowledge from direct experience in that world? In this project, the term "agent" refers to a computational simulation agent with basic behavior and memory, not a large language model. The question connects computer science, cognitive science, and Artificial Life because it asks whether interaction between an agent and its environment can produce measurable behavioral patterns.

The project therefore builds an Artificial Life simulation to study whether agents that are not taught the meanings of "seed", "plant", "farm", or "technology" can develop behavior that resembles environmental knowledge. The simulated world contains limited resources, agent energy, plants, seeds, moisture, light, temperature, soil nutrients, and basic actions such as moving, eating, remembering food locations, picking up seeds, and dropping seeds. The study avoids over-interpreting the agents as "understanding" or "intentionally farming" until the relevant metrics and controls provide enough evidence.

The interesting point of the project is that it does not start by teaching the agent how to solve the problem. Instead, it starts by building a world with basic rules that are rich enough for causal relationships to exist, then tests whether the agent's experience in that world changes its behavior. This separates two important questions: 1) whether the world contains learnable signals, and 2) whether the agent can use those signals to produce useful behavior.

Preliminary experiments in the project provide data-based evidence that the system is ready for studying world-based learning, while still requiring careful interpretation:

| Phase | Test Question | Main Finding |
|---|---|---|
| Phase 1 | Is the `seed -> plant -> fruit -> consumed` cycle stable enough in the simulated world? | Passed 5/5 seeds; plants fruited and plant-derived food was consumed in every seed |
| Phase 2 | Does the agent return to plant-food reward locations more often than expected by chance? | Passed 3/3 seeds; mean owner return lift = 41.7027 |
| Phase 3 | Can seeds moved by agents enter the plant cycle and later produce food? | Passed 3/3 seeds; mean completed chain from moved seeds = 16.3333 per run |
| Phase 4 | Can repeated agent seed drops form productive ecological interaction patches? | Passed 5/5 seeds; mean patch productivity lift = 5.8216, with no scaffold contamination detected |
| Phase 5.1 | Does the agent choose better seed-drop locations than control conditions? | Not yet passed; the 100x100 baseline passed 0/5 seeds in the core gate |

Based on this evidence, the appropriate current conclusion is that the system has not yet demonstrated that the agent understands cultivation, chooses seed-drop locations better than controls, or intentionally creates technology. However, it does show preliminary evidence of location-based learning, causal participation in the plant lifecycle, and emergent ecological interaction that repeatedly produces food in the simulated world. This provides a suitable basis for asking whether experience-based knowledge can later develop toward site selection, behavioral transmission, and early forms of technology.

Main research question:

**If artificial agents are placed in a novel simulated world without being taught the meanings of objects or the uses of resources in advance, can they build knowledge from direct experience and produce causal behaviors such as returning to food sources, moving seeds, and generating productive ecological interactions?**

---

## 4) Objectives

1. To develop and use an Artificial Life simulated world for studying agent learning from direct experience in an environment without predefined knowledge.

2. To test whether agents can show reward-place learning, meaning a tendency to return to locations where plant-derived food was previously obtained, more often than control conditions.

3. To test whether seeds moved by agents can enter the biological cycle `seed -> plant -> fruit -> consumed` and later produce causal outcomes.

4. To evaluate whether areas formed by repeated agent seed drops produce more food than control areas, without interpreting this as site selection or intentional cultivation until stronger controls are passed.

5. To build metrics and controls that help separate "behavior that looks like learning" from "effects caused by food density, repeated movement paths, or environmental attraction."

Research hypothesis:

**Agents that are not taught the meanings of objects in the simulated world may still develop behavior resembling environmental knowledge if the world contains sufficiently stable causal cycles, such as plant-derived food, reward locations, seeds, germination, and delayed outcomes. However, claims that agents "understand" or "intentionally cultivate" must pass stronger controls than simply observing production or return behavior.**

---

## 5) Conceptual Framework

Conceptual framework diagram:

```text
Novel simulated world without predefined meanings
        |
        v
Basic world rules
(energy, plants, seeds, light, water, temperature, soil, food)
        |
        v
Agent-world interaction
(move, eat, remember locations, pick/drop seeds)
        |
        v
Experience-based knowledge metrics
(return lift, seed causal chain, patch productivity)
        |
        v
Control tests
(current-position, nearby, visible, random, low-food signal, world-size stress)
        |
        v
Evidence-bounded conclusion
(emergent ecological interaction / not yet intentional farming or full technology)
```

Independent variables:

- Simulated world conditions, such as world size, food density, food-signal strength, and initial population size
- Agent behavior and state conditions, such as food-location memory, seed pickup or drop behavior, and hunger state
- Control conditions, such as low-food-signal condition, current-position control, nearby control, visible control, and world-size stress test

Dependent variables:

- Amount of plant-lifecycle food consumed by agents
- Return rate to previous reward locations compared with baseline or control conditions
- Number of seeds moved by agents that enter the cycle and later produce food
- Number of repeated productive patches and productivity lift compared with controls
- Site-selection lift values, such as current-position lift, nearby lift, visible lift, and late-vs-early lift

Controlled variables:

- Seeds used for repeated runs
- Number of ticks or run duration per experiment
- Basic plant-lifecycle rules and world physics in each experiment set
- Removal of scaffolds that could provide ready-made answers, such as instructions that tell agents to plant crops or build farms

Summary of method:

1. Build a simulated world with a plant lifecycle and basic resources, without giving agents ready-made instructions that seeds or plants should be used for cultivation.
2. Run multiple random seeds to confirm that the world contains learnable signals, such as plants producing fruit and agents consuming plant-derived food.
3. Measure location-based learning by observing whether agents leave food areas and later return near previous reward locations.
4. Track seed IDs to test whether seeds moved by agents can germinate, grow, fruit, and become food that is later consumed.
5. Test whether repeated seed dropping forms patches with higher productivity than control areas.
6. Use stronger controls to examine whether patches or returns to previous locations are caused by learning, or instead by food hotspots, social corridors, world size, or hunger pressure.

---

## 6) Expected Benefits

1. A computational model for studying how far artificial agents can build knowledge from a new world without receiving ready-made explanations.

2. Metrics for separating behavior that is merely an environmental side effect from behavior with evidence of experience-based learning, such as return lift, causal seed chain, patch productivity, and site-selection controls.

3. A cautious experimental approach that identifies supporting evidence, counter-evidence, and limitations for each claim.

4. A foundation for future studies of social learning, information transfer, communication, and early technology in simulated worlds, starting from verifiable evidence rather than assuming that agents already understand their world.

5. Practical research experience across the full process: forming a research question, designing a simulated world, defining variables, running multiple seeds, using controls to falsify hypotheses, and reporting conclusions without exceeding the evidence.
