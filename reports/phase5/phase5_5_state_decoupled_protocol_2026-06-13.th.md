# Protocol: Phase 5.5 State-Decoupled Seed Handling

วันที่: 2026-06-13

## Objective

แยกพฤติกรรม seed handling ออกจาก `hunger state` ให้ชัดกว่า Phase 5.4 โดยไม่สอน agent ว่า seed ใช้ปลูก

ผล Phase 5.4 พบว่า:

- baseline hunger-context fraction = `0.97644`
- hunger-neutral hunger-context fraction = `0.98168`
- site-selection pass = `0/5` ทุก condition
- food chain เกิดจริง แต่ future-path lift อย่างเดียวไม่พอจะตีความเป็น farming

ดังนั้น Phase 5.5 จะทดสอบว่า agent มี seed-placement agency เมื่อไม่ถูก hunger state ครอบหรือไม่

## Research Question

agent วาง seed เพราะเลือกตำแหน่งจริง หรือแค่ถือ seed ระหว่างเดินหาอาหารแล้วบังเอิญ drop

## Hypotheses

H5.5a: ถ้า seed placement เป็นพฤติกรรมที่ agent ควบคุมได้ condition ที่ลด critical-hunger drop หรือบังคับ safe-window drop ควรเพิ่ม safe/balanced drop fraction และเพิ่ม quality lift เทียบกับ current/recovery controls

H5.5b: ถ้า seed placement เป็นผลข้างเคียงของ hunger pathing การบล็อก critical hunger drop จะลด activity หรือทำให้ lift ไม่ดีขึ้น และ reward-memory ablations จะไม่เปลี่ยนผลมาก

## Independent Variables

- `seed_hunger_drop_bonus`
- `seed_drop_block_critical_hunger`
- `seed_drop_safe_window_only`
- `learning_reward_memory_limit`
- `reward_memory_shuffle_radius`

## Dependent Variables

- `agent_moved_drop_count`
- `safe_or_balanced_drop_fraction`
- `hunger_drop_fraction`
- `drop_quality_vs_current_position_lift`
- `drop_quality_vs_hunger_recovery_position_lift`
- `drop_quality_vs_safe_window_position_lift`
- `drop_quality_vs_visible_control_lift`
- `high_quality_completed_chain_rate`
- `low_quality_completed_chain_rate`
- `late_vs_early_drop_quality_lift`

## Controls

Primary controls:

1. current-position control
2. hunger-recovery-position control
3. safe-window-position control
4. visible control
5. nearby control
6. future-path control as diagnostic only

Reward controls:

- memory disabled
- memory shuffled

## Conditions

Core:

1. `baseline_100x100`
2. `no_hunger_seed_drop_bonus_100x100`
3. `critical_hunger_drop_blocked_100x100`
4. `safe_window_seed_drop_only_100x100`

Diagnostics:

5. `reward_memory_disabled_100x100`
6. `reward_memory_shuffled_100x100`

## Success Criteria

Phase 5.5 passes if at least one state-decoupled condition has:

- mean moved drops >= 50
- safe/balanced drop fraction higher than baseline by >= 0.05
- at least 3/5 seeds pass:
  - current-position lift > 1.10
  - recovery-position lift > 1.05 when recovery samples exist
  - visible lift > 1.00
  - high-quality chain rate > low-quality chain rate
  - late/early lift >= 1.05
- directional consistency at least 4/5 seeds

## Failure Criteria

Fail if any of these hold:

- hunger fraction remains near baseline
- activity collapses below usable sample size
- current/recovery/visible controls do not improve
- high-quality chain does not outperform low-quality chain
- reward-memory disabled/shuffled conditions look the same as baseline

## Interpretation Rules

- future-path lift alone must never pass the phase
- if safe-window-only increases safe drops but quality does not improve, interpret as state decoupling without site selection
- if critical-hunger blocking collapses activity, seed handling is currently dependent on hunger loop
- if reward shuffling does not change results, do not claim memory-driven learning

## Expected Output

- `data\phase5_5_state_decoupled_*`
- `reports\phase5_5_state_decoupled_confirm01_2026-06-13.th.md`
- `reports\phase5_5_state_decoupled_analysis_2026-06-13.th.md`
