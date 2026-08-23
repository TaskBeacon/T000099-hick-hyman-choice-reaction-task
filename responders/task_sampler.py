from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Any

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


class ScriptedResponder:
    def start_session(self, session: SessionInfo, rng: Any) -> None:
        return None

    def on_feedback(self, feedback: Feedback) -> None:
        return None

    def end_session(self) -> None:
        return None

    def act(self, observation: Observation) -> Action:
        keys = [str(key).lower() for key in observation.valid_keys]
        if not keys:
            return Action(key=None, rt_s=None)
        if observation.phase == "choice_response":
            correct_key = str(observation.task_factors.get("correct_key", "")).lower()
            bits = float(observation.task_factors.get("information_bits", 1.0))
            return Action(key=correct_key if correct_key in keys else keys[0], rt_s=0.20 + 0.06 * bits)
        return Action(key="space" if "space" in keys else keys[0], rt_s=0.10)


@dataclass
class TaskSamplerResponder:
    intercept_s: float = 0.22
    slope_s_per_bit: float = 0.07
    rt_sd_s: float = 0.025
    error_rate: float = 0.10
    timeout_rate: float = 0.04

    def __post_init__(self) -> None:
        self._rng: Any = None

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._rng = rng

    def on_feedback(self, feedback: Feedback) -> None:
        return None

    def end_session(self) -> None:
        self._rng = None

    def _random(self) -> float:
        return float(self._rng.random()) if hasattr(self._rng, "random") else random.random()

    def _normal(self, mean: float, sd: float) -> float:
        if hasattr(self._rng, "normal"):
            return float(self._rng.normal(mean, sd))
        if hasattr(self._rng, "gauss"):
            return float(self._rng.gauss(mean, sd))
        return random.gauss(mean, sd)

    def act(self, observation: Observation) -> Action:
        keys = [str(key).lower() for key in observation.valid_keys]
        if not keys:
            return Action(key=None, rt_s=None)
        if observation.phase != "choice_response":
            return Action(key="space" if "space" in keys else keys[0], rt_s=0.10)
        if self._random() < self.timeout_rate:
            return Action(key=None, rt_s=None, meta={"kind": "timeout"})
        correct_key = str(observation.task_factors.get("correct_key", "")).lower()
        chosen_key = correct_key if correct_key in keys else keys[0]
        if self._random() < self.error_rate:
            chosen_key = next((key for key in keys if key != correct_key), chosen_key)
        bits = float(observation.task_factors.get("information_bits", 1.0))
        rt_s = max(0.12, self._normal(self.intercept_s + self.slope_s_per_bit * bits, self.rt_sd_s))
        return Action(key=chosen_key, rt_s=rt_s, meta={"kind": "choice", "bits": bits})
