"""Spelling and Grammar Analyzer with tech-aware dictionary, WordNet lemmatization, and grammar heuristics."""

import re
from typing import Any, Dict, List, Set

import nltk
from analyzer.constants import BUZZWORDS_AND_CLICHES, TECH_DICTIONARY
from analyzer.text_utils import split_sentences

# Lazy-loaded English lexicon set and lemmatizer
_ENGLISH_WORDS: Set[str] = set()
_LEMMATIZER = None


def _get_resources():
    """Returns cached English lexicon and WordNetLemmatizer."""
    global _ENGLISH_WORDS, _LEMMATIZER
    if not _ENGLISH_WORDS:
        try:
            from nltk.corpus import words
            _ENGLISH_WORDS = {w.lower() for w in words.words()}
        except (LookupError, AttributeError):
            try:
                nltk.download("words", quiet=True)
                from nltk.corpus import words
                _ENGLISH_WORDS = {w.lower() for w in words.words()}
            except Exception:
                _ENGLISH_WORDS = {"the", "and", "engineer", "software", "development", "data", "science", "system"}
        except Exception:
            _ENGLISH_WORDS = {"the", "and", "engineer", "software", "development", "data", "science", "system"}

        try:
            from nltk.stem import WordNetLemmatizer
            lem = WordNetLemmatizer()
            lem.lemmatize("testing", "v")
            _LEMMATIZER = lem
        except (LookupError, AttributeError):
            try:
                nltk.download("wordnet", quiet=True)
                from nltk.stem import WordNetLemmatizer
                _LEMMATIZER = WordNetLemmatizer()
            except Exception:
                _LEMMATIZER = None
        except Exception:
            _LEMMATIZER = None

        # Add tech terms, degrees, months, and common resume vocabulary
        _ENGLISH_WORDS.update(TECH_DICTIONARY)
        _ENGLISH_WORDS.update({
            "resume", "cv", "curriculum", "vitae", "gpa", "cgpa", "bachelor", "master",
            "phd", "btech", "mtech", "bsc", "msc", "mba", "intern", "internship",
            "developer", "engineer", "architect", "analyst", "consultant", "manager",
            "lead", "frontend", "backend", "fullstack", "devops", "cloud", "ai", "ml",
            "automating", "deploying", "refactoring", "containerizing", "optimizing",
            "scalable", "performant", "agile", "scrum", "sprint", "microservices",
            "repo", "repos", "sdk", "sdks", "api", "apis", "ui", "ux", "gui",
            "etl", "elt", "sql", "nosql", "ci", "cd", "cicd", "jan", "feb", "mar",
            "apr", "may", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
            "january", "february", "march", "april", "june", "july", "august",
            "september", "october", "november", "december", "present", "current",
            "san", "francisco", "austin", "california", "texas", "berkeley",
        })
    return _ENGLISH_WORDS, _LEMMATIZER


COMMON_TYPOS: Dict[str, str] = {
    "recieved": "received",
    "seperate": "separate",
    "definately": "definitely",
    "managment": "management",
    "develepor": "developer",
    "developper": "developer",
    "implimented": "implemented",
    "implimentation": "implementation",
    "achivement": "achievement",
    "achievment": "achievement",
    "experiance": "experience",
    "enviroment": "environment",
    "responisble": "responsible",
    "resposible": "responsible",
    "responsiblities": "responsibilities",
    "maintainance": "maintenance",
    "occurance": "occurrence",
    "programing": "programming",
    "succesful": "successful",
    "flawlessley": "flawlessly",
    "colaborated": "collaborated",
    "profecient": "proficient",
    "profficient": "proficient",
    "infrastucture": "infrastructure",
    "databse": "database",
    "algoritm": "algorithm",
    "analisis": "analysis",
    "teh": "the",
}


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Computes Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def is_valid_english_word(w: str, lexicon: Set[str], lemmatizer) -> bool:
    """Checks whether a word is valid English via lexicon, WordNet, lemmas, or common suffixes."""
    w_low = w.lower()
    if w_low in lexicon or w_low in TECH_DICTIONARY:
        return True

    # WordNet synsets check
    try:
        from nltk.corpus import wordnet
        if bool(wordnet.synsets(w_low)):
            return True
    except Exception:
        pass

    # Check lemmatization
    if lemmatizer:
        for pos in ["v", "n", "a", "r"]:
            try:
                lemma = lemmatizer.lemmatize(w_low, pos)
                if lemma in lexicon:
                    return True
                from nltk.corpus import wordnet
                if bool(wordnet.synsets(lemma)):
                    return True
            except Exception:
                pass

    # Suffix stripping heuristics (e.g. -ing, -ed, -es, -s, -ly, -ment, -tion, -able)
    suffixes = [
        ("ing", ""), ("ing", "e"), ("ed", ""), ("ed", "e"),
        ("es", ""), ("s", ""), ("ly", ""), ("ment", ""), ("able", "")
    ]
    for suf, repl in suffixes:
        if w_low.endswith(suf) and len(w_low) > len(suf) + 2:
            cand = w_low[:-len(suf)] + repl
            if cand in lexicon:
                return True
            try:
                from nltk.corpus import wordnet
                if bool(wordnet.synsets(cand)):
                    return True
            except Exception:
                pass

    return False


def find_suggestion(word: str, lexicon: Set[str]) -> str:
    """Finds the closest correction candidate for a misspelled word."""
    w_low = word.lower()
    if w_low in COMMON_TYPOS:
        return COMMON_TYPOS[w_low]

    candidates = [c for c in lexicon if len(c) >= 3 and abs(len(c) - len(w_low)) <= 1 and c[0] == w_low[0]]
    if not candidates:
        candidates = [c for c in lexicon if abs(len(c) - len(w_low)) <= 1]

    best_match = ""
    min_dist = 3
    for candidate in candidates[:800]:
        dist = _levenshtein_distance(w_low, candidate)
        if dist < min_dist:
            min_dist = dist
            best_match = candidate
            if dist == 1:
                break

    return best_match if best_match else "Check spelling"


