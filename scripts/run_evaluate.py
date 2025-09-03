from __future__ import annotations

import sys
import json

from app.agents.evaluator import EvaluatorAgent


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python scripts/run_evaluate.py <dataset_json> <comma_tasks>")
        sys.exit(1)
    dataset = sys.argv[1]
    tasks = sys.argv[2].split(",")
    agent = EvaluatorAgent(config={})
    result = agent.evaluate(dataset, tasks)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()


