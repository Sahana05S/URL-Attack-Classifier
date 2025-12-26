
import re
PATTERNS = {
    "SQL Injection": re.compile(r"(union|select|sleep|drop|--|'\s*or)", re.I),
    "XSS": re.compile(r"(<script|javascript:|onerror=|onload=)", re.I),
    "Directory Traversal": re.compile(r"(\.\./|%2e%2e%2f)", re.I),
    "Command Injection": re.compile(r"(;|&&|\|).*(ls|cat|pwd|whoami)", re.I),
    "SSRF": re.compile(r"(169\.254\.169\.254|metadata)", re.I)
}
def detect_attack(url):
    if not isinstance(url, str):
        return "Normal"
    for a, p in PATTERNS.items():
        if p.search(url.lower()):
            return a
    return "Normal"
