"""Header Links and Contact Information Analyzer."""

import re
from typing import Any, Dict, List, Optional


def extract_header_info(text: str) -> Dict[str, Any]:
    """Extracts contact details, professional profile links, and calculates a header score."""
    # Email regex
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    emails = re.findall(email_pattern, text)
    email = emails[0] if emails else None
    email_domain = email.split("@")[-1].lower() if email else ""

    # Phone regex (supports international, US, brackets, dashes, dots, spaces)
    phone_pattern = r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4}\b"
    phone_candidates = re.findall(phone_pattern, text)
    # Filter out potential dates or pure numbers < 10 digits
    valid_phones = [p.strip() for p in phone_candidates if sum(c.isdigit() for c in p) >= 10]
    phone = valid_phones[0] if valid_phones else None

    # LinkedIn profile regex
    linkedin_pattern = r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|pub)\/([A-Za-z0-9_-]+)\/?"
    linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
    linkedin_url = f"https://linkedin.com/in/{linkedin_matches[0]}" if linkedin_matches else None
    if not linkedin_url and "linkedin.com" in text.lower():
        simple_match = re.search(r"linkedin\.com\/[^\s\)\|]+", text, re.IGNORECASE)
        if simple_match:
            raw = simple_match.group(0).rstrip(".,;|")
            linkedin_url = f"https://{raw}" if not raw.startswith("http") else raw

    # GitHub profile regex
    github_pattern = r"(?:https?:\/\/)?(?:www\.)?github\.com\/([A-Za-z0-9_-]+)\/?"
    github_matches = re.findall(github_pattern, text, re.IGNORECASE)
    valid_github_users = [u for u in github_matches if u.lower() not in {"topics", "explore", "trending"}]
    github_url = f"https://github.com/{valid_github_users[0]}" if valid_github_users else None
    if not github_url and "github.com" in text.lower():
        simple_match = re.search(r"github\.com\/[^\s\)\|]+", text, re.IGNORECASE)
        if simple_match:
            raw = simple_match.group(0).rstrip(".,;|")
            github_url = f"https://{raw}" if not raw.startswith("http") else raw

    # Portfolio / Personal Website regex
    portfolio_pattern = r"(?:https?:\/\/)?(?:www\.)?([a-zA-Z0-9-]+\.(?:dev|me|io|tech|app|site|net|org|page|in|com)(?:\/[^\s\)\|]*)?)"
    all_domains = re.findall(portfolio_pattern, text, re.IGNORECASE)
    ignored_domains = {
        "linkedin.com", "github.com", "gmail.com", "yahoo.com", "outlook.com",
        "hotmail.com", "icloud.com", "email.com", "coursera.org", "udemy.com",
        "leetcode.com", "hackerrank.com"
    }
    if email_domain:
        ignored_domains.add(email_domain)

    portfolios = []
    for dom in all_domains:
        dom_clean = dom.rstrip(".,;|)")
        base = dom_clean.split("/")[0].lower()
        if not any(ign == base or base.endswith("." + ign) for ign in ignored_domains) and not base.endswith(".pdf"):
            full = f"https://{dom_clean}" if not dom_clean.startswith("http") else dom_clean
            portfolios.append(full)
    portfolio_url = portfolios[0] if portfolios else None

    # Location heuristic (City, State / Country)
    location_pattern = r"\b([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)?),\s*([A-Z]{2}|[A-Z][a-zA-Z]+)\b"
    locations = re.findall(location_pattern, text[:500])
    location = f"{locations[0][0]}, {locations[0][1]}" if locations else None

    # Calculate Header Score (0 - 100)
    score = 0
    checks = {
        "Email Address": {"found": email is not None, "value": email, "weight": 25},
        "Phone Number": {"found": phone is not None, "value": phone, "weight": 25},
        "LinkedIn Profile": {"found": linkedin_url is not None, "value": linkedin_url, "weight": 25},
        "GitHub / Portfolio": {"found": (github_url is not None or portfolio_url is not None),
                                "value": github_url or portfolio_url, "weight": 25},
    }

    missing_items: List[str] = []
    recommendations: List[str] = []

    for item, details in checks.items():
        if details["found"]:
            score += details["weight"]
        else:
            missing_items.append(item)
            recommendations.append(f"Add your {item} to the header so recruiters can reach out easily.")

    return {
        "score": score,
        "email": email,
        "phone": phone,
        "linkedin": linkedin_url,
        "github": github_url,
        "portfolio": portfolio_url,
        "location": location,
        "checks": checks,
        "missing_items": missing_items,
        "recommendations": recommendations,
    }
