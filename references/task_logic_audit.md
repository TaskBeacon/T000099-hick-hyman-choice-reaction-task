# Hick–Hyman Choice Reaction Task Logic Audit

## 1. Paradigm Intent

- Task: Hick–Hyman Choice Reaction Task.
- Primary construct: response-selection time as a function of stimulus–response uncertainty.
- Manipulated factors: number of equiprobable stimulus–response alternatives (`N = 2, 4, 8`; `1, 2, 3` bits).
- Dependent measures: correct-trial reaction time, accuracy, timeout rate, and the participant-level slope/intercept of mean correct RT regressed on `log2(N)`.
- Key citations: Hick (1952; `W1990242729`), Hyman (1953; `W2014448832`), Proctor and Schneider (2018; `W2608251392`), and Tajima et al. (2019; `W2965135644`).
- Paradigm boundary: this is a discrete choice-reaction task. It is not a vigilance task (one repeated detection response) and it does not manipulate pointing distance or target width as in Fitts' law.

## 2. Block/Trial Workflow

### Block Structure

- Total blocks: three scored blocks, one each for 2, 4, and 8 alternatives.
- Trials per block: 32, yielding 96 scored trials. Thirty-two is divisible by every set size, permitting exact equiprobability at each level.
- Randomization/counterbalancing: the six permutations of `[2, 4, 8]` are assigned by subject ID modulo six. Within a block, target-position labels are generated in randomized order with equal weights.
- Condition weight policy: each active target position is equally weighted within its set-size block. `task.condition_weights` is omitted because each block supplies an equal-weight subset to `BlockUnit.generate_conditions(...)`.
- Condition generation method: built-in `BlockUnit.generate_conditions(...)`. The labels passed into `run_trial.py` are keys into the config-defined `task.condition_specs` mapping.
- Runtime-generated trial values: none of the experimental factors are sampled in `run_trial.py`. Block set size is selected before block construction, and each target-position condition is scheduled by `BlockUnit` under the task seed.

### Trial State Machine

1. `fixation`
   - Onset trigger: `fixation_onset`.
   - Stimuli shown: a black central `+` on a light neutral background.
   - Duration: 500 ms.
   - Valid keys: none.
   - Next state: `choice_response`.
2. `choice_response`
   - Onset trigger: set-size-specific target trigger.
   - Stimuli shown: the active set of 2, 4, or 8 outlined circles and one black filled target circle at the chosen location.
   - Valid keys: the eight configured response keys are monitored so wrong active or inactive-key presses are recorded rather than silently ignored.
   - Timeout behavior: no response after 2,000 ms is recorded as a timeout.
   - Next state: `error_feedback` after an error/timeout, otherwise `iti`.
3. `error_feedback` (conditional)
   - Onset trigger: `error_feedback_onset`.
   - Stimuli shown: config-formatted Chinese feedback naming the correct key; for an incorrect response it also names the pressed key, and for a timeout it reports that no response was detected.
   - Duration: 500 ms.
   - Valid keys: none.
   - Next state: `iti`.
4. `iti`
   - Onset trigger: `iti_onset`.
   - Stimuli shown: central fixation cross.
   - Duration: 700 ms.
   - Valid keys: none.
   - Next state: next trial or block summary.

Historical evidence: Hick used compact lamps with fingers resting on corresponding keys and varied the number of alternatives; Hyman varied equiprobable alternatives and showed RT to be linear in information. The 2/4/8 restriction follows the range for which modern reviews describe the canonical linear pattern and matches the requested low-cost keyboard implementation.

## 3. Condition Semantics

- `n2_p4`, `n2_p5`: two-choice trials using the two innermost positions and keys `F/J`; each target has probability 1/2 and information 1 bit.
- `n4_p3`, `n4_p4`, `n4_p5`, `n4_p6`: four-choice trials using the central four positions and keys `D/F/J/K`; each target has probability 1/4 and information 2 bits.
- `n8_p1` through `n8_p8`: eight-choice trials using all positions and keys `A/S/D/F/J/K/L/;`; each target has probability 1/8 and information 3 bits.
- Participant-facing text source: instructions, block reminders, feedback templates, circle outlines, targets, and fixation are all defined in `config/*.yaml`.
- Auditability: `task.condition_specs` maps every condition token to `set_size`, `information_bits`, `target_position`, `correct_key`, `active_outline_ids`, and `target_stim_id`.
- Localization strategy: participant wording and fonts are config-only; changing language does not require edits to `src/run_trial.py`.

