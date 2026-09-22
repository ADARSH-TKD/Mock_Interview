"""Repetition, Buzzwords, and Vocabulary Diversity Analyzer."""

import collections
import re
from typing import Any, Dict, List, Tuple

from analyzer.constants import ACTION_VERB_SYNONYMS, ACTION_VERBS, BUZZWORDS_AND_CLICHES

COMMON_STOP_WORDS = {
    "the", "and", "to", "of", "a", "in", "for", "is", "on", "that", "by", "this",
    "with", "i", "you", "it", "not", "or", "be", "are", "from", "at", "as", "your",
    "all", "have", "new", "more", "an", "was", "we", "will", "home", "can", "us",
    "about", "if", "my", "has", "into", "their", "them", "these", "those", "our",
}


def analyze_repetition(text: str) -> Dict[str, Any]:
    """Analyzes word repetition, buzzword frequency, repeated action verbs, and vocabulary diversity."""
    # Tokenize words
    words = [w.lower() for w in re.findall(r"\b[A-Za-z]{3,}\b", text)]
    total_words = len(words)
    unique_words = len(set(words))

    # Type-Token Ratio (Lexical Diversity)
    ttr = round((unique_words / max(1, total_words)), 3)
    ttr_percentage = round(ttr * 100, 1)

    # Filter out stopwords for frequency count
    filtered_words = [w for w in words if w not in COMMON_STOP_WORDS]
    word_counts = collections.Counter(filtered_words)

    # Top repeated words (excluding common section names)
    excluded_headings = {"experience", "education", "skills", "projects", "summary", "university"}
    top_repeated: List[Tuple[str, int]] = [
        (word, count) for word, count in word_counts.most_common(20)
        if word not in excluded_headings and count >= 3
    ]

    # Detect buzzwords and clichés
    lower_text = text.lower()
    found_buzzwords: List[Dict[str, Any]] = []
    for buzz in BUZZWORDS_AND_CLICHES:
        count = len(re.findall(r"\b" + re.escape(buzz) + r"\b", lower_text))
        if count > 0:
            found_buzzwords.append({
                "buzzword": buzz,
                "count": count,
                "recommendation": f"Replace generic buzzword '{buzz}' with concrete achievements and measurable results.",
            })

    # Detect overused action verbs and provide synonyms
    action_verb_counts: Dict[str, int] = collections.defaultdict(int)
    for w in words:
        if w in ACTION_VERBS:
            action_verb_counts[w] += 1

    overused_verbs: List[Dict[str, Any]] = []
    for verb, count in sorted(action_verb_counts.items(), key=lambda x: x[1], reverse=True):
        if count >= 3:
            synonyms = ACTION_VERB_SYNONYMS.get(verb, ["spearheaded", "orchestrated", "engineered", "streamlined"])
            overused_verbs.append({
                "verb": verb,
                "count": count,
                "synonyms": synonyms,
                "recommendation": f"The verb '{verb}' is used {count} times. Vary your language with: {', '.join(synonyms)}.",
            })

    # Repetition score (0 - 100)
    # Higher is better (meaning diverse vocabulary and no buzzwords)
    score = 100
    # Penalty for buzzwords (-5 per buzzword instance, max -30)
    total_buzzword_instances = sum(b["count"] for b in found_buzzwords)
    score -= min(30, total_buzzword_instances * 5)

    # Penalty for overused verbs (-4 per overused verb, max -20)
    score -= min(20, len(overused_verbs) * 4)

    # Lexical diversity evaluation (TTR)
    if ttr < 0.35:
        score -= 20
    elif ttr < 0.45:
        score -= 10

    score = max(25, min(100, score))

    return {
        "score": score,
        "total_words": total_words,
        "unique_words": unique_words,
        "lexical_diversity_ttr": ttr,
        "ttr_percentage": ttr_percentage,
        "top_repeated_words": top_repeated[:10],
        "buzzwords": found_buzzwords,
        "overused_verbs": overused_verbs,
    }
