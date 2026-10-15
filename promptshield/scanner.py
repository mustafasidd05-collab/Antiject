"""
Layer 1: Fast Rule & Anomaly Scanner for PromptShield.
Detects invisible Unicode characters, HTML comment injections, and multilingual
prompt injection patterns (English, Hindi, Hinglish) without calling an LLM.
Hindi patterns are engineered without ASCII '\\b' boundaries to support Devanagari script.
"""

import re
from typing import List
from promptshield.models import RuleMatch

# 1. Unicode & Steganographic Anomaly Patterns
INVISIBLE_UNICODE_CHARS = {
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
}

# Unicode tag characters (U+E0000 to U+E007F) used for ASCII smuggling attacks
TAG_CHAR_PATTERN = re.compile(r'[\U000E0000-\U000E007F]')

# HTML Comment injection pattern: <!-- ignore instructions ... -->
HTML_COMMENT_PATTERN = re.compile(r'<!--(.*?)-->', re.DOTALL)

# 2. Multilingual Regular Expression Rules
PATTERNS = [
    # English Patterns
    (
        "L1-EN-IGNORE-PREVIOUS",
        "English: Ignore Previous Instructions",
        "regex_english",
        re.compile(
            r'\b(?:ignore|disregard|forget|override|bypass)\s+(?:all\s+)?(?:previous|prior|above|former|initial)\s+(?:instructions|prompts|directions|rules|commands)\b',
            re.IGNORECASE
        ),
        0.95
    ),
    (
        "L1-EN-SYSTEM-PROMPT",
        "English: System Prompt Injection",
        "regex_english",
        re.compile(
            r'\b(?:system\s+prompt|system\s+instructions|system\s+directive|developer\s+mode|assistant\s+notice)\s*[:=]',
            re.IGNORECASE
        ),
        0.90
    ),
    (
        "L1-EN-ROLE-OVERRIDE",
        "English: Role Hijacking / DAN Mode",
        "regex_english",
        re.compile(
            r'\b(?:you\s+are\s+now|act\s+as|pretend\s+you\s+are)\s+(?:an?\s+)?(?:unrestricted|jailbreak|dan|evil|hacked|new)\s+(?:ai|assistant|mode|persona)\b',
            re.IGNORECASE
        ),
        0.90
    ),
    (
        "L1-EN-CONCEALMENT",
        "English: Do Not Tell User",
        "regex_english",
        re.compile(
            r'\b(?:do\s+not|never|don\'?t)\s+(?:tell|reveal|inform|alert|warn)\s+(?:the\s+)?(?:user|human|administrator)\b',
            re.IGNORECASE
        ),
        0.85
    ),
    (
        "L1-EN-EXFILTRATION",
        "English: Data Exfiltration Directive",
        "regex_english",
        re.compile(
            r'\b(?:secretly|covertly|silently)\s+(?:send|email|forward|transmit|exfiltrate|post)\b',
            re.IGNORECASE
        ),
        0.85
    ),
    (
        "L1-EN-NEW-DIRECTIVE",
        "English: Explicit Directive Marker",
        "regex_english",
        re.compile(
            r'\b(?:new\s+instruction|new\s+directive|special\s+command)\s*:\s*(?:send|ignore|execute|call)',
            re.IGNORECASE
        ),
        0.80
    ),

    # Hindi (Devanagari) Patterns — NO '\b' used!
    (
        "L1-HI-IGNORE-PREVIOUS",
        "Hindi: Ignore Previous Instructions",
        "regex_hindi",
        re.compile(
            r'(?:^|[^\w\u0900-\u097F])(?:पिछले|पूर्व)\s+(?:सभी\s+)?(?:निर्देशों?|आदेशों?|प्रॉम्प्ट्स?)\s+(?:को\s+)?(?:भूल\s+जाएं|अनदेखा\s+करें|रद्द\s+करें|हटा\s+दें)(?:[^\w\u0900-\u097F]|$)',
            re.UNICODE
        ),
        0.95
    ),
    (
        "L1-HI-CONCEALMENT",
        "Hindi: Do Not Tell User",
        "regex_hindi",
        re.compile(
            r'(?:उपयोगकर्ता|यूजर)\s+को\s+(?:मत\s+बताना|सूचित\s+मत\s+करना|पता\s+ना\s+चले)',
            re.UNICODE
        ),
        0.85
    ),
    (
        "L1-HI-EXFILTRATION",
        "Hindi: Exfiltrate / Email Directive",
        "regex_hindi",
        re.compile(
            r'(?:गुप्त\s+रूप\s+से|चुपके\s+से)\s+(?:ईमेल\s+करें|भेजें|डेटा\s+निकालें)',
            re.UNICODE
        ),
        0.90
    ),
    (
        "L1-HI-SYSTEM-PROMPT",
        "Hindi: System Prompt Marker",
        "regex_hindi",
        re.compile(
            r'(?:सिस्टम|गुप्त)\s+(?:प्रॉम्प्ट|निर्देश)\s*[:=]',
            re.UNICODE
        ),
        0.85
    ),
    (
        "L1-HI-DIRECTIVE",
        "Hindi: General Order Directive",
        "regex_hindi",
        re.compile(
            r'(?:पिछले\s+आदेश\s+रद्द\s+करें|पासवर्ड\s+को\s+.*?पर\s+भेजें)',
            re.UNICODE
        ),
        0.85
    ),

    # Hinglish Patterns (Latin script Hindi/English mix)
    (
        "L1-HINGLISH-IGNORE",
        "Hinglish: Ignore Instructions",
        "regex_hinglish",
        re.compile(
            r'\b(?:pichle|purane)\s+(?:saare|sabhi)?\s*(?:instructions?|nirdesh|rules?|prompts?)\s+(?:ko\s+)?(?:bhool\s+jao|bhol\s+jao|bhool\s+ja|ignore\s+karo|cancel\s+karo)\b',
            re.IGNORECASE
        ),
        0.95
    ),
    (
        "L1-HINGLISH-CONCEALMENT",
        "Hinglish: User Ko Mat Batana",
        "regex_hinglish",
        re.compile(
            r'\b(?:user|kisi)\s+ko\s+(?:mat|nahi)\s+(?:batana|inform\s+karna|dikhaana|bina\s+bataye)\b',
            re.IGNORECASE
        ),
        0.85
    ),
    (
        "L1-HINGLISH-EXFILTRATION",
        "Hinglish: Secret Exfiltration Directive",
        "regex_hinglish",
        re.compile(
            r'\b(?:chupke\s+se|secretly)\s+(?:ye\s+)?(?:email\s+karo|bhejo|data\s+leak\s+karo)\b',
            re.IGNORECASE
        ),
        0.90
    ),
    (
        "L1-HINGLISH-DATA-SEND",
        "Hinglish: Send Data to Address",
        "regex_hinglish",
        re.compile(
            r'\b(?:ye|is)\s+(?:chat|data|history|files?)\s+(?:is\s+)?email\s+(?:pe|ko)\s+(?:send|bhej|forward)\b',
            re.IGNORECASE
        ),
        0.85
    ),
]


