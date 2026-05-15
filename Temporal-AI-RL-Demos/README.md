# Temporal AI RL Demos

Small, resume-ready examples that connect reinforcement learning workflows with Temporal's durable execution model.

These projects are intentionally compact. They demonstrate the vocabulary and engineering surface area relevant to Temporal's AI SDK work without claiming production Temporal experience:

- Workflows as code
- Activities for non-deterministic work
- Workers and Task Queues
- Temporal Client start/query/signal flow
- Retry Policy, timeouts, heartbeats, idempotency, and checkpointing
- Durable agent / human-in-the-loop orchestration patterns
- Python SDK and TypeScript SDK examples

## Projects

1. [`durable-rl-gridworld`](./durable-rl-gridworld) - Python Temporal workflow that orchestrates fault-tolerant Q-learning batches for a gridworld policy, including retries, workflow queries, stop signals, and checkpoint-shaped outputs.
2. [`durable-rl-policy-review`](./durable-rl-policy-review) - TypeScript Temporal workflow that models an AI SDK style policy-review loop with tool-like Activities, long-running evaluation, human approval, and deterministic workflow state.

## Why this exists

Temporal's AI SDK role emphasizes reliable AI applications: agents, tool calls, memory/state, human-in-the-loop work, background processing, and integrations across Python/TypeScript. These demos frame reinforcement learning research as a durable distributed-systems problem: experiments run for a long time, fail midway, call external services, checkpoint state, and need observable progress.