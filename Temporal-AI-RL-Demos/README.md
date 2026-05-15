# Temporalized Research Systems: GeoTrace-Agent and Pi-GRPO

This folder contains two small but realistic engineering slices from my geospatial AI research. They are not generic Temporal tutorials. They are written around problems I have worked on directly: auditable spatiotemporal reasoning over heterogeneous trajectory/Earth-observation sources, and physics-informed reinforcement learning for trajectory generation and reasoning.

The shared idea is simple: both systems have long-running, failure-prone, externally connected work. A spatial agent may call AIS, OSM, weather, imagery, and kinematic validators before asking a human reviewer to approve an answer. An RL training loop may run rollouts, score physical feasibility, checkpoint policies, and curate preference data over many hours. Those are orchestration problems as much as ML problems, which is why Temporal is a natural fit.

## Projects

| Project | What it models | Temporal surface |
| --- | --- | --- |
| [`geotrace-agent-temporal`](./geotrace-agent-temporal) | Durable multi-agent geospatial reasoning for GeoTrace-Agent | TypeScript SDK, Workflows, Activities, Signals, Queries, human-in-the-loop review, AI SDK/MCP-ready tool calls |
| [`pi-grpo-temporal`](./pi-grpo-temporal) | Durable physics-informed RL training/evaluation for Pi-GRPO | Python SDK, Workflows, Activities, Task Queues, retries, heartbeats, Signals, Queries, checkpoint-shaped outputs |

## Why Temporal belongs here

Temporal's core abstraction is Durable Execution: application code can resume after process crashes, network failures, worker restarts, or infrastructure outages. That maps well to research systems that need to preserve state across expensive experiments and multi-step reasoning workflows.

In these projects:

- Workflows hold deterministic orchestration state.
- Activities isolate non-deterministic work: model calls, external APIs, database writes, file/checkpoint I/O, scoring jobs, and notification hooks.
- Workers poll Task Queues and execute the Workflow/Activity code.
- Event History makes progress replayable and inspectable.
- Signals model outside events such as stop requests, reviewer decisions, and threshold updates.
- Queries expose progress without mutating Workflow state.
- Retry policies, timeouts, heartbeats, and idempotent outputs make long-running work recoverable.

## Repository posture

The implementation is intentionally compact, but the READMEs describe the full research-system design. I kept the runnable code small enough to audit quickly while still using the same architecture I would use for a production version:

- deterministic orchestration in Workflow code;
- non-deterministic APIs and ML calls in Activities;
- typed inputs/outputs for reproducibility;
- explicit failure boundaries;
- human review as a first-class part of the system;
- observability hooks for W&B/OpenTelemetry-style experiment traces.

## Running locally

Install the Temporal CLI and start the dev server:

```bash
temporal server start-dev
```

Then follow each project README.

## Relationship to the research bullets

These projects connect to two research bullets in my resume:

- GeoTrace-Agent: multi-agent spatiotemporal reasoning with typed planning, MCP/JSON-RPC tool access, physical-feasibility checks, semantic caching, OpenTelemetry tracing, and Postgres-backed human review.
- Pi-GRPO: physics-informed RL/alignment stack combining PPO, DPO, and GRPO with S-KBM hard-violation penalties, jerk/curvature envelopes, Pi-DPM likelihood terms, vLLM-backed rollouts, content-addressed checkpoints, and preference-data curation from GeoTrace-Agent.
