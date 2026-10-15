"""
Configuration dataclass and environment variable loader for PromptShield.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

@dataclass
class FirewallConfig:
    """Configurable thresholds and operational parameters for PromptShield."""
    model_name: str = field(
        default_factory=lambda: os.environ.get("PROMPTSHIELD_MODEL", "")
    )
    block_threshold: float = field(
        default_factory=lambda: float(os.environ.get("PROMPTSHIELD_BLOCK_THRESHOLD", "0.70"))
    )
    sanitize_threshold: float = field(
        default_factory=lambda: float(os.environ.get("PROMPTSHIELD_SANITIZE_THRESHOLD", "0.30"))
    )
    l1_confident_block_threshold: float = field(
        default_factory=lambda: float(os.environ.get("PROMPTSHIELD_L1_BLOCK_THRESHOLD", "0.90"))
    )
    request_timeout: float = field(
        default_factory=lambda: float(os.environ.get("PROMPTSHIELD_REQUEST_TIMEOUT", "10.0"))
    )
    max_retries: int = field(
        default_factory=lambda: int(os.environ.get("PROMPTSHIELD_MAX_RETRIES", "2"))
    )
    max_chunk_chars: int = field(
        default_factory=lambda: int(os.environ.get("PROMPTSHIELD_CHUNK_SIZE", "5000"))
    )
    chunk_overlap: int = field(
        default_factory=lambda: int(os.environ.get("PROMPTSHIELD_CHUNK_OVERLAP", "500"))
    )
