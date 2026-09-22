"""Resume Design, Format, and Visual Structure Analyzer."""

import re
from typing import Any, Dict, List, Optional
from analyzer.constants import ACTION_VERBS


def analyze_format_and_design(text: str, pdf_pages: Optional[int] = None) -> Dict[str, Any]:
    """Evaluates formatting, structure, bullet point density, action verbs, and quantifiable metrics."""
    words = re.findall(r"\b[A-Za-z0-9+#.-]+\b", text)
    word_count = len(words)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    line_count = len(lines)

    # Page estimate: either actual PDF pages or word-count heuristic
    if pdf_pages and pdf_pages > 0:
        estimated_pages = pdf_pages
    else:
        # standard 1-page resume is ~350-650 words
        estimated_pages = max(1, round(word_count / 500))

    # Bullet points detection
    bullet_regex = re.compile(r"^[\s]*[•\-\*\▪\–\>\✓\✔\⁃\⁃\u2022\u2023\u25E6\u2043\u2219]")
    bullet_lines = [line for line in lines if bullet_regex.match(line)]
    bullet_count = len(bullet_lines)
    bullet_ratio = round((bullet_count / max(1, line_count)) * 100, 1)

    # Action verbs at beginning of bullet points or statements
    action_verb_bullets: List[str] = []
    for line in (bullet_lines if bullet_lines else lines):
        # strip bullet marker
        clean = re.sub(r"^[•\-\*\▪\–\>\✓\✔\⁃\s]+", "", line).strip()
        first_word = clean.split()[0].lower() if clean.split() else ""
        # remove punctuation from first word
        first_word = re.sub(r"[^a-z]", "", first_word)
        if first_word in ACTION_VERBS:
            action_verb_bullets.append(clean)

    action_verb_ratio = round((len(action_verb_bullets) / max(1, len(bullet_lines or lines))) * 100, 1)

    # Quantifiable metrics & achievements detection (e.g., numbers, %, $, x-factor)
    metrics_regex = re.compile(r"(\b\d+(?:\.\d+)?%|\$\s?\d+(?:,\d+)*(?:\.\d+)?(?:k|m|b)?|\b\d+\s?(?:x|times|users|clients|engineers|people|projects|datasets|models)\b|\b\d{2,}\b)", re.IGNORECASE)
    lines_with_metrics: List[str] = []
    for line in lines:
        if metrics_regex.search(line):
            lines_with_metrics.append(line)

    metrics_count = len(lines_with_metrics)
    metrics_ratio = round((metrics_count / max(1, line_count)) * 100, 1)

    # Long text walls (> 70 words without a break)
    text_walls = [line for line in lines if len(line.split()) > 70]

    # Format scoring rubric (0 - 100)
    # Length appropriateness: 25 pts
    # Bullet points usage: 25 pts
    # Action verbs starts: 25 pts
    # Quantifiable metrics: 25 pts
    score = 0
    feedback: List[str] = []
    positive_highlights: List[str] = []

    # 1. Length
    if 350 <= word_count <= 1100:
        score += 25
        positive_highlights.append(f"Optimal resume length ({word_count} words, ~{estimated_pages} page(s)).")
    elif word_count < 300:
        score += 12
        feedback.append(f"Resume is very brief ({word_count} words). Consider elaborating on key technical projects and experience.")
    else:
        score += 18
        feedback.append(f"Resume is quite long ({word_count} words). Aim for a concise 1-2 page format.")

    # 2. Bullet points
    if bullet_count >= 8:
        score += 25
        positive_highlights.append(f"Great use of bullet points ({bullet_count} bullets, {bullet_ratio}% of lines).")
    elif bullet_count >= 4:
        score += 17
        feedback.append("Increase the proportion of bullet points for better recruiter readability.")
    else:
        score += 8
        feedback.append("Resume contains very few bullet points. Convert text blocks into concise bulleted accomplishments.")

    # 3. Action verbs
    if action_verb_ratio >= 40:
        score += 25
        positive_highlights.append(f"Strong action verb presence ({action_verb_ratio}% of bullets begin with powerful verbs).")
    elif action_verb_ratio >= 20:
        score += 16
        feedback.append("Start more bullet points with strong past-tense action verbs (e.g. 'Architected', 'Spearheaded', 'Optimized').")
    else:
        score += 8
        feedback.append("Few bullet points begin with impact action verbs. Replace passive phrases with decisive action verbs.")

    # 4. Quantifiable metrics
    if metrics_count >= 5:
        score += 25
        positive_highlights.append(f"Excellent quantifiable impact detected ({metrics_count} lines contain numbers, % or metrics).")
    elif metrics_count >= 2:
        score += 16
        feedback.append("Add more measurable metrics (e.g., '% improved', '$ saved', 'number of users served') to prove your impact.")
    else:
        score += 8
        feedback.append("No or very few quantifiable metrics found. Use the XYZ formula: 'Accomplished [X] as measured by [Y] by doing [Z]'.")

    # Text walls penalty
    if text_walls:
        score = max(20, score - 8)
        feedback.append(f"Found {len(text_walls)} dense paragraph(s) with over 70 words. Break these into 2-3 concise bullets.")

    return {
        "score": score,
        "word_count": word_count,
        "estimated_pages": estimated_pages,
        "line_count": line_count,
        "bullet_count": bullet_count,
        "bullet_ratio": bullet_ratio,
        "action_verb_count": len(action_verb_bullets),
        "action_verb_ratio": action_verb_ratio,
        "metrics_count": metrics_count,
        "metrics_ratio": metrics_ratio,
        "sample_metrics_lines": lines_with_metrics[:4],
        "positive_highlights": positive_highlights,
        "feedback": feedback,
    }