def analyze_spelling_and_grammar(text: str) -> Dict[str, Any]:
    """Performs spell checking and heuristic grammar/style analysis."""
    lexicon, lemmatizer = _get_resources()
    issues: List[Dict[str, Any]] = []

    # 1. Spelling Check
    lines = text.splitlines()
    seen_misspellings: Set[str] = set()

    # Pre-extract URLs and emails to ignore their components
    urls_and_emails = set(re.findall(r"\bhttps?://[^\s]+|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b|\b[A-Za-z0-9-]+\.(?:com|org|dev|io|net|edu)\b", text))
    url_tokens = set()
    for item in urls_and_emails:
        url_tokens.update(re.findall(r"[A-Za-z]+", item.lower()))

    for line_idx, line in enumerate(lines, 1):
        clean_line = line.strip()
        if not clean_line:
            continue
        
        # Skip pure header link lines (e.g., https://... | email@...)
        if clean_line.startswith("http") or "@" in clean_line and "|" in clean_line:
            continue

        raw_words = re.findall(r"\b[A-Za-z]+(?:'[a-zA-Z]+)?\b", line)
        for w in raw_words:
            # Strip possessive 's or curly ’s
            if w.endswith("'s") or w.endswith("’s"):
                w = w[:-2]

            w_lower = w.lower()
            # Ignore 1-letter words, pure uppercase acronyms (AWS, SQL), or words in URLs/emails
            if len(w) <= 1 or w.isupper() or len(w) > 25 or w_lower in url_tokens:
                continue

            # CamelCase words (e.g. PyTorch, JavaScript, TechScale, CloudSphere)
            if re.match(r"^[A-Z][a-z]+[A-Z][a-z]+", w):
                continue

            # Capitalized words (e.g. Berkeley, California, Alex, Morgan, TechScale, Dean)
            # If capitalized and not the first word of a sentence or bullet
            if w.istitle() and not (clean_line.startswith(w) or clean_line.startswith("• " + w) or clean_line.startswith("- " + w)):
                continue

            # Check if valid English word
            if is_valid_english_word(w, lexicon, lemmatizer):
                continue

            if w_lower not in seen_misspellings:
                seen_misspellings.add(w_lower)
                suggestion = find_suggestion(w, lexicon)

                start = max(0, line.find(w) - 20)
                end = min(len(line), line.find(w) + len(w) + 20)
                snippet = "..." + line[start:end].strip() + "..."

                issues.append({
                    "type": "Spelling",
                    "severity": "Warning",
                    "word": w,
                    "suggestion": suggestion,
                    "line": line_idx,
                    "context": snippet,
                    "message": f"Possible spelling error '{w}'. Suggested: '{suggestion}'",
                })

    # 2. Grammar: Repeated Adjacent Words
    repeated_pattern = re.compile(r"\b([a-zA-Z]{2,})\s+\1\b", re.IGNORECASE)
    for line_idx, line in enumerate(lines, 1):
        for match in repeated_pattern.finditer(line):
            rep_word = match.group(1)
            issues.append({
                "type": "Grammar",
                "severity": "Error",
                "word": rep_word,
                "suggestion": rep_word,
                "line": line_idx,
                "context": match.group(0),
                "message": f"Repeated consecutive word detected: '{rep_word} {rep_word}'",
            })

    # 3. Grammar: Punctuation Spacing (space before comma/period)
    bad_spacing_pattern = re.compile(r"\b([a-zA-Z]+)\s+([,\.!\?:;])")
    for line_idx, line in enumerate(lines, 1):
        for match in bad_spacing_pattern.finditer(line):
            issues.append({
                "type": "Punctuation",
                "severity": "Warning",
                "word": match.group(0),
                "suggestion": f"{match.group(1)}{match.group(2)}",
                "line": line_idx,
                "context": match.group(0),
                "message": f"Unusual space before punctuation: '{match.group(0)}'",
            })

    # 4. Style: Weak / Passive Phrasing
    weak_phrases = {
        "responsible for": "Use strong action verbs like 'Engineered', 'Orchestrated', or 'Directed'",
        "duties included": "Rephrase using direct action verbs (e.g. 'Executed', 'Delivered')",
        "helped to": "Use 'Coordinated', 'Assisted', or state the exact part you built",
        "worked on": "Use 'Engineered', 'Developed', or 'Architected'",
        "tried to": "State the concrete achievement directly",
    }
    for phrase, suggestion in weak_phrases.items():
        if phrase in text.lower():
            issues.append({
                "type": "Style",
                "severity": "Recommendation",
                "word": phrase,
                "suggestion": suggestion,
                "line": "-",
                "context": f"Phrase: '{phrase}'",
                "message": f"Weak phrasing: '{phrase}'. {suggestion}",
            })

    spelling_count = sum(1 for i in issues if i["type"] == "Spelling")
    grammar_count = sum(1 for i in issues if i["type"] == "Grammar")
    other_count = len(issues) - (spelling_count + grammar_count)

    deductions = min(40, spelling_count * 4) + min(30, grammar_count * 5) + min(20, other_count * 2)
    score = max(35, 100 - deductions)

    return {
        "score": score,
        "total_issues": len(issues),
        "spelling_errors": spelling_count,
        "grammar_errors": grammar_count,
        "style_recommendations": other_count,
        "issues": issues,
    }
