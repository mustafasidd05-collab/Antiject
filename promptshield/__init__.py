"""
PromptShield: A 3-Layer Prompt-Injection Firewall for AI Agents.
"""

from promptshield.models import (
    Policy,
    ScanVerdict,
    RuleMatch,
    JudgeResult,
)
from promptshield.config import FirewallConfig
from promptshield.scanner import Scanner
from promptshield.judge import BaseJudge, GemmaJudge, MockJudge
from promptshield.firewall import (
    PromptShield,
    Firewall,
    Antiject,
    scan,
    scan_file,
    agent_system_note,
    get_firewall,
    escape_untrusted_delimiters,
    wrap_untrusted_data,
)
from promptshield.loaders import (
    load_file,
    load_text,
    load_pdf,
    load_html,
)

__version__ = "0.1.0"
__all__ = [
    "Antiject",
    "PromptShield",
    "Firewall",
    "scan",
    "scan_file",
    "agent_system_note",
    "get_firewall",
    "Policy",
    "ScanVerdict",
    "RuleMatch",
    "JudgeResult",
    "FirewallConfig",
    "Scanner",
    "BaseJudge",
    "GemmaJudge",
    "MockJudge",
    "load_file",
    "load_text",
    "load_pdf",
    "load_html",
    "escape_untrusted_delimiters",
    "wrap_untrusted_data",
]
