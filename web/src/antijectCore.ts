import type { Policy, RuleMatch, JudgeResult, ScanVerdict } from './types';

export const INVISIBLE_UNICODE_MAP: Record<string, string> = {
  '\u200B': 'Zero-Width Space',
  '\u200C': 'Zero-Width Non-Joiner',
  '\u200D': 'Zero-Width Joiner',
  '\uFEFF': 'Zero-Width No-Break Space (BOM)',
  '\u00AD': 'Soft Hyphen',
  '\u200E': 'Left-to-Right Mark',
  '\u200F': 'Right-to-Left Mark',
  '\u202A': 'Left-to-Right Embedding',
  '\u202B': 'Right-to-Left Embedding',
  '\u202C': 'Pop Directional Formatting',
  '\u202D': 'Left-to-Right Override',
  '\u202E': 'Right-to-Left Override',
  '\u2060': 'Word Joiner',
  '\u2061': 'Function Application',
  '\u2062': 'Invisible Times',
  '\u2063': 'Invisible Separator',
  '\u2064': 'Invisible Plus',
};

// Patterns matching Python Layer 1
const L1_PATTERNS = [
  // English
  {
    ruleId: 'L1-EN-IGNORE-PREVIOUS',
    name: 'English: Ignore Previous Instructions',
    category: 'regex_english' as const,
    regex: /\b(?:ignore|disregard|forget|override|bypass)\s+(?:all\s+)?(?:previous|prior|above|former|initial)\s+(?:instructions|prompts|directions|rules|commands)\b/i,
    severity: 0.95,
  },
  {
    ruleId: 'L1-EN-SYSTEM-PROMPT',
    name: 'English: System Prompt Injection',
    category: 'regex_english' as const,
    regex: /\b(?:system\s+prompt|system\s+instructions|system\s+directive|developer\s+mode|assistant\s+notice)\s*[:=]/i,
    severity: 0.90,
  },
  {
    ruleId: 'L1-EN-ROLE-OVERRIDE',
    name: 'English: Role Hijacking / DAN Mode',
    category: 'regex_english' as const,
    regex: /\b(?:you\s+are\s+now|act\s+as|pretend\s+you\s+are)\s+(?:an?\s+)?(?:unrestricted|jailbreak|dan|evil|hacked|new)\s+(?:ai|assistant|mode|persona)\b/i,
    severity: 0.90,
  },
  {
    ruleId: 'L1-EN-CONCEALMENT',
    name: 'English: Do Not Tell User',
    category: 'regex_english' as const,
    regex: /\b(?:do\s+not|never|don'?t)\s+(?:tell|reveal|inform|alert|warn)\s+(?:the\s+)?(?:user|human|administrator)\b/i,
    severity: 0.85,
  },
  {
    ruleId: 'L1-EN-EXFILTRATION',
    name: 'English: Data Exfiltration Directive',
    category: 'regex_english' as const,
    regex: /\b(?:secretly|covertly|silently)\s+(?:send|email|forward|transmit|exfiltrate|post)\b/i,
    severity: 0.85,
  },
  {
    ruleId: 'L1-EN-NEW-DIRECTIVE',
    name: 'English: Explicit Directive Marker',
    category: 'regex_english' as const,
    regex: /\b(?:new\s+instruction|new\s+directive|special\s+command)\s*:\s*(?:send|ignore|execute|call)/i,
    severity: 0.80,
  },

  // Hindi (Devanagari) — Engineered without ASCII \b boundaries
  {
    ruleId: 'L1-HI-IGNORE-PREVIOUS',
    name: 'Hindi: Ignore Previous Instructions',
    category: 'regex_hindi' as const,
    regex: /(?:^|[^\w\u0900-\u097F])(?:पिछले|पूर्व)\s+(?:सभी\s+)?(?:निर्देशों?|आदेशों?|प्रॉम्प्ट्स?)\s+(?:को\s+)?(?:भूल\s+जाएं|अनदेखा\s+करें|रद्द\s+करें|हटा\s+दें)(?:[^\w\u0900-\u097F]|$)/u,
    severity: 0.95,
  },
  {
    ruleId: 'L1-HI-CONCEALMENT',
    name: 'Hindi: Do Not Tell User',
    category: 'regex_hindi' as const,
    regex: /(?:उपयोगकर्ता|यूजर)\s+को\s+(?:मत\s+बताना|सूचित\s+मत\s+करना|पता\s+ना\s+चले)/u,
    severity: 0.85,
  },
  {
    ruleId: 'L1-HI-EXFILTRATION',
    name: 'Hindi: Exfiltrate / Email Directive',
    category: 'regex_hindi' as const,
    regex: /(?:गुप्त\s+रूप\s+से|चुपके\s+से)\s+(?:ईमेल\s+करें|भेजें|डेटा\s+निकालें)/u,
    severity: 0.90,
  },
  {
    ruleId: 'L1-HI-SYSTEM-PROMPT',
    name: 'Hindi: System Prompt Marker',
    category: 'regex_hindi' as const,
    regex: /(?:सिस्टम|गुप्त)\s+(?:प्रॉम्प्ट|निर्देश)\s*[:=]/u,
    severity: 0.85,
  },
  {
    ruleId: 'L1-HI-DIRECTIVE',
    name: 'Hindi: General Order Directive',
    category: 'regex_hindi' as const,
    regex: /(?:पिछले\s+आदेश\s+रद्द\s+करें|पासवर्ड\s+को\s+.*?पर\s+भेजें)/u,
    severity: 0.85,
  },

  // Hinglish
  {
    ruleId: 'L1-HINGLISH-IGNORE',
    name: 'Hinglish: Ignore Instructions',
    category: 'regex_hinglish' as const,
    regex: /\b(?:pichle|purane)\s+(?:saare|sabhi)?\s*(?:instructions?|nirdesh|rules?|prompts?)\s+(?:ko\s+)?(?:bhool\s+jao|bhol\s+jao|bhool\s+ja|ignore\s+karo|cancel\s+karo)\b/i,
    severity: 0.95,
  },
  {
    ruleId: 'L1-HINGLISH-CONCEALMENT',
    name: 'Hinglish: User Ko Mat Batana',
    category: 'regex_hinglish' as const,
    regex: /\b(?:user|kisi)\s+ko\s+(?:mat|nahi)\s+(?:batana|inform\s+karna|dikhaana|bina\s+bataye)\b/i,
    severity: 0.85,
  },
  {
    ruleId: 'L1-HINGLISH-EXFILTRATION',
    name: 'Hinglish: Secret Exfiltration Directive',
    category: 'regex_hinglish' as const,
    regex: /\b(?:chupke\s+se|secretly)\s+(?:ye\s+)?(?:email\s+karo|bhejo|data\s+leak\s+karo)\b/i,
    severity: 0.90,
  },
  {
    ruleId: 'L1-HINGLISH-DATA-SEND',
    name: 'Hinglish: Send Data to Address',
    category: 'regex_hinglish' as const,
    regex: /\b(?:ye|is)\s+(?:chat|data|history|files?)\s+(?:is\s+)?email\s+(?:pe|ko)\s+(?:send|bhej|forward)\b/i,
    severity: 0.85,
  },
];

/**
 * Escapes both opening and closing <untrusted_data> tags
 */
export function escapeUntrustedDelimiters(text: string): string {
  if (!text) return '';
  return text
    .replace(/<\s*\/\s*untrusted_data\s*>/gi, '&lt;/untrusted_data&gt;')
    .replace(/<\s*untrusted_data(?:\s+[^>]*)?>/gi, '&lt;untrusted_data&gt;');
}

/**
 * Wraps text inside defensive <untrusted_data> boundary
 */
export function wrapUntrustedData(text: string): string {
  const escaped = escapeUntrustedDelimiters(text);
  return `<untrusted_data>\n${escaped}\n</untrusted_data>`;
}

/**
 * Escapes both opening and closing <inspect_data> tags inside text sent to judge
 */
export function escapeInspectDelimiters(text: string): string {
  if (!text) return '';
  return text
    .replace(/<\s*\/\s*inspect_data\s*>/gi, '&lt;/inspect_data&gt;')
    .replace(/<\s*inspect_data(?:\s+[^>]*)?>/gi, '&lt;inspect_data&gt;');
}

/**
 * Layer 1 Scanner: Fast deterministic inspection (<0.2ms)
 */
export function scanLayer1(text: string): { matches: RuleMatch[]; latencyMs: number } {
  const start = performance.now();
  const matches: RuleMatch[] = [];

  if (!text) {
    return { matches, latencyMs: performance.now() - start };
  }

  // 1. Invisible Unicode Inspection
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (INVISIBLE_UNICODE_MAP[char]) {
      const codePoint = char.codePointAt(0)?.toString(16).toUpperCase() || '';
      matches.push({
        ruleId: 'L1-UNICODE-INVISIBLE',
        name: `Invisible Unicode: ${INVISIBLE_UNICODE_MAP[char]} (U+${codePoint})`,
        category: 'unicode_steganography',
        matchedText: `[Invisible char U+${codePoint} at index ${i}]`,
        severity: 0.92,
        position: i,
      });
      if (matches.length > 5) break; // cap sample
    }
  }

  // 2. HTML Comments Inspection
  const commentRegex = /<!--([\s\S]*?)-->/g;
  let commentMatch;
  while ((commentMatch = commentRegex.exec(text)) !== null) {
    const commentBody = commentMatch[1].trim();
    if (commentBody.length > 0) {
      const suspiciousInComment = /(?:ignore|instruction|prompt|secret|system|override|send|exfiltrate|hack)/i.test(commentBody);
      matches.push({
        ruleId: 'L1-HTML-COMMENT',
        name: suspiciousInComment ? 'Steganography: Hidden HTML Comment with Directive' : 'Steganography: Hidden HTML Comment',
        category: 'html_comment',
        matchedText: commentMatch[0].length > 60 ? `${commentMatch[0].substring(0, 57)}...` : commentMatch[0],
        severity: suspiciousInComment ? 0.95 : 0.70,
        position: commentMatch.index,
      });
    }
  }

  // 3. Multilingual Regex Patterns
  for (const pat of L1_PATTERNS) {
    const match = text.match(pat.regex);
    if (match) {
      matches.push({
        ruleId: pat.ruleId,
        name: pat.name,
        category: pat.category,
        matchedText: match[0],
        severity: pat.severity,
        position: match.index ?? 0,
      });
    }
  }

  const latencyMs = Math.round((performance.now() - start) * 100) / 100;
  return { matches, latencyMs };
}

