from __future__ import annotations

from contextlib import nullcontext
from functools import partial
from pathlib import Path
from typing import Any

import pandas as pd
from psychopy import core
from psyflow import (
    BlockUnit,
    StimBank,
    StimUnit,
    SubInfo,
    TaskSettings,
    context_from_config,
    initialize_exp,
    initialize_triggers,
    load_config,
    parse_task_run_options,
    reset_trial_counter,
    runtime_context,
    set_trial_context,
)

from src import resolve_block_order, run_trial, summarize_trials


MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_scripted_sim.yaml",
}


def _continue_screen(
    *,
    win,
    kb,
    stim_bank,
    trigger_runtime,
    settings,
    label: str,
    stim_id: str,
    values: dict[str, Any] | None = None,
    terminate: bool = False,
) -> None:
    unit = StimUnit(label, win, kb, runtime=trigger_runtime)
    set_trial_context(
        unit,
        trial_id=label,
        phase=label,
        deadline_s=None,
        valid_keys=["space"],
        block_id=label,
        condition_id=label,
        task_factors={"screen": label, **(values or {})},
        stim_id=stim_id,
    )
    trigger_runtime.send(settings.triggers.get(f"{label}_onset"))
    stimulus = stim_bank.get_and_format(stim_id, **values) if values else stim_bank.get(stim_id)
    unit.add_stim(stimulus).wait_and_continue(keys=["space"], min_wait=0.0, terminate=terminate)


def run(options) -> None:
    task_root = Path(__file__).resolve().parent
    config = load_config(str(options.config_path))
    context, output_dir, scope = None, None, nullcontext()
    if options.mode in ("qa", "sim"):
        context = context_from_config(task_dir=task_root, config=config, mode=options.mode)
        output_dir, scope = context.output_dir, runtime_context(context)

    with scope:
        if options.mode == "qa":
            subject = {"subject_id": 101}
        elif options.mode == "sim":
            subject = {"subject_id": str(context.session.participant_id or "sim099")}
        else:
            subject = SubInfo(config["subform_config"]).collect()

        settings = TaskSettings.from_dict(config["task_config"])
        settings.add_subinfo(subject)
        if output_dir is not None:
            settings.save_path = str(output_dir)
        if options.mode == "qa" and output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            settings.res_file = str(output_dir / "qa_trace.csv")
            settings.log_file = str(output_dir / "qa_psychopy.log")
            settings.json_file = str(output_dir / "qa_settings.json")
        settings.triggers = config["trigger_config"]
        settings.save_to_json()

        trigger_runtime = initialize_triggers(mock=True) if options.mode in ("qa", "sim") else initialize_triggers(config)
        win, kb = initialize_exp(settings)
        stim_bank = StimBank(win, config["stim_config"]).preload_all()
        reset_trial_counter()

        trigger_runtime.send(settings.triggers.get("experiment_start"))
        _continue_screen(
            win=win,
            kb=kb,
            stim_bank=stim_bank,
            trigger_runtime=trigger_runtime,
            settings=settings,
            label="instruction",
            stim_id="instruction_text",
        )

        block_order = resolve_block_order(subject.get("subject_id"), getattr(settings, "block_orders"))
        choice_sets = dict(getattr(settings, "choice_sets"))
        all_rows: list[dict[str, Any]] = []
        for block_idx, set_size in enumerate(block_order):
            set_spec = dict(choice_sets[str(set_size)])
            condition_labels = [str(value) for value in set_spec["condition_ids"]]
            _continue_screen(
                win=win,
                kb=kb,
                stim_bank=stim_bank,
                trigger_runtime=trigger_runtime,
                settings=settings,
                label="block_instruction",
                stim_id="block_instruction_text",
                values={
                    "block_num": block_idx + 1,
                    "total_blocks": len(block_order),
                    "set_size": set_size,
                    "information_bits": int(set_spec["information_bits"]),
                    "active_keys": str(set_spec["key_display"]),
                },
            )
            block_id = f"block_{block_idx + 1:02d}_n{set_size}"
            sequence_state: dict[str, Any] = {"previous_target_position": None}
            block = (
                BlockUnit(
                    block_id=block_id,
                    block_idx=block_idx,
                    settings=settings,
                    window=win,
                    keyboard=kb,
                )
                .generate_conditions(condition_labels=condition_labels, weights=[1.0] * len(condition_labels), order="random")
                .on_start(lambda _, _runtime=trigger_runtime, _settings=settings: _runtime.send(_settings.triggers.get("block_start")))
                .on_end(lambda _, _runtime=trigger_runtime, _settings=settings: _runtime.send(_settings.triggers.get("block_end")))
                .run_trial(
                    partial(
                        run_trial,
                        stim_bank=stim_bank,
                        trigger_runtime=trigger_runtime,
                        block_id=block_id,
                        block_idx=block_idx,
                        set_size=set_size,
                        sequence_state=sequence_state,
                    )
                )
            )
            block.to_dict(all_rows)
            if block_idx < len(block_order) - 1:
                block_summary = summarize_trials(block.get_all_data())
                _continue_screen(
                    win=win,
                    kb=kb,
                    stim_bank=stim_bank,
                    trigger_runtime=trigger_runtime,
                    settings=settings,
                    label="block_break",
                    stim_id="block_break_text",
                    values={
                        "block_num": block_idx + 1,
                        "total_blocks": len(block_order),
                        "set_size": set_size,
                        **block_summary,
                    },
                )

        summary = summarize_trials(all_rows)
        _continue_screen(
            win=win,
            kb=kb,
            stim_bank=stim_bank,
            trigger_runtime=trigger_runtime,
            settings=settings,
            label="good_bye",
            stim_id="good_bye_text",
            values=summary,
            terminate=True,
        )
        trigger_runtime.send(settings.triggers.get("experiment_end"))
        pd.DataFrame(all_rows).to_csv(settings.res_file, index=False)
        if hasattr(trigger_runtime, "close"):
            trigger_runtime.close()
        core.quit()


def main() -> None:
    run(
        parse_task_run_options(
            task_root=Path(__file__).resolve().parent,
            description="Run the Hick–Hyman Choice Reaction Task.",
            default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
            modes=MODES,
        )
    )


if __name__ == "__main__":
    main()
