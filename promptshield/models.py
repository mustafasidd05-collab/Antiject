"""
Data models and schemas for PromptShield.
"""

from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field

class Policy(str, Enum):
    STRICT = "STRICT"
    BALANCED = "BALANCED"
    PERMISSIVE = "PERMISSIVE"

class RuleMatch(BaseModel):
    rule_id: str
    name: str
    category: str  # "unicode", "comment", "regex_english", "regex_hindi", "regex_hinglish"
    start: int
    end: int
    matched_text: str
    severity: float = Field(default=0.8, ge=0.0, le=1.0)

class JudgeResult(BaseModel):
    is_attack: bool
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    quote: Optional[str] = None
    quote_verified: bool = False
    reason: str = ""
    model_name: str = "MockJudge"
    is_simulation: bool = True
    latency_ms: float = 0.0

class ScanVerdict(BaseModel):
    verdict: Literal["ALLOW", "SANITIZE", "BLOCK"]
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    layer1_triggered: bool = False
    layer1_matches: list[RuleMatch] = Field(default_factory=list)
    layer2_triggered: bool = False
    layer2_skipped: bool = False
    judge_available: bool = True
    judge_error: Optional[str] = None
    judge_result: Optional[JudgeResult] = None
    clean_text: Optional[str] = None
    wrapped_text: str = ""
    reasons: list[str] = Field(default_factory=list)
    latency_breakdown: dict[str, float] = Field(default_factory=dict)
    model_label: str = "MockJudge (Local Simulation - No API Key)"
