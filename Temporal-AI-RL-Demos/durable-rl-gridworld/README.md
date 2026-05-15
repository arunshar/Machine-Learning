# Durable RL Gridworld

A minimal Python Temporal application that treats reinforcement-learning training as durable orchestration.

The Workflow coordinates Q-learning batches as Activities. If a Worker crashes between batches, Temporal can replay the deterministic Workflow state and continue from the Event History. Non-deterministic operations such as random exploration, checkpoint writes, and metric generation are isolated inside Activities.

## Temporal concepts demonstrated

- Workflow Definition and Workflow Execution
- Activity Definition and Activity Execution
- Worker Process polling a Task Queue
- Temporal Client starting a Workflow with a Workflow Id
- RetryPolicy for transient batch failures
- Start-To-Close Timeout for bounded Activity execution
- Query handler for progress inspection
- Signal handler for cooperative cancellation
- Idempotent checkpoint-shaped Activity output

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install temporalio

temporal server start-dev
python app.py worker
python app.py start
```

The same code can be pointed at Temporal Cloud by configuring the client connection in `connect_client()`.

## Resume framing

Built a Temporal Python SDK demo that maps long-running RL experiments to Workflows and Activities, preserving progress across Worker restarts with retries, timeout policies, Workflow queries/signals, and checkpoint-style Activity outputs.