class Scanner:
    """
    Fast rule-based scanner for PromptShield (Layer 1).
    Performs deterministic pattern matching and steganography checks in milliseconds.
    """

    def scan(self, text: str) -> List[RuleMatch]:
        """
        Scans input text for invisible Unicode characters, hidden comments,
        and multilingual prompt injection expressions.
        """
        if not text:
            return []

        matches: List[RuleMatch] = []

        # 1. Check for invisible / zero-width Unicode characters
        for idx, char in enumerate(text):
            if char in INVISIBLE_UNICODE_CHARS:
                name = INVISIBLE_UNICODE_CHARS[char]
                matches.append(
                    RuleMatch(
                        rule_id="L1-UNICODE-INVISIBLE",
                        name=f"Invisible Unicode Character: {name}",
                        category="unicode",
                        start=idx,
                        end=idx + 1,
                        matched_text=repr(char),
                        severity=0.75,
                    )
                )

        # Check for Unicode tag characters (plane 14 ASCII smuggling)
        for tag_match in TAG_CHAR_PATTERN.finditer(text):
            matches.append(
                RuleMatch(
                    rule_id="L1-UNICODE-TAG-SMUGGLING",
                    name="Unicode Tag Character (ASCII Smuggling)",
                    category="unicode",
                    start=tag_match.start(),
                    end=tag_match.end(),
                    matched_text="[UNICODE_TAG_CHAR]",
                    severity=0.90,
                )
            )

        # 2. Check for hidden HTML comments
        for comment_match in HTML_COMMENT_PATTERN.finditer(text):
            comment_content = comment_match.group(1).strip()
            # If the comment contains directive-like words, flag with high severity
            is_suspicious = any(
                kw in comment_content.lower()
                for kw in ["ignore", "instruction", "system", "email", "send", "prompt", "secret"]
            )
            matches.append(
                RuleMatch(
                    rule_id="L1-HTML-COMMENT-HIDDEN",
                    name="Hidden HTML Comment Directive" if is_suspicious else "Hidden HTML Comment",
                    category="comment",
                    start=comment_match.start(),
                    end=comment_match.end(),
                    matched_text=comment_match.group(0),
                    severity=0.90 if is_suspicious else 0.50,
                )
            )

        # 3. Check multilingual regex patterns
        for rule_id, name, category, pattern, severity in PATTERNS:
            for match in pattern.finditer(text):
                matches.append(
                    RuleMatch(
                        rule_id=rule_id,
                        name=name,
                        category=category,
                        start=match.start(),
                        end=match.end(),
                        matched_text=match.group(0).strip(),
                        severity=severity,
                    )
                )

        return matches

    def clean_unicode(self, text: str) -> str:
        """Strips invisible Unicode characters from text."""
        cleaned = "".join(ch for ch in text if ch not in INVISIBLE_UNICODE_CHARS)
        cleaned = TAG_CHAR_PATTERN.sub("", cleaned)
        return cleaned