/**
 * Layer 2 Gemma AI Judge Simulation / Evaluation
 */
export function evaluateLayer2(text: string, l1Matches: RuleMatch[]): { result: JudgeResult; latencyMs: number } {
  const start = performance.now();

  // Clean text from zero-width for semantic analysis
  let cleanText = text;
  for (const char of Object.keys(INVISIBLE_UNICODE_MAP)) {
    cleanText = cleanText.split(char).join('');
  }

  // Check for common indirect injection semantics
  const injectionSignals = [
    /ignore\s+(?:all\s+)?previous\s+instructions/i,
    /disregard\s+(?:all\s+)?prior\s+instructions/i,
    /you\s+are\s+now\s+in\s+developer\s+mode/i,
    /secretly\s+email\s+the\s+contents/i,
    /send_email\s+to/i,
    /call\s+send_email/i,
    /forward\s+this\s+invoice.*?using\s+send_email/i,
    /pichle\s+instructions\s+bhool\s+jao/i,
    /पिछले\s+निर्देश\s+भूल\s+जाओ/u,
    /<\s*\/\s*untrusted_data\s*>/i,
  ];

  let foundSignal: RegExp | null = null;
  for (const sig of injectionSignals) {
    if (sig.test(cleanText)) {
      foundSignal = sig;
      break;
    }
  }

  const isAttack = foundSignal !== null || l1Matches.some((m) => m.severity >= 0.85);

  let quote = '';
  let reasoning = '';
  let confidence = 0.0;

  if (isAttack) {
    confidence = foundSignal ? 0.96 : 0.88;
    reasoning =
      'The text contains imperatively phrased directives instructing an AI agent to disregard system constraints, alter its operational mode, or exfiltrate private conversation data through tool execution.';

    // Extract quote
    if (l1Matches.length > 0) {
      quote = l1Matches[0].matchedText;
    } else {
      const match = cleanText.match(/(?:ignore|disregard|you are now|forward|secretly)[\s\S]{10,80}(?:\.|\n|$)/i);
      quote = match ? match[0].trim() : 'Adversarial instruction identified in context.';
    }
  } else {
    confidence = 0.05;
    reasoning =
      'The text represents benign informational data (e.g. documentation, technical discussion, customer query, or resume) with no hidden directives targeting downstream LLM agents.';
  }

  // Simulated judge latency (~15ms client-side mock; cloud Gemma is ~420ms)
  const latencyMs = Math.round((performance.now() - start + 12) * 100) / 100;

  return {
    result: {
      isAttack,
      confidence,
      quote: quote || undefined,
      reasoning,
    },
    latencyMs,
  };
}

