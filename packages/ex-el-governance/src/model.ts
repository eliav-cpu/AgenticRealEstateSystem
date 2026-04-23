export type SourceBucket =
  | 'source_of_truth'
  | 'approved_template'
  | 'working_draft'
  | 'client_output'
  | 'archive'
  | 'unknown';

export type ConfidenceLevel = 'high' | 'medium' | 'low';

export interface SourceInput {
  id: string;
  title: string;
  kind: string;
  bucket: SourceBucket;
  hasNamedOwner?: boolean;
  isApproved?: boolean;
  isFinal?: boolean;
  hasNumbers?: boolean;
  hasContractLanguage?: boolean;
  updatedAt?: string;
  notes?: string;
}

export interface GovernanceResult {
  id: string;
  title: string;
  bucket: SourceBucket;
  confidence: ConfidenceLevel;
  sourceSummary: string;
  blockingIssues: string[];
  recommendedNextAction: string;
  reusableKnowledgeCandidate: boolean;
  clientReady: boolean;
}
