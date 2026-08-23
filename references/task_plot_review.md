# Task Plot Review

## Round 1 — Regenerate

- Evidence match: pass. Rows were 2/4/8 choices with 1/2/3 bits; phase order and 500/2000/700-ms labels matched config and `run_trial.py`.
- Text: pass. All condition, phase, timing, and corrective-feedback labels were readable and correctly spelled.
- Stimulus count: pass. Choice screens contained exactly 2, 4, and 8 outlined circles with one target.
- Layout: pass. No overlaps, clipped labels, malformed arrows, extra devices, or generated branding.
- Scale gate: fail. The 2- and 4-choice outline circles were visibly larger than the 8-choice circles.
- Revision: reduce the 2/4-choice circles to the 8-choice diameter and standardize target-dot diameter/centering while preserving every other element.

## Round 2 — Pass

- Evidence match: pass. All three rows, labels, phase order, response window, and optional error/timeout note match the canonical task.
- Stimulus fidelity: pass. Exactly 2, 4, and 8 equal-diameter outline circles are shown; one black target dot is centered within an outline on each choice screen.
- Ratio/scale: pass. All participant-screen boxes share one aspect ratio and size; circle and target diameters are consistent across rows.
- Readability: pass. Text is clean at document preview size; there is no garbling, clipping, or overlap.
- Temporal layout: pass. Arrows and row separators clearly communicate left-to-right progression without crossing labels or screens.
- Branding: pass after post-processing. The centered title and `Construct:` subtitle occupy the reserved header; the borderless TaskBeacon lockup is in the top-right and does not overlap content.
- Raw preservation: pass. `references/task_plot_timeline_raw.png` contains the pre-branding timeline.
- README embed: pass. `![Task Flow](task_flow.png)` is the first image under `## 2. Task Flow`.

Final decision: accepted after 2 visual rounds (within the user-specified maximum of 5).
