"""Essential and auxiliary resume section analyzer."""

import re
from typing import Any, Dict, List
from analyzer.constants import ESSENTIAL_SECTIONS, SECTION_ALIASES
from analyzer.text_utils import normalize_heading


def extract_all_sections(text: str) -> Dict[str, str]:
    """Splits raw resume text into distinct named sections."""
    sections: Dict[str, List[str]] = {key: [] for key in SECTION_ALIASES}
    sections["other"] = []
    current_section = "other"

    lines = text.splitlines()
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        # Check if this line is likely a heading (short, doesn't end with a period, matches alias)
        if len(line.split()) <= 6:
            norm = normalize_heading(line)
            matched_key = None
            for key, aliases in SECTION_ALIASES.items():
                if norm in aliases or any(norm.startswith(alias) or norm.endswith(alias) for alias in aliases):
                    matched_key = key
                    break

            if matched_key:
                current_section = matched_key
                continue

        sections[current_section].append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items() if v}


def analyze_sections(sections_dict: Dict[str, str]) -> Dict[str, Any]:
    """Analyzes the presence, depth, and quality of essential and auxiliary resume sections."""
    total_essential = len(ESSENTIAL_SECTIONS)
    found_essential: List[Dict[str, Any]] = []
    missing_essential: List[str] = []
    recommendations: List[str] = []

    # Check each essential section
    for section_name in ESSENTIAL_SECTIONS:
        content = sections_dict.get(section_name, "").strip()
        if content:
            words = content.split()
            word_count = len(words)
            snippet = " ".join(words[:30]) + ("..." if word_count > 30 else "")
            
            # Depth check
            status_note = "Good depth"
            if section_name == "summary" and word_count < 25:
                status_note = "A bit brief (recommend 40-75 words)"
                recommendations.append("Expand your Summary section to 3-4 impactful sentences highlighting years of experience, core domains, and key achievements.")
            elif section_name == "experience" and word_count < 40:
                status_note = "Sparse (recommend detailed bullet points)"
                recommendations.append("Add more bullet points in Experience detailing responsibilities, tools used, and measurable outcomes.")

            found_essential.append({
                "section": section_name,
                "display_name": section_name.title(),
                "status": "Found",
                "word_count": word_count,
                "snippet": snippet,
                "note": status_note,
            })
        else:
            missing_essential.append(section_name.title())
            if section_name == "summary":
                recommendations.append("Add an Executive Summary / Professional Profile at the top to quickly convey your target role and value proposition.")
            elif section_name == "experience":
                recommendations.append("CRITICAL: Add an Experience / Work History section with bulleted accomplishments.")
            elif section_name == "education":
                recommendations.append("Add an Education section including your degree, institution, and graduation year.")
            elif section_name == "skills":
                recommendations.append("Add a dedicated Skills / Technical Proficiencies section to pass ATS keyword parsing.")
            elif section_name == "projects":
                recommendations.append("Add a Projects section demonstrating practical engineering implementations.")

    # Check auxiliary sections
    auxiliary_found: List[str] = []
    for aux in ["certifications", "achievements", "publications"]:
        if sections_dict.get(aux, "").strip():
            auxiliary_found.append(aux.title())

    # Calculate score (out of 100)
    # Experience (25), Skills (25), Education (20), Summary (15), Projects (15)
    weights = {
        "experience": 25,
        "skills": 25,
        "education": 20,
        "summary": 15,
        "projects": 15,
    }
    score = sum(weights[s["section"]] for s in found_essential)

    return {
        "score": score,
        "found_essential": found_essential,
        "missing_essential": missing_essential,
        "auxiliary_found": auxiliary_found,
        "total_essential": total_essential,
        "found_count": len(found_essential),
        "recommendations": recommendations,
    }
