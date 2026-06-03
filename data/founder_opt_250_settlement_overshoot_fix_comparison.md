# Founder 250 Settlement Overshoot Fix Comparison

- Body: sensor=0, muscle=0, armor=1, brain=3, profile=nurturing_settler
- Seeds: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
- Population: 250

## Aggregate comparison

- Baseline mean_max_generation: 6.6
- Household redesign mean_max_generation: 5.8
- Settlement fix mean_max_generation: 1.0
- Settlement delta vs baseline: -5.6
- Settlement delta vs redesign: -4.8
- Baseline mean_final_tick: 594.9
- Household redesign mean_final_tick: 589.7
- Settlement fix mean_final_tick: 120.2
- Baseline mean_matured_children: 108.5
- Household redesign mean_matured_children: 106.4
- Settlement fix mean_matured_children: 1.4
- Baseline gen>=7 runs: 6/10
- Household redesign gen>=7 runs: 4/10
- Settlement fix gen>=7 runs: 0/10
- Baseline non-extinct runs: 6/10
- Household redesign non-extinct runs: 5/10
- Settlement fix non-extinct runs: 0/10

## Best runs

- Baseline: seed=11, gen=10, tick=742, births=221, matured=145
- Household redesign: seed=11, gen=9, tick=863, births=254, matured=177
- Settlement fix: seed=13, gen=1, tick=201, births=125, matured=4

## Per-seed settlement-fix runs

- seed=7 gen=1 final_tick=133 births=125 matured=1 extinct=True
- seed=8 gen=1 final_tick=75 births=125 matured=0 extinct=True
- seed=9 gen=1 final_tick=133 births=125 matured=2 extinct=True
- seed=10 gen=1 final_tick=174 births=125 matured=1 extinct=True
- seed=11 gen=1 final_tick=64 births=125 matured=1 extinct=True
- seed=12 gen=1 final_tick=111 births=125 matured=2 extinct=True
- seed=13 gen=1 final_tick=201 births=125 matured=4 extinct=True
- seed=14 gen=1 final_tick=72 births=125 matured=2 extinct=True
- seed=15 gen=1 final_tick=133 births=125 matured=0 extinct=True
- seed=16 gen=1 final_tick=106 births=125 matured=1 extinct=True