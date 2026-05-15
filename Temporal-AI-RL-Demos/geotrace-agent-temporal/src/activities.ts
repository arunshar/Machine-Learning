import type { PolicyCandidate } from './types.js';

export async function scorePolicy(policy: PolicyCandidate): Promise<number> {
  const stabilityPenalty = Math.min(policy.rewardStd / 10, 0.25);
  const safetyPenalty = policy.safetyViolations * 0.15;
  return Number((policy.rewardMean / 100 - stabilityPenalty - safetyPenalty).toFixed(3));
}

export async function draftReview(input: {
  policy: PolicyCandidate;
  score: number;
  minReward: number;
  maxSafetyViolations: number;
}): Promise<string> {
  const verdict =
    input.policy.rewardMean >= input.minReward &&
    input.policy.safetyViolations <= input.maxSafetyViolations
      ? 'candidate is ready for human approval'
      : 'candidate needs another training run';

  return [
    `Policy ${input.policy.id} (${input.policy.algorithm}) ${verdict}.`,
    `Mean reward=${input.policy.rewardMean}, reward std=${input.policy.rewardStd}, safety violations=${input.policy.safetyViolations}, composite score=${input.score}.`,
    `Checkpoint: ${input.policy.checkpointUri}`,
  ].join(' ');
}

export async function persistReview(input: {
  experimentId: string;
  candidateId: string;
  summary: string;
  score: number;
}): Promise<string> {
  return `reviews/${input.experimentId}/${input.candidateId}.json`;
}

export async function notifyReviewer(input: { experimentId: string; candidateId: string; summary: string }): Promise<void> {
  console.log(`Review requested for ${input.experimentId}/${input.candidateId}: ${input.summary}`);
}
