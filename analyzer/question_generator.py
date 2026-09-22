"""Interview question generator based on resume sections, skills, and CS core subjects."""

from typing import Dict, List, Set
from analyzer.constants import CORE_SUBJECTS, FIXED_QUESTIONS


def generate_interview_questions(
    sections: Dict[str, str],
    skills: Set[str],
    custom_core_questions: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    """Generates two-part interview questions:
    
    Part 1: Dynamic questions based on extracted resume sections and top skills.
    Part 2: Core CS fundamentals questions.
    """
    questions: Dict[str, List[str]] = {}

    # Part 1: Resume Section Questions
    for section_key, section_text in sections.items():
        if section_key in FIXED_QUESTIONS and section_text.strip():
            questions[f"Resume: {section_key.title()}"] = list(FIXED_QUESTIONS[section_key])

    # If top skills were detected, add targeted skill inquiry
    key_tech_skills = [s for s in skills if s in {"Python", "SQL", "Docker", "Machine Learning", "PyTorch", "React", "AWS", "Kubernetes"}]
    if key_tech_skills:
        sample_skill = key_tech_skills[0]
        questions["Resume: Technical Deep Dive"] = [
            f"You mentioned expertise in {sample_skill}. Describe a challenging production bug or optimization you tackled with it.",
            f"How do you evaluate design patterns and trade-offs when building solutions using {sample_skill}?",
        ]

    # Part 2: CS Core Subjects Questions
    for subject in CORE_SUBJECTS:
        custom_list = custom_core_questions.get(subject, [])
        cleaned = [q.strip() for q in custom_list if q.strip()]
        defaults = [
            f"Explain a core practical concept in {subject} and a real-world scenario where it is critical.",
            f"What is a classic engineering problem or performance bottleneck related to {subject}?",
        ]
        questions[f"Core CS: {subject}"] = (cleaned + defaults)[:2]

    return questions
