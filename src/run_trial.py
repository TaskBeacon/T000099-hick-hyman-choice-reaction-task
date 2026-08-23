from __future__ import annotations

import json
from typing import Any

from psyflow import StimUnit, next_trial_id, set_trial_context


def _trigger(settings: Any, name: str) -> int | None:
    triggers = getattr(settings, "triggers", {}) or {}
    return triggers.get(name) if hasattr(triggers, "get") else None


def _unit(
    *,
    win,
    kb,
    trigger_runtime,
    label: str,
    trial_id: int,
    block_id: str,
    condition_id: str,
    deadline_s: float,
    valid_keys: list[str],
    task_factors: dict[str, Any],
    stim_id: str,
) -> StimUnit:
    unit = StimUnit(label, win, kb, runtime=trigger_runtime)
    set_trial_context(
        unit,
        trial_id=trial_id,
        phase=label,
        deadline_s=deadline_s,
        valid_keys=valid_keys,
        block_id=block_id,
        condition_id=condition_id,
        task_factors=task_factors,
        stim_id=stim_id,
    )
    return unit


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    trigger_runtime,
    block_id=None,
    block_idx=None,
    set_size=None,
    sequence_state=None,
):
    """Run one config-defined equiprobable spatial choice trial."""

    condition_id = str(condition)
    condition_specs = dict(getattr(settings, "condition_specs", {}) or {})
    if condition_id not in condition_specs:
        raise KeyError(f"Unknown Hick–Hyman condition: {condition_id}")
    spec = dict(condition_specs[condition_id])

    trial_id = int(next_trial_id())
    block_index = int(block_idx if block_idx is not None else 0)
    block_id_value = str(block_id or f"block_{block_index + 1:02d}")
    set_size_value = int(spec["set_size"])
    if set_size is not None and int(set_size) != set_size_value:
        raise ValueError(f"Condition {condition_id} does not belong to N={set_size}")

    target_position = int(spec["target_position"])
    correct_key = str(spec["correct_key"]).lower()
    active_outline_ids = [str(value) for value in spec["active_outline_ids"]]
    target_stim_id = str(spec["target_stim_id"])
    response_keys = [str(key).lower() for key in list(getattr(settings, "response_keys", []))]
    fixation_duration_s = float(getattr(settings, "fixation_duration_s"))
    response_timeout_s = float(getattr(settings, "response_timeout_s"))
    error_feedback_duration_s = float(getattr(settings, "error_feedback_duration_s"))
    iti_duration_s = float(getattr(settings, "iti_duration_s"))

    previous_target = None if sequence_state is None else sequence_state.get("previous_target_position")
    task_factors = {
        "set_size": set_size_value,
        "information_bits": float(spec["information_bits"]),
        "stimulus_probability": float(spec["stimulus_probability"]),
        "target_position": target_position,
        "correct_key": correct_key,
        "active_keys": [str(value).lower() for value in spec["active_keys"]],
        "previous_target_position": previous_target,
        "is_repetition": previous_target == target_position if previous_target is not None else False,
    }
    trial_data: dict[str, Any] = {
        "trial_id": trial_id,
        "block_id": block_id_value,
        "block_idx": block_index,
        "condition_id": condition_id,
        **task_factors,
    }
    trigger_runtime.send(_trigger(settings, "trial_start"))

    fixation = _unit(
        win=win,
        kb=kb,
        trigger_runtime=trigger_runtime,
        label="fixation",
        trial_id=trial_id,
        block_id=block_id_value,
        condition_id=condition_id,
        deadline_s=fixation_duration_s,
        valid_keys=[],
        task_factors=task_factors,
        stim_id="fixation",
    )
    fixation.add_stim(stim_bank.get("fixation")).show(
        duration=fixation_duration_s,
        onset_trigger=_trigger(settings, "fixation_onset"),
    ).to_dict(trial_data)

    choice = _unit(
        win=win,
        kb=kb,
        trigger_runtime=trigger_runtime,
        label="choice_response",
        trial_id=trial_id,
        block_id=block_id_value,
        condition_id=condition_id,
        deadline_s=response_timeout_s,
        valid_keys=response_keys,
        task_factors=task_factors,
        stim_id="+".join([*active_outline_ids, target_stim_id]),
    )
    for outline_id in active_outline_ids:
        choice.add_stim(stim_bank.get(outline_id))
    choice.add_stim(stim_bank.get(target_stim_id)).capture_response(
        keys=response_keys,
        duration=response_timeout_s,
        onset_trigger=_trigger(settings, f"target_n{set_size_value}"),
        response_trigger={
            key: _trigger(settings, "response_semicolon" if key == ";" else f"response_{key}")
            for key in response_keys
        },
        timeout_trigger=_trigger(settings, "response_timeout"),
        terminate_on_response=True,
        correct_keys=[correct_key],
    ).to_dict(trial_data)

    response_key = choice.get_state("response", None)
    response_rt_s = choice.get_state("response_time", None)
    response_correct = response_key == correct_key
    response_timeout = response_key is None
    phase_sequence = ["fixation", "choice_response"]

    if not response_correct:
        feedback_id = "timeout_feedback_text" if response_timeout else "error_feedback_text"
        values = {"pressed_key": "无" if response_key is None else str(response_key).upper(), "correct_key": correct_key.upper()}
        feedback = _unit(
            win=win,
            kb=kb,
            trigger_runtime=trigger_runtime,
            label="error_feedback",
            trial_id=trial_id,
            block_id=block_id_value,
            condition_id=condition_id,
            deadline_s=error_feedback_duration_s,
            valid_keys=[],
            task_factors=task_factors,
            stim_id=feedback_id,
        )
        feedback.add_stim(stim_bank.get_and_format(feedback_id, **values)).show(
            duration=error_feedback_duration_s,
            onset_trigger=_trigger(settings, "error_feedback_onset"),
        ).to_dict(trial_data)
        phase_sequence.append("error_feedback")

    iti = _unit(
        win=win,
        kb=kb,
        trigger_runtime=trigger_runtime,
        label="iti",
        trial_id=trial_id,
        block_id=block_id_value,
        condition_id=condition_id,
        deadline_s=iti_duration_s,
        valid_keys=[],
        task_factors=task_factors,
        stim_id="fixation",
    )
    iti.add_stim(stim_bank.get("fixation")).show(
        duration=iti_duration_s,
        onset_trigger=_trigger(settings, "iti_onset"),
    ).to_dict(trial_data)
    phase_sequence.append("iti")

    trial_data.update(
        {
            "response_key": response_key,
            "response_rt_s": response_rt_s,
            "response_correct": response_correct,
            "response_timeout": response_timeout,
            "target_hit": int(response_correct),
            "target_rt": response_rt_s,
            "phase_sequence_json": json.dumps(phase_sequence),
            "phase_count": len(phase_sequence),
        }
    )
    if sequence_state is not None:
        sequence_state["previous_target_position"] = target_position
    return trial_data


__all__ = ["run_trial"]
