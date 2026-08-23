# CHANGELOG

All notable changes to T000099 are documented here.

## [0.1.0] - 2026-08-24

### Added

- Added the literature-audited Hick–Hyman 2/4/8-choice keyboard task.
- Added exact equiprobable target scheduling, subject-based block-order counterbalancing, and position–key mapping.
- Added fixation, choice response, conditional corrective feedback, and ITI phases through PsyFlow primitives.
- Added trial-level information, repetition, correctness, timeout, and response-time fields.
- Added per-set-size RT summaries and participant-level Hick slope/intercept/R².
- Added human, QA, scripted-simulation, and sampler-simulation configs plus task-aware responders.
- Added reference, parameter, stimulus, and paradigm-logic audit artifacts.

### Changed

- Modernized the historical lamp/key apparatus as a compact eight-position keyboard display while preserving one-to-one spatial stimulus–response mappings.

### Fixed

- Included the continuation key in the QA allowed-key contract and aligned all smoke profiles with their required mode sections.
