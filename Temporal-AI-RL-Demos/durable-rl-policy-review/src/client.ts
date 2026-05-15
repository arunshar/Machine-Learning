import { Client } from '@temporalio/client';
import { approveSignal, progressQuery, reviewPolicyWorkflow } from './workflows.js';
import type { ReviewInput } from './types.js';

async function main() {
  const client = new Client();

  const input: ReviewInput = {
    experimentId: 'rl-navigation-research',
    minReward: 80,
    maxSafetyViolations: 1,
    policy: {
      id: 'ppo-gridworld-v3',
      algorithm: 'ppo',
      rewardMean: 87.4,
      rewardStd: 6.2,
      safetyViolations: 1,
      checkpointUri: 's3://example-research-checkpoints/ppo-gridworld-v3.pt',
    },
  };

  const handle = await client.workflow.start(reviewPolicyWorkflow, {
    taskQueue: 'durable-rl-policy-review',
    workflowId: `policy-review-${input.policy.id}`,
    args: [input],
  });

  console.log('Started Workflow Execution', handle.workflowId);
  console.log('Progress', await handle.query(progressQuery));

  await handle.signal(approveSignal, {
    candidateId: input.policy.id,
    approved: true,
    reason: 'reward and safety metrics meet review threshold',
  });

  console.log(await handle.result());
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
