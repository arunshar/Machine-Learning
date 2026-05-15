# Durable RL Policy Review

A TypeScript Temporal demo for reviewing reinforcement-learning policy candidates as a durable, human-in-the-loop agent workflow.

The Workflow keeps orchestration deterministic. Tool-like work such as metric scoring, model commentary, persistence, and notification runs in Activities. This mirrors the shape of AI SDK integrations where LLM/tool calls are non-deterministic and must be wrapped outside Workflow code.

## Temporal concepts demonstrated

- TypeScript SDK Workflow, Activities, Worker, Client, Namespace, and Task Queue
- Signals for human approval and threshold changes
- Queries for Workflow visibility
- Activity retries and timeouts
- Durable agent loop for long-running evaluation
- Separation between deterministic workflow logic and non-deterministic tool/API calls

## Run locally

```bash
npm install
npx temporal server start-dev
npm run worker
npm run start
```

The Activities are mocked so the demo can run without API keys. To connect it to the Vercel AI SDK / `@temporalio/ai-sdk` public-preview integration, replace `draftReview()` with a real model call that executes as an Activity.

## Resume framing

Built a Temporal TypeScript demo for durable AI/RL review loops using Workflow queries, Signals, retryable Activities, and human-in-the-loop approval semantics for long-running agentic evaluations.