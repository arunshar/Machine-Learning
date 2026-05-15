export type PolicyCandidate = {
  id: string;
  algorithm: 'ppo' | 'dqn' | 'sac';
  rewardMean: number;
  rewardStd: number;
  safetyViolations: number;
  checkpointUri: string;
};

export type ReviewDecision = {
  candidateId: string;
  approved: boolean;
  reason: string;
};

export type ReviewInput = {
  experimentId: string;
  policy: PolicyCandidate;
  minReward: number;
  maxSafetyViolations: number;
};

export type ReviewProgress = {
  stage: 'queued' | 'scoring' | 'drafting' | 'waiting-for-human' | 'approved' | 'rejected';
  score?: number;
  summary?: string;
  decision?: ReviewDecision;
};
