import { Worker } from '@temporalio/worker';
import * as activities from './activities.js';

async function main() {
  const worker = await Worker.create({
    workflowsPath: new URL('./workflows.ts', import.meta.url).pathname,
    activities,
    taskQueue: 'durable-rl-policy-review',
  });

  await worker.run();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
