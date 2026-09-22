"""Comprehensive ATS (Applicant Tracking System) Scorer and Evaluator."""

from typing import Any, Dict, List


def calculate_ats_score(
    section_data: Dict[str, Any],
    skills_data: Dict[str, Any],
    format_data: Dict[str, Any],
    header_data: Dict[str, Any],
    repetition_data: Dict[str, Any],
    spelling_data: Dict[str, Any],
    job_match_score: float = 0.0,
    has_job_description: bool = False,
) -> Dict[str, Any]:
    """Computes a multi-dimensional ATS readiness score (0-100), letter grade, category sub-scores,

    and prioritized recommendations.
    """
    # 1. Essential Sections Score (0 - 100) -> 25% weight
    sections_score = section_data.get("score", 50)

    # 2. Skills & Keyword Richness Score (0 - 100) -> 25% weight
    # If job description is provided, blend skill richness and job match
    extracted_skills_count = len(skills_data.get("all_skills", []))
    raw_skills_score = min(100, int((extracted_skills_count / 10) * 100))
    if has_job_description:
        skills_score = round(0.5 * raw_skills_score + 0.5 * job_match_score)
    else:
        skills_score = raw_skills_score

    # 3. Format & Readability Score (0 - 100) -> 20% weight
    format_score = format_data.get("score", 60)

    # 4. Action Verbs & Quantifiable Impact Score (0 - 100) -> 15% weight
    verb_ratio = format_data.get("action_verb_ratio", 0)
    metrics_count = format_data.get("metrics_count", 0)
    impact_score = min(100, int(verb_ratio * 0.8 + min(10, metrics_count) * 6))

    # 5. Header Links & Contact Info Score (0 - 100) -> 15% weight
    header_score = header_data.get("score", 50)

    # Composite weighted ATS score
    weighted_score = (
        (sections_score * 0.25)
        + (skills_score * 0.25)
        + (format_score * 0.20)
        + (impact_score * 0.15)
        + (header_score * 0.15)
    )

    # Minor penalties for severe spelling errors
    spelling_errors = spelling_data.get("spelling_errors", 0)
    if spelling_errors > 3:
        weighted_score = max(20.0, weighted_score - min(10, (spelling_errors - 3) * 2))

    final_score = int(round(weighted_score))

    # Grade determination
    if final_score >= 90:
        grade = "A+"
        status = "Excellent ATS Readiness"
        color = "#10B981"  # Emerald Green
    elif final_score >= 80:
        grade = "A"
        status = "Strong ATS Compatibility"
        color = "#3B82F6"  # Blue
    elif final_score >= 70:
        grade = "B"
        status = "Good (Minor Tweaks Needed)"
        color = "#F59E0B"  # Amber
    elif final_score >= 60:
        grade = "C"
        status = "Fair (Needs Optimization)"
        color = "#EA580C"  # Orange
    else:
        grade = "D"
        status = "High Rejection Risk"
        color = "#EF4444"  # Red

    # Compile prioritized recommendations
    action_items: List[str] = []
    
    # Priority 1: Missing Essential Sections
    if section_data.get("missing_essential"):
        missing_str = ", ".join(section_data["missing_essential"])
        action_items.append(f"Add missing essential section(s): **{missing_str}**.")

    # Priority 2: Header Contacts
    if header_data.get("missing_items"):
        missing_headers = ", ".join(header_data["missing_items"])
        action_items.append(f"Add missing contact links: **{missing_headers}**.")

    # Priority 3: Quantifiable metrics
    if metrics_count < 3:
        action_items.append("Quantify your achievements with numbers, percentages, or dollar impacts (e.g. 'Improved speed by 35%').")

    # Priority 4: Action verbs
    if verb_ratio < 30:
        action_items.append("Begin bullet points with strong past-tense action verbs (e.g., 'Architected', 'Spearheaded', 'Optimized').")

    # Priority 5: Spelling/Grammar
    if spelling_errors > 0:
        action_items.append(f"Fix {spelling_errors} spelling/typo issue(s) flagged in the Spelling & Grammar tab.")

    # Priority 6: Skills density
    if extracted_skills_count < 6:
        action_items.append("List more technical skills and frameworks in your Skills section to pass keyword indexing.")

    # Priority 7: Buzzwords
    if repetition_data.get("buzzwords"):
        action_items.append("Replace vague buzzwords (e.g., 'hardworking', 'team player') with concrete evidence.")

    return {
        "final_score": final_score,
        "grade": grade,
        "status": status,
        "color": color,
        "sub_scores": {
            "Essential Sections": sections_score,
            "Skills & Keywords": skills_score,
            "Design & Format": format_score,
            "Action Verbs & Impact": impact_score,
            "Header Links & Contact": header_score,
        },
        "action_items": action_items[:5],
    }
