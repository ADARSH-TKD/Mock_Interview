"""Job description matching and skill extraction engine."""

import re
from typing import Dict, List, Set, Tuple

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from analyzer.constants import SKILL_GROUPS


def build_spacy_pipeline():
    """Builds a cached lightweight spaCy entity ruler for fast skill recognition."""
    nlp = spacy.blank("en")
    if "entity_ruler" not in nlp.pipe_names:
        ruler = nlp.add_pipe("entity_ruler")
        patterns = []
        for label, terms in SKILL_GROUPS.items():
            for term in terms:
                patterns.append({"label": "SKILL", "pattern": term})
        patterns += [
            {"label": "EDUCATION", "pattern": "Bachelor"},
            {"label": "EDUCATION", "pattern": "Master"},
            {"label": "EDUCATION", "pattern": "Ph.D."},
            {"label": "ROLE", "pattern": "Data Scientist"},
            {"label": "ROLE", "pattern": "Software Engineer"},
            {"label": "ROLE", "pattern": "Machine Learning Engineer"},
            {"label": "ROLE", "pattern": "DevOps Engineer"},
            {"label": "ROLE", "pattern": "Full Stack Developer"},
        ]
        ruler.add_patterns(patterns)
    return nlp


# Cache pipeline instance
_NLP_INSTANCE = None


def get_nlp():
    global _NLP_INSTANCE
    if _NLP_INSTANCE is None:
        _NLP_INSTANCE = build_spacy_pipeline()
    return _NLP_INSTANCE


def extract_skills(text: str) -> Set[str]:
    """Extracts known technical and domain skills from text."""
    found: Set[str] = set()
    lower_text = text.lower()

    # Regex search for skill group aliases
    for canonical_name, terms in SKILL_GROUPS.items():
        for term in terms:
            # Word boundary regex with support for C++, C#, etc.
            escaped = re.escape(term)
            if term in {"c++", "c#"}:
                pattern = rf"(?:^|[\s,;()]){escaped}(?:$|[\s,;()])"
            else:
                pattern = rf"\b{escaped}\b"

            if re.search(pattern, lower_text):
                found.add(canonical_name)
                break

    # Also run spaCy entity ruler
    try:
        nlp = get_nlp()
        doc = nlp(text[:10000])  # process first 10k chars
        for ent in doc.ents:
            if ent.label_ == "SKILL":
                # Find matching canonical group
                ent_text = ent.text.lower()
                for canonical_name, terms in SKILL_GROUPS.items():
                    if ent_text in terms:
                        found.add(canonical_name)
    except Exception:
        pass

    return found


def infer_main_stream(skills: Set[str]) -> str:
    """Infers career track/stream from detected technical skills."""
    stream_scores = {
        "AI / Machine Learning": sum(s in skills for s in {
            "Machine Learning", "Deep Learning", "NLP", "TensorFlow", "PyTorch", "Hugging Face", "LLMs / GenAI", "Computer Vision"
        }),
        "Data Science & Analytics": sum(s in skills for s in {
            "Python", "SQL", "Pandas", "NumPy", "Scikit-learn", "BigQuery", "Snowflake", "Spark", "Matplotlib"
        }),
        "Software Engineering (Full Stack / Backend)": sum(s in skills for s in {
            "Python", "Java", "C++", "JavaScript", "TypeScript", "React", "Node.js", "Django", "FastAPI", "RESTful APIs"
        }),
        "Cloud & DevOps": sum(s in skills for s in {
            "AWS", "GCP", "Azure", "Docker", "Kubernetes", "CI/CD", "Linux / Bash", "Terraform", "Git"
        }),
        "Database & Data Engineering": sum(s in skills for s in {
            "SQL", "DBMS", "MongoDB", "Redis", "Kafka", "PostgreSQL", "Elasticsearch"
        }),
    }
    best_stream = max(stream_scores, key=stream_scores.get) if max(stream_scores.values(), default=0) > 0 else "General Software & Computer Science"
    return best_stream


def match_with_job(resume_text: str, job_text: str) -> Dict[str, Any]:
    """Computes TF-IDF cosine similarity, matched skills, and missing skills."""
    if not job_text.strip():
        return {
            "match_score": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "resume_skills": sorted(list(extract_skills(resume_text))),
            "job_skills": [],
        }

    # Vectorize texts
    try:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=2000)
        matrix = vectorizer.fit_transform([resume_text, job_text])
        cos_sim = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100)
    except Exception:
        cos_sim = 0.0

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)

    matched = resume_skills & job_skills
    missing = job_skills - resume_skills

    # Bonus keyword overlap score
    skill_match_ratio = (len(matched) / max(1, len(job_skills))) * 100 if job_skills else cos_sim
    composite_match = round(0.5 * cos_sim + 0.5 * skill_match_ratio, 1)

    return {
        "match_score": min(100.0, composite_match),
        "cosine_similarity": round(cos_sim, 1),
        "matched_skills": sorted(list(matched)),
        "missing_skills": sorted(list(missing)),
        "resume_skills": sorted(list(resume_skills)),
        "job_skills": sorted(list(job_skills)),
    }