## 4. Response and Scoring Rules

- Response mapping: left-to-right positions 1–8 map to `A, S, D, F, J, K, L, ;`.
- Response key source: `task.response_keys` and `task.condition_specs` in config.
- Missing-response policy: a 2,000 ms timeout is incorrect and included in timeout-rate summaries, but excluded from correct-RT regression.
- Correctness logic: first captured key equals the condition's `correct_key`.
- Reward/penalty updates: none.
- Running metrics: per block, accuracy and mean correct RT; at task end, overall accuracy plus mean correct RT for 2/4/8 choices and ordinary least-squares intercept, slope in ms/bit, and `R²` when all three means exist.
- Sequential audit fields: previous target, whether the target repeated, and trial position are stored because repetition frequency changes with set size under equiprobable random sampling.

## 5. Stimulus Layout Plan

- Screen name: `choice_response`.
- Stimulus IDs shown together: one subset of `outline_1` through `outline_8` plus one `target_1` through `target_8`.
- Layout anchors: x coordinates `[-525, -375, -225, -75, 75, 225, 375, 525]` px at y `0`; the 2-choice set uses positions 4/5 and the 4-choice set uses positions 3–6.
- Size/spacing: outline radius 48 px; target radius 32 px; adjacent centers are 150 px apart. On a 1280×800 window the outer circles remain inside the viewport with 67 px side margins.
- Readability/overlap checks: target circles fit inside outlines with 16 px radial clearance; no simultaneous text is displayed on the target screen; instruction and block-reminder text use explicit `pos`, `height`, and `wrapWidth`.
- Rationale: a compact position array preserves the classic lamp-to-response mapping while avoiding the long pointer movement central to Fitts-style tasks.

## 6. Trigger Plan

- Experiment/session: `experiment_start=1`, `experiment_end=99`.
- Blocks: `block_start=10`, `block_end=19`.
- Trial: `trial_start=20`, `fixation_onset=21`.
- Targets: `target_n2=32`, `target_n4=34`, `target_n8=38`.
- Responses: `response_a=41`, `response_s=42`, `response_d=43`, `response_f=44`, `response_j=45`, `response_k=46`, `response_l=47`, `response_semicolon=48`, `response_timeout=49`.
- Post-response: `error_feedback_onset=50`, `iti_onset=60`.
- Participant screens: `instruction_onset=70`, `block_instruction_onset=71`, `block_break_onset=72`, `good_bye_onset=73`.

## 7. Architecture Decisions (Auditability)

- `main.py` runtime flow style: one explicit mode-aware flow that resolves block order, generates equal-weight conditions for the current set size, calls `run_trial`, and shows block/session summaries.
- `utils.py` used: yes, only for subject-based block-order counterbalancing and pure RT summaries/regression.
- Custom controller used: no; the task has no adaptive rule.
- Legacy/backward-compatibility fallback logic required: no.
- Trial identity, timing, response events, and phase persistence remain owned by PsyFlow (`next_trial_id`, `StimUnit`, `set_trial_context`, and `to_dict`).

## 8. Inference Log

- Decision: modern keyboard mapping `A/S/D/F/J/K/L/;` replaces physical Morse keys or vocal pseudowords.
  - Why inference was required: the historical apparatus is not suitable for a low-cost computer task.
  - Citation-supported rationale: Hick used one resting finger per response key, while Hyman used unique responses per stimulus; the implementation preserves the one-to-one spatial S–R mapping.
- Decision: use only 2/4/8 alternatives.
  - Why inference was required: the classic studies tested wider sets, but the requested task calls for 2/4/8.
  - Citation-supported rationale: Proctor and Schneider describe 2–8 as the canonical range in which the linear relationship is typically observed.
- Decision: use 32 trials per block, 500 ms fixation, 2,000 ms response deadline, 500 ms error feedback, and 700 ms ITI.
  - Why inference was required: classic timing depended on electromechanical apparatus and extensive sessions.
  - Citation-supported rationale: the timing preserves a discrete warning/target/response cycle while keeping the deadline above typical choice RT and the compact task mechanism-complete.
- Decision: random equal-weight trial order is used and repetition status is logged.
  - Why inference was required: perfectly matching repetition probability across 2/4/8 would introduce different sequential predictability or require substantially longer blocks.
  - Citation-supported rationale: the review identifies S–R repetition probability as a known Hick-law consideration, so it is made explicit for analysis rather than hidden.