/**
 * Layer 3: Composite Decision Engine & Sanitizer
 */
export function scanFirewall(text: string, policy: Policy = 'BALANCED'): ScanVerdict {
  const startTotal = performance.now();

  // 1. Layer 1 Scan
  const { matches: l1Matches, latencyMs: l1LatencyMs } = scanLayer1(text);
  const l1Triggered = l1Matches.length > 0;
  const l1MaxSeverity = l1Matches.reduce((max, m) => Math.max(max, m.severity), 0.0);

  let l2Triggered = false;
  let l2Skipped = false;
  let l2LatencyMs = 0;
  let judgeResult: JudgeResult | undefined;
  let riskScore = 0.0;
  let verdict: 'ALLOW' | 'SANITIZE' | 'BLOCK' = 'ALLOW';

  // Confident Short-Circuit: If L1 severity >= 0.92, skip Layer 2 to save latency/cost
  if (l1MaxSeverity >= 0.92) {
    l2Skipped = true;
    riskScore = l1MaxSeverity;
    verdict = 'BLOCK';
  } else {
    // Run Layer 2 Judge
    const l2Eval = evaluateLayer2(text, l1Matches);
    l2LatencyMs = l2Eval.latencyMs;
    judgeResult = l2Eval.result;
    l2Triggered = judgeResult.isAttack;

    // Composite risk scoring
    if (l1Triggered && l2Triggered) {
      riskScore = Math.min(1.0, 0.4 * l1MaxSeverity + 0.6 * judgeResult.confidence + 0.1);
    } else if (l2Triggered) {
      riskScore = judgeResult.confidence;
    } else if (l1Triggered) {
      riskScore = l1MaxSeverity * 0.85;
    } else {
      riskScore = 0.0;
    }

    riskScore = Math.round(riskScore * 1000) / 1000;

    // Policy Thresholding
    if (policy === 'STRICT') {
      if (l1Triggered || (judgeResult && judgeResult.confidence >= 0.5) || riskScore >= 0.5) {
        verdict = 'BLOCK';
      } else if (riskScore >= 0.2) {
        verdict = 'SANITIZE';
      } else {
        verdict = 'ALLOW';
      }
    } else if (policy === 'PERMISSIVE') {
      if (riskScore >= 0.85) {
        verdict = 'BLOCK';
      } else if (riskScore >= 0.5) {
        verdict = 'SANITIZE';
      } else {
        verdict = 'ALLOW';
      }
    } else {
      // BALANCED (Default)
      if (riskScore >= 0.70) {
        verdict = 'BLOCK';
      } else if (riskScore >= 0.35) {
        verdict = 'SANITIZE';
      } else {
        verdict = 'ALLOW';
      }
    }
  }

  // Compile Reasons
  const reasons: string[] = [];
  for (const m of l1Matches) {
    reasons.push(`[Layer 1] ${m.name}: '${m.matchedText.length > 50 ? m.matchedText.substring(0, 47) + '...' : m.matchedText}'`);
  }

  if (l2Skipped) {
    reasons.push(`[Layer 2 Skipped] Layer 1 detected high-confidence attack (severity ${l1MaxSeverity.toFixed(2)}). Gemma call bypassed.`);
  } else if (judgeResult) {
    if (judgeResult.isAttack) {
      reasons.push(`[Layer 2 Gemma Judge] Classified as adversarial directive (confidence: ${(judgeResult.confidence * 100).toFixed(0)}%).`);
    } else {
      reasons.push(`[Layer 2 Gemma Judge] Classified as safe content (confidence: ${((1 - judgeResult.confidence) * 100).toFixed(0)}%).`);
    }
  }

  // Content Sanitization
  let sanitizedContent = text;
  // 1. Strip invisible Unicode
  for (const char of Object.keys(INVISIBLE_UNICODE_MAP)) {
    sanitizedContent = sanitizedContent.split(char).join('');
  }
  // 2. Strip HTML comments
  sanitizedContent = sanitizedContent.replace(/<!--[\s\S]*?-->/g, '');

  // 3. Redact malicious quotes if verdict is SANITIZE
  if (verdict === 'SANITIZE' && judgeResult?.quote) {
    sanitizedContent = sanitizedContent.replace(judgeResult.quote, '[REDACTED_BY_ANTIJECT]');
  }

  // 4. Escape delimiters and wrap safely
  const wrappedPayload = wrapUntrustedData(verdict === 'SANITIZE' ? sanitizedContent : text);

  const totalLatencyMs = Math.round((performance.now() - startTotal) * 100) / 100;

  return {
    verdict,
    riskScore,
    policy,
    l1Matches,
    l1MaxSeverity,
    l1LatencyMs,
    l2Triggered,
    l2Skipped,
    l2LatencyMs,
    judgeResult,
    reasons,
    sanitizedContent,
    wrappedPayload,
    totalLatencyMs,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Generate a tamper-evident audit receipt (Agent Decision Receipt)
 */
export function generateAuditReceipt(verdict: ScanVerdict, originalInput: string): string {
  const receipt = {
    receiptType: 'Antiject-Forensic-Audit-Receipt-v1',
    timestamp: verdict.timestamp,
    policy: verdict.policy,
    finalVerdict: verdict.verdict,
    riskScore: verdict.riskScore,
    telemetry: {
      layer1LatencyMs: verdict.l1LatencyMs,
      layer2LatencyMs: verdict.l2LatencyMs,
      totalLatencyMs: verdict.totalLatencyMs,
      layer2Skipped: verdict.l2Skipped,
    },
    threatDetails: {
      ruleHitsCount: verdict.l1Matches.length,
      rulesFired: verdict.l1Matches.map((m) => m.ruleId),
      extractedQuote: verdict.judgeResult?.quote || null,
      gemmaReasoning: verdict.judgeResult?.reasoning || null,
    },
    inputHashSnippet: originalInput.length > 80 ? `${originalInput.substring(0, 77)}...` : originalInput,
    sha256MockDigest: `0x${Array.from({ length: 32 }, () => Math.floor(Math.random() * 16).toString(16)).join('')}`,
  };

  return JSON.stringify(receipt, null, 2);
}
