# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| `set_sizes` | `task.set_sizes` | `[2, 4, 8]` | `W1990242729`; `W2014448832`; `W2608251392` | Hick varied choice alternatives; Hyman Experiment I varied equally probable alternatives; review pp. 1283–1284 describes the accepted 2–8 range. | direct | Gives 1, 2, and 3 bits. |
| `condition_probability` | block condition weights | `1/N` within each set size | `W2014448832` | Experiment I conditions differed in the number of equally probable alternatives. | direct | Exact balance is possible because 32 is divisible by 2, 4, and 8. |
| `information_bits` | `task.condition_specs.*.information_bits` | `log2(N)` | `W1990242729`; `W2014448832` | Accepted model `RT = a + b log2(N)` / `RT = a + bH`. | direct | Stored on every trial and used in summary regression. |
| `response_mapping` | `task.response_keys`; `task.condition_specs` | positions 1–8 → `A/S/D/F/J/K/L/;` | `W1990242729` | Hick used corresponding lamps and resting-finger response keys. | inferred | Keyboard modernization preserves one-to-one spatial compatibility. |
| `block_order` | `task.block_orders` | all six permutations of 2/4/8 by subject ID | `W2608251392` | Review documents substantial practice effects on the set-size slope. | inferred | Counterbalances practice/order across participants. |
| `trials_per_block` | `task.trial_per_block` | `32` | `W2014448832` | Hyman used long balanced series; the essential requirement is stable, equiprobable alternatives. | inferred | Compact low-cost version; divisible by every N. |
| `fixation_duration` | `timing.fixation_duration_s` | `0.50 s` | `W2014448832` | Hyman used a warning signal before the response stimulus. | inferred | Modern fixed warning/fixation interval. |
| `response_deadline` | `timing.response_timeout_s` | `2.00 s` | `W2014448832` | Historical description presented the selected light for two seconds. | direct-modernized | The stimulus remains until response or deadline. |
| `error_feedback` | `timing.error_feedback_duration_s` | `0.50 s` | `W2608251392` | Review emphasizes accuracy and speed–accuracy considerations. | inferred | Brief corrective feedback supports mapping accuracy. |
| `iti_duration` | `timing.iti_duration_s` | `0.70 s` | `W2608251392` | Discrete-trial choice RT requires separation of successive response events. | inferred | Prevents accidental carryover keypresses. |
| `analysis_model` | summary utility | mean correct RT by N; OLS on `log2(N)` | `W1990242729`; `W2014448832` | Core law states mean RT is linear in average information. | direct | Reports intercept, ms/bit slope, and R². |
| `sequential_fields` | trial data | previous target and repetition flag | `W2608251392` | Review pp. 1289–1290 identifies S–R repetition probability as a set-size confound. | direct | Makes the known limitation auditable. |
