import { condition, defineQuery, defineSignal, proxyActivities, setHandler } from '@temporalio/workflow';
import type * as activities from './activities.js';
import type { ReviewDecision, ReviewInput, ReviewProgress } from './types.js';

const { scorePolicy, draftReview, persistReview, notifyReviewer } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
  retry: {
    initialInterval: '1 second',
    maximumAttempts: 3,
  },
});

export const approveSignal = defineSignal<[ReviewDecision]>('approve');
export const updateThresholdSignal = defineSignal<[number]>('updateThreshold');
export const progressQuery = defineQuery<ReviewProgress>('progress');

export async function reviewPolicyWorkflow(input: ReviewInput): Promise<ReviewDecision> {
  let progress: ReviewProgress = { stage: 'queued' };
  let decision: ReviewDecision | undefined;
  let minReward = input.minReward;

  setHandler(progressQuery, () => progress);
  setHandler(approveSignal, (humanDecision) => {
    decision = humanDecision;
    progress = { ...progress, stage: humanDecision.approved ? 'approved' : 'rejected', decision: humanDecision };
  });
  setHandler(updateThresholdSignal, (nextMinReward) => {
    minReward = nextMinReward;
  });

  progress = { stage: 'scoring' };
  const score = await scorePolicy(input.policy);

  progress = { stage: 'drafting', score };
  const summary = await draftReview({
    policy: input.policy,
    score,
    minReward,
    maxSafetyViolations: input.maxSafetyViolations,
  });

  await persistReview({
    experimentId: input.experimentId,
    candidateId: input.policy.id,
    summary,
    score,
  });
  await notifyReviewer({ experimentId: input.experimentId, candidateId: input.policy.id, summary });

  const autoReject = input.policy.rewardMean < minReward || input.policy.safetyViolations > input.maxSafetyViolations;
  if (autoReject) {
    decision = {
      candidateId: input.policy.id,
      approved: false,
      reason: `below threshold after durable review: minReward=${minReward}, maxSafetyViolations=${input.maxSafetyViolations}`,
    };
    progress = { stage: 'rejected', score, summary, decision };
    return decision;
  }

  progress = { stage: 'waiting-for-human', score, summary };
  await condition(() => decision !== undefined, '7 days');

  if (!decision) {
    decision = {
      candidateId: input.policy.id,
      approved: false,
      reason: 'timed out waiting for human approval',
    };
  }

  progress = { stage: decision.approved ? 'approved' : 'rejected', score, summary, decision };
  return decision;
}
