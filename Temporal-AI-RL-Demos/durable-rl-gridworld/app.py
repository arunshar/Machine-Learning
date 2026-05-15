from __future__ import annotations

import asyncio
import random
import sys
from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, List, Tuple

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker

TASK_QUEUE = "durable-rl-gridworld"

State = Tuple[int, int]
Action = str

ACTIONS: Tuple[Action, ...] = ("up", "down", "left", "right")
GOAL: State = (3, 3)
TRAP: State = (1, 2)


@dataclass
class ExperimentConfig:
    workflow_id: str = "rl-gridworld-demo"
    batches: int = 8
    episodes_per_batch: int = 50
    max_steps: int = 30
    alpha: float = 0.2
    gamma: float = 0.95
    epsilon: float = 0.25
    target_avg_reward: float = 0.75
    seed: int = 7


@dataclass
class BatchInput:
    batch_index: int
    q_table: Dict[str, Dict[Action, float]]
    config: ExperimentConfig


def state_key(state: State) -> str:
    return f"{state[0]},{state[1]}"


def next_state(state: State, action: Action) -> State:
    row, col = state
    if action == "up":
        row -= 1
    elif action == "down":
        row += 1
    elif action == "left":
        col -= 1
    elif action == "right":
        col += 1
    return max(0, min(3, row)), max(0, min(3, col))


def reward_for(state: State) -> float:
    if state == GOAL:
        return 1.0
    if state == TRAP:
        return -1.0
    return -0.02


def ensure_state(q_table: Dict[str, Dict[Action, float]], state: State) -> Dict[Action, float]:
    key = state_key(state)
    if key not in q_table:
        q_table[key] = {action: 0.0 for action in ACTIONS}
    return q_table[key]


def choose_action(q_table: Dict[str, Dict[Action, float]], state: State, epsilon: float, rng: random.Random) -> Action:
    values = ensure_state(q_table, state)
    if rng.random() < epsilon:
        return rng.choice(ACTIONS)
    return max(ACTIONS, key=lambda action: values[action])


@activity.defn
async def train_batch(payload: BatchInput) -> Dict[str, object]:
    """Run one idempotent RL training batch.

    The random seed is derived from the batch index so the Activity can be retried
    without producing inconsistent experiment state.
    """

    rng = random.Random(payload.config.seed + payload.batch_index)
    q_table = {state: values.copy() for state, values in payload.q_table.items()}
    rewards: List[float] = []

    for episode in range(payload.config.episodes_per_batch):
        state: State = (0, 0)
        total_reward = 0.0

        for step in range(payload.config.max_steps):
            activity.heartbeat({"episode": episode, "step": step})
            action = choose_action(q_table, state, payload.config.epsilon, rng)
            candidate = next_state(state, action)
            reward = reward_for(candidate)
            total_reward += reward

            current = ensure_state(q_table, state)
            nxt = ensure_state(q_table, candidate)
            best_next = max(nxt.values())
            current[action] += payload.config.alpha * (reward + payload.config.gamma * best_next - current[action])
            state = candidate

            if state in (GOAL, TRAP):
                break

        rewards.append(total_reward)

    avg_reward = round(sum(rewards) / len(rewards), 4)
    return {
        "batch_index": payload.batch_index,
        "avg_reward": avg_reward,
        "q_table": q_table,
        "checkpoint_key": f"gridworld/batch-{payload.batch_index:03d}.json",
    }


@activity.defn
async def evaluate_policy(q_table: Dict[str, Dict[Action, float]]) -> Dict[str, object]:
    state: State = (0, 0)
    path = [state]
    total_reward = 0.0

    for _ in range(20):
        values = ensure_state(q_table, state)
        action = max(ACTIONS, key=lambda candidate: values[candidate])
        state = next_state(state, action)
        path.append(state)
        total_reward += reward_for(state)
        if state in (GOAL, TRAP):
            break

    return {"path": path, "total_reward": round(total_reward, 4), "reached_goal": state == GOAL}


@workflow.defn
class DurableRLExperiment:
    def __init__(self) -> None:
        self._progress: List[Dict[str, object]] = []
        self._stopped = False

    @workflow.run
    async def run(self, config: ExperimentConfig) -> Dict[str, object]:
        q_table: Dict[str, Dict[Action, float]] = {}

        for batch_index in range(config.batches):
            if self._stopped:
                break

            result = await workflow.execute_activity(
                train_batch,
                BatchInput(batch_index=batch_index, q_table=q_table, config=config),
                start_to_close_timeout=timedelta(minutes=2),
                heartbeat_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(maximum_attempts=3, initial_interval=timedelta(seconds=1)),
            )
            q_table = result["q_table"]  # type: ignore[assignment]
            self._progress.append(
                {
                    "batch_index": result["batch_index"],
                    "avg_reward": result["avg_reward"],
                    "checkpoint_key": result["checkpoint_key"],
                }
            )

            if float(result["avg_reward"]) >= config.target_avg_reward:
                break

        evaluation = await workflow.execute_activity(
            evaluate_policy,
            q_table,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(maximum_attempts=2),
        )
        return {"batches": self._progress, "evaluation": evaluation, "stopped": self._stopped}

    @workflow.query
    def progress(self) -> List[Dict[str, object]]:
        return self._progress

    @workflow.signal
    async def stop(self) -> None:
        self._stopped = True


async def connect_client() -> Client:
    return await Client.connect("localhost:7233")


async def run_worker() -> None:
    client = await connect_client()
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[DurableRLExperiment],
        activities=[train_batch, evaluate_policy],
    )
    await worker.run()


async def start_workflow() -> None:
    config = ExperimentConfig()
    client = await connect_client()
    handle = await client.start_workflow(
        DurableRLExperiment.run,
        config,
        id=config.workflow_id,
        task_queue=TASK_QUEUE,
    )
    print(f"Started Workflow Execution: {handle.id}")
    print(await handle.result())


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "help"
    if command == "worker":
        asyncio.run(run_worker())
    elif command == "start":
        asyncio.run(start_workflow())
    else:
        print("Usage: python app.py [worker|start]")
