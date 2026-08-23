# Stimulus Mapping

Map each implemented condition/stimulus to the selected literature source.
All values below are resolved for publication.

## Mapping Table

| Condition | Stage/Phase | Stimulus IDs | Participant-Facing Content | Source Paper ID | Evidence (quote/figure/table) | Implementation Mode | Asset References | Notes |
|---|---|---|---|---|---|---|---|---|
| all | instruction | `instruction_text` | Chinese explanation of the 2/4/8 spatial key task and speed-plus-accuracy instruction | `W1990242729`; `W2014448832` | Choice RT requires a unique response to each possible stimulus and low error. | `psychopy_builtin` | `config/config.yaml` | SimHei; config-defined. |
| all | block instruction | `block_instruction_text` | Current set size, information in bits, and active left-to-right key sequence | `W2014448832` | Experiment I manipulated the number of equiprobable alternatives between conditions. | `psychopy_builtin` | `config/config.yaml` | Formatted from scheduled block metadata. |
| all | fixation | `fixation` | Black central plus sign on a light-gray background | `W2014448832` | Warning signal preceded the response stimulus in the historical apparatus. | `psychopy_builtin` | `config/config.yaml` | Fixed 500 ms modern warning display. |
| `n2_p4`, `n2_p5` | choice response | `outline_4`, `outline_5`, `target_4`/`target_5` | Two outlined central positions; one position filled black | `W1990242729`; `W2014448832` | Compact light locations each mapped to a unique response; two equiprobable alternatives = 1 bit. | `psychopy_builtin` | `config/config.yaml` | Keys F/J; no key labels appear during RT measurement. |
| `n4_p3`, `n4_p4`, `n4_p5`, `n4_p6` | choice response | `outline_3` through `outline_6`; matching target | Four outlined central positions; one position filled black | `W1990242729`; `W2014448832` | Four equiprobable S–R alternatives = 2 bits. | `psychopy_builtin` | `config/config.yaml` | Keys D/F/J/K. |
| `n8_p1`, `n8_p2`, `n8_p3`, `n8_p4`, `n8_p5`, `n8_p6`, `n8_p7`, `n8_p8` | choice response | `outline_1` through `outline_8`; matching target | Eight outlined positions spanning the central row; one position filled black | `W1990242729`; `W2014448832` | Hyman used up to eight light locations; eight equiprobable alternatives = 3 bits. | `psychopy_builtin` | `config/config.yaml` | Keys A/S/D/F/J/K/L/;. |
| all incorrect | error feedback | `error_feedback_text` / `timeout_feedback_text` | Chinese corrective message naming the correct key and, when present, the pressed key | `W2608251392` | Accuracy must be tracked because speed–accuracy policy changes RT interpretation. | `psychopy_builtin` | `config/config.yaml` | Only appears after error or timeout. |
| all | ITI | `fixation` | Central plus sign | `W2608251392` | Sequential dependencies are a known issue in discrete choice RT. | `psychopy_builtin` | `config/config.yaml` | Fixed 700 ms separation. |
| all | summary | `block_break_text`, `good_bye_text` | Accuracy, mean correct RT, and final RT-vs-bit slope/R² | `W1990242729`; `W2014448832` | Core dependent relation is mean RT as a linear function of information. | `psychopy_builtin` | `config/config.yaml` | Summary formatting only; not part of trial RT. |

Accepted implementation modes:
- `psychopy_builtin`
- `generated_reference_asset`
- `licensed_external_asset`

Decision rule:
- Participant-facing text should be configured in `config/*.yaml` stimuli and referenced via stimulus IDs.
