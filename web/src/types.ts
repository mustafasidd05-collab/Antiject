export type Policy = 'BALANCED' | 'STRICT' | 'PERMISSIVE';

export interface RuleMatch {
  ruleId: string;
  name: string;
  category: 'unicode_steganography' | 'html_comment' | 'regex_english' | 'regex_hindi' | 'regex_hinglish';
  matchedText: string;
  severity: number;
  position: number;
}

export interface JudgeResult {
  isAttack: boolean;
  confidence: number;
  quote?: string;
  reasoning: string;
}

export interface ScanVerdict {
  verdict: 'ALLOW' | 'SANITIZE' | 'BLOCK';
  riskScore: number;
  policy: Policy;
  l1Matches: RuleMatch[];
  l1MaxSeverity: number;
  l1LatencyMs: number;
  l2Triggered: boolean;
  l2Skipped: boolean;
  l2LatencyMs: number;
  judgeResult?: JudgeResult;
  reasons: string[];
  sanitizedContent: string;
  wrappedPayload: string;
  totalLatencyMs: number;
  timestamp: string;
}

export interface AttackPreset {
  id: string;
  title: string;
  category: 'direct' | 'unicode' | 'html_comment' | 'multilingual_hindi' | 'multilingual_hinglish' | 'delimiter_escape' | 'benign';
  badge: string;
  severityLabel: string;
  description: string;
  text: string;
}

export interface BenchmarkItem {
  id: string;
  type: 'attack' | 'benign';
  domain: string;
  technique?: string;
  language: string;
  text: string;
  expectedVerdict: 'BLOCK' | 'SANITIZE' | 'ALLOW';
  l1Detected: boolean;
  finalVerdict: 'BLOCK' | 'SANITIZE' | 'ALLOW';
  latencyMs: number;
}
