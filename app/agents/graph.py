from __future__ import annotations

from .planner import PlannerAgent
from .curator import DataCuratorAgent
from .runner import RunnerAgent
from .evaluator import EvaluatorAgent
from .observability import ObservabilityAgent
from .reporter import ReportAgent


def build_graph(cfg: dict):
    planner = PlannerAgent(cfg)
    curator = DataCuratorAgent(cfg)
    runner = RunnerAgent(cfg)
    evaluator = EvaluatorAgent(cfg)
    observ = ObservabilityAgent(cfg)
    reporter = ReportAgent(cfg)
    return planner, curator, runner, evaluator, observ, reporter


