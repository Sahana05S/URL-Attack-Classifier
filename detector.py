import re
from typing import List, Tuple

PATTERNS = {
    "SQL Injection": re.compile(r"(union|select|sleep|drop|--|'\s*or)", re.I),
    "XSS": re.compile(r"(<script|javascript:|onerror=|onload=)", re.I),
    "Directory Traversal": re.compile(r"(\.\./|%2e%2e%2f)", re.I),
    "Command Injection": re.compile(r"(;|&&|\|).*(ls|cat|pwd|whoami)", re.I),
    "SSRF": re.compile(r"(169\.254\.169\.254|metadata)", re.I),
}


def detect_attack(url: str) -> Tuple[str, List[str]]:
    """
    Detect attack type from URL based on regex signatures.
    Returns (label, hits) where hits are matched signature names.
    """
    if not isinstance(url, str):
        return "Normal", []

    hits: List[str] = []
    for name, pattern in PATTERNS.items():
        if pattern.search(url):
            hits.append(name)

    label = hits[0] if hits else "Normal"
    return label, hits
print(detect_attack("/login?id=1 OR 1=1"))
