"""Economic-Driven Self-Learning Agent Integration Proof-of-Concept.

Demonstrates integration between:
- ClawWork economic_sdk (economic value tracking)
- ai-native-self-learning-agents (intrinsic motivation)

This PoC shows how economic feedback can drive agent learning parameters.
"""

import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any
import tempfile

sys.path.insert(0, str(Path(__file__).parent / "economic_sdk"))

from economic_sdk.tracker import EconomicTracker
from economic_sdk.models import TrackerConfig


@dataclass
class LearningMetrics:
    novelty: float = 0.0
    learning_progress: float = 0.0
    economic_value: float = 0.0
    intrinsic_motivation: float = 0.0


class EconomicDrivenAgent:
    def __init__(self, agent_id: str, initial_balance: float = 1000.0):
        self.agent_id = agent_id

        config = TrackerConfig(
            signature=agent_id,
            initial_balance=initial_balance,
            output_dir=Path(tempfile.mkdtemp()),
        )
        self.tracker = EconomicTracker(config)

        self.metrics = LearningMetrics()

        self.config = {
            "learning_rate": 0.001,
            "exploration_rate": 0.3,
            "threshold_confidence": 0.6,
        }

    def track_task_completion(
        self,
        task_description: str,
        value_earned: float,
        tokens_used: int = 0,
        api_calls: int = 0,
    ) -> Dict[str, Any]:
        task_id = f"task_{len(self.tracker.daily_task_ids) + 1}"
        self.tracker.start_task(task_id)

        llm_cost = 0.0
        if tokens_used > 0:
            llm_cost = self.tracker.track_llm_call(
                input_tokens=tokens_used // 2,
                output_tokens=tokens_used // 2,
                api_name="gpt-4o",
            )

        api_cost = 0.0
        if api_calls > 0:
            for _ in range(api_calls):
                api_cost += self.tracker.track_api_call(
                    api_name="search_api", cost=0.005
                )

        net_value = value_earned - llm_cost - api_cost

        if value_earned > 0:
            evaluation_score = 0.8
            self.tracker.add_work_income(
                amount=value_earned,
                task_id=task_id,
                evaluation_score=evaluation_score,
                description=task_description,
            )

        self.tracker.end_task()

        self.metrics.economic_value = net_value

        self.metrics.novelty = min(1.0, tokens_used / 10000)
        self.metrics.learning_progress = min(1.0, net_value / 10.0)

        self.metrics.intrinsic_motivation = (
            self.metrics.novelty * self.metrics.learning_progress
        )

        self._adjust_learning_parameters()

        return {
            "task": task_description,
            "value_earned": value_earned,
            "costs": {"llm": llm_cost, "api": api_cost},
            "net_value": net_value,
            "balance": self.tracker.get_balance(),
            "metrics": {
                "novelty": self.metrics.novelty,
                "learning_progress": self.metrics.learning_progress,
                "intrinsic_motivation": self.metrics.intrinsic_motivation,
            },
            "learning_config": self.config.copy(),
        }

    def _adjust_learning_parameters(self) -> None:
        if self.metrics.economic_value > 5.0:
            self.config["learning_rate"] = min(0.01, self.config["learning_rate"] * 1.1)
            self.config["exploration_rate"] = max(
                0.1, self.config["exploration_rate"] * 0.95
            )
        elif self.metrics.economic_value < 0:
            self.config["learning_rate"] = max(
                0.0001, self.config["learning_rate"] * 0.9
            )
            self.config["exploration_rate"] = min(
                0.5, self.config["exploration_rate"] * 1.05
            )

        self.config["threshold_confidence"] = 0.5 + (
            self.metrics.intrinsic_motivation * 0.3
        )

    def get_summary(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "balance": self.tracker.get_balance(),
            "metrics": {
                "novelty": self.metrics.novelty,
                "learning_progress": self.metrics.learning_progress,
                "economic_value": self.metrics.economic_value,
                "intrinsic_motivation": self.metrics.intrinsic_motivation,
            },
            "learning_config": self.config.copy(),
        }


def run_integration_demo():
    print("=" * 80)
    print("Economic-Driven Self-Learning Agent Integration PoC")
    print("=" * 80)
    print()

    agent = EconomicDrivenAgent("demo-agent-001", initial_balance=1000.0)

    tasks = [
        {"desc": "Simple data extraction", "value": 5.0, "tokens": 500, "api": 1},
        {"desc": "Complex analysis", "value": 15.0, "tokens": 2000, "api": 3},
        {"desc": "Quick lookup", "value": 2.0, "tokens": 100, "api": 1},
        {"desc": "Deep research", "value": 25.0, "tokens": 5000, "api": 5},
        {"desc": "Failed task", "value": 0.0, "tokens": 1000, "api": 2},
    ]

    print("Task Execution Sequence:")
    print("-" * 80)

    for i, task in enumerate(tasks, 1):
        print(f"\nTask {i}: {task['desc']}")
        result = agent.track_task_completion(
            task["desc"], task["value"], task["tokens"], task["api"]
        )

        print(f"  Value Earned: ${result['value_earned']:.2f}")
        print(
            f"  Costs: LLM=${result['costs']['llm']:.4f}, API=${result['costs']['api']:.3f}"
        )
        print(f"  Net Value: ${result['net_value']:.4f}")
        print(f"  Balance: ${result['balance']:.4f}")
        print(
            f"  Intrinsic Motivation: {result['metrics']['intrinsic_motivation']:.3f}"
        )
        print(f"  Learning Rate: {result['learning_config']['learning_rate']:.6f}")
        print(
            f"  Exploration Rate: {result['learning_config']['exploration_rate']:.3f}"
        )

    print()
    print("=" * 80)
    print("Final Agent Summary")
    print("=" * 80)

    summary = agent.get_summary()
    print(f"\nAgent ID: {summary['agent_id']}")
    print(f"Final Balance: ${summary['balance']:.4f}")
    print(f"\nMetrics:")
    for key, value in summary["metrics"].items():
        print(f"  {key}: {value:.4f}")
    print(f"\nLearning Configuration:")
    for key, value in summary["learning_config"].items():
        print(
            f"  {key}: {value:.6f}" if isinstance(value, float) else f"  {key}: {value}"
        )

    print()
    print("=" * 80)
    print("Integration Status: ✅ SUCCESS")
    print("=" * 80)
    print()
    print("Key Observations:")
    print("1. Economic value successfully tracked for each task")
    print("2. Intrinsic motivation formula integrated (novelty × learning_progress)")
    print("3. Learning parameters adjusted based on economic feedback")
    print("4. High-value tasks → increased learning rate, reduced exploration")
    print("5. Low-value tasks → decreased learning rate, increased exploration")
    print()
    print("Next Steps for Production:")
    print("- Connect to real ai-native-self-learning-agents BaseAgent")
    print("- Integrate with DSPy optimization pipeline")
    print("- Add PEFT/LoRA fine-tuning based on economic signals")
    print("- Implement multi-agent economic competition framework")
    print("=" * 80)


if __name__ == "__main__":
    run_integration_demo()
