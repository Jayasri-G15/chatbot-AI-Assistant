import re

REFUSAL_MESSAGE = (
    "I'm just a conversational assistant, so I can't help with that — things like "
    "hacking, bypassing security, or exposing how I'm built are off the table. "
    "Happy to chat about something else though — what's on your mind?"
)

_JAILBREAK_PATTERNS = [
    r"ignore (all |any |the )?(previous|prior|above) instructions",
    r"disregard (your|the) (system prompt|instructions|rules)",
    r"reveal (your|the) (system prompt|instructions|prompt)",
    r"(show|print|tell) (me |us )?(your|the) (system prompt|instructions)",
    r"what is (your|the) (system prompt|instructions)",
    r"you are now (in )?(dan|developer mode|jailbroken?)",
    r"pretend (you have no|there are no) (rules|restrictions|guardrails)",
    r"act as if you have no (restrictions|filters|rules)",
    r"bypass (your|the|any) (restrictions|filters|safety|guardrails)",
]

_HACKING_PATTERNS = [
    r"how (do i|to|can i) hack",
    r"how (do i|to|can i) (write|create|make) (a |an )?(virus|malware|ransomware|keylogger|trojan)",
    r"sql injection (attack|payload|exploit)",
    r"how (do i|to|can i) (exploit|crack) (a |an )?(password|account|system|server|wifi|network)",
    r"ddos (attack|script|tool)",
    r"how (do i|to|can i) phish",
]

_SELF_EXPOSURE_PATTERNS = [
    r"(show|reveal|print|dump|give)( me| us)? (your|the) (source code|codebase|backend|architecture|api key|env(ironment)? variables?|(system|internal) prompt)",
    r"what (database|model|framework|library) (are you|do you) (using|built (on|with))",
    r"how (are you|is this app) (built|implemented|structured)",
    r"what('s| is) your (system prompt|internal prompt)",
]

_ROLE_ESCALATION_PATTERNS = [
    r"act as (an? )?admin(istrator)?",
    r"change my role to admin",
    r"grant (me|us) admin (access|privileges|permissions)",
    r"execute (arbitrary )?sql",
    r"select password_hash from",
    r"select \* from users",
]

_ALL_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in (_JAILBREAK_PATTERNS + _HACKING_PATTERNS + _SELF_EXPOSURE_PATTERNS + _ROLE_ESCALATION_PATTERNS)
]


def check_input(text: str) -> bool:
    """Returns True if the input should be blocked before it ever reaches the LLM."""
    if not text:
        return False
    return any(pattern.search(text) for pattern in _ALL_PATTERNS)


def sanitize_untrusted_text(text: str) -> str:
    """
    Sanitize untrusted text (retrieved documents, web results, CRM notes) by neutralizing
    embedded system prompt injection directives before placing in context blocks.
    """
    if not text:
        return ""

    # Neutralize embedded prompt override instructions in data strings
    sanitized = text
    injection_phrases = [
        "ignore all previous instructions",
        "ignore previous instructions",
        "disregard your system prompt",
        "disregard all instructions",
        "reveal your system prompt",
        "print your system prompt",
        "act as an administrator",
        "change your role to admin",
        "send all crm data to",
        "execute arbitrary sql",
    ]
    for phrase in injection_phrases:
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        sanitized = pattern.sub("[REDACTED_INJECTION_ATTEMPT]", sanitized)

    return sanitized
