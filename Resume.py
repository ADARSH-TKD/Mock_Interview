"""AI Resume Analyzer, ATS Scorer, and Multi-Parameter Evaluation Engine.

Provides deep evaluation across ATS score, Spelling & Grammar, Resume Design & Format,
Header Links, Essential Sections, Repetition & Buzzwords, Job Matching, and Interview Prep.
"""

import io
import json
import re
from typing import Any, Dict, List, Optional

import streamlit as st

from analyzer.ats_scorer import calculate_ats_score
from analyzer.constants import CORE_SUBJECTS
from analyzer.format_analyzer import analyze_format_and_design
from analyzer.header_analyzer import extract_header_info
from analyzer.job_matcher import extract_skills, infer_main_stream, match_with_job
from analyzer.question_generator import generate_interview_questions
from analyzer.repetition_analyzer import analyze_repetition
from analyzer.sample_data import SAMPLE_JOB_DESCRIPTION, SAMPLE_RESUME_TEXT
from analyzer.section_analyzer import analyze_sections, extract_all_sections
from analyzer.spelling_grammar import analyze_spelling_and_grammar
from analyzer.text_utils import extract_pdf_text_and_meta


def set_custom_styles() -> None:
    """Injects modern, polished CSS styling into the Streamlit app."""
    st.markdown(
        """
        <style>
            /* Main container polish */
            .main .block-container {
                padding-top: 1.8rem;
                padding-bottom: 3rem;
                max-width: 1200px;
            }
            /* Hero metric card */
            .hero-card {
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 1.5rem;
                color: #f8fafc;
                margin-bottom: 1.2rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }
            .hero-score {
                font-size: 3.5rem;
                font-weight: 800;
                line-height: 1;
                margin: 0;
            }
            .hero-grade {
                display: inline-block;
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-weight: 700;
                font-size: 1rem;
                margin-left: 0.8rem;
            }
            /* Parameter card */
            .param-card {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 1.2rem;
                margin-bottom: 1rem;
                transition: transform 0.15s ease, box-shadow 0.15s ease;
            }
            .param-card:hover {
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
            }
            /* Dark mode support */
            @media (prefers-color-scheme: dark) {
                .param-card {
                    background-color: #1e293b;
                    border-color: #334155;
                    color: #f1f5f9;
                }
            }
            /* Pills / Badges */
            .badge-success {
                background-color: #dcfce7;
                color: #166534;
                padding: 0.2rem 0.6rem;
                border-radius: 6px;
                font-weight: 600;
                font-size: 0.85rem;
                display: inline-block;
            }
            .badge-warning {
                background-color: #fef3c7;
                color: #92400e;
                padding: 0.2rem 0.6rem;
                border-radius: 6px;
                font-weight: 600;
                font-size: 0.85rem;
                display: inline-block;
            }
            .badge-danger {
                background-color: #fee2e2;
                color: #991b1b;
                padding: 0.2rem 0.6rem;
                border-radius: 6px;
                font-weight: 600;
                font-size: 0.85rem;
                display: inline-block;
            }
            .badge-neutral {
                background-color: #f1f5f9;
                color: #334155;
                padding: 0.2rem 0.6rem;
                border-radius: 6px;
                font-weight: 500;
                font-size: 0.85rem;
                display: inline-block;
            }
            .skill-pill-matched {
                background-color: #e0f2fe;
                color: #0369a1;
                border: 1px solid #bae6fd;
                border-radius: 16px;
                padding: 0.25rem 0.75rem;
                font-size: 0.85rem;
                font-weight: 600;
                margin: 0.2rem;
                display: inline-block;
            }
            .skill-pill-missing {
                background-color: #fef2f2;
                color: #b91c1c;
                border: 1px solid #fecaca;
                border-radius: 16px;
                padding: 0.25rem 0.75rem;
                font-size: 0.85rem;
                font-weight: 600;
                margin: 0.2rem;
                display: inline-block;
            }
            .recommendation-box {
                background-color: #f8fafc;
                border-left: 4px solid #3b82f6;
                padding: 0.8rem 1rem;
                border-radius: 0 8px 8px 0;
                margin: 0.5rem 0;
                font-size: 0.95rem;
            }
            @media (prefers-color-scheme: dark) {
                .recommendation-box {
                    background-color: #0f172a;
                    border-left-color: #60a5fa;
                    color: #cbd5e1;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def run_full_analysis(
    resume_text: str,
    job_description: str,
    pdf_pages: Optional[int] = None,
    custom_core: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Any]:
    """Executes all parameter analyzers across the resume."""
    if custom_core is None:
        custom_core = {}

    # 1. Sections Analysis (Essential & Auxiliary)
    raw_sections = extract_all_sections(resume_text)
    section_data = analyze_sections(raw_sections)

    # 2. Header Links & Contact Information
    header_data = extract_header_info(resume_text)

    # 3. Resume Design & Format
    format_data = analyze_format_and_design(resume_text, pdf_pages=pdf_pages)

    # 4. Spelling & Grammar Heuristics
    spelling_data = analyze_spelling_and_grammar(resume_text)

    # 5. Repetition, Buzzwords & Lexical Diversity
    repetition_data = analyze_repetition(resume_text)

    # 6. Technical Skills & Main Stream Inference
    skills = extract_skills(resume_text)
    main_stream = infer_main_stream(skills)
    skills_data = {
        "all_skills": sorted(list(skills)),
        "main_stream": main_stream,
    }

    # 7. Job Matching (if job description provided)
    has_jd = bool(job_description.strip())
    job_data = match_with_job(resume_text, job_description)

    # 8. ATS Score Computation
    ats_data = calculate_ats_score(
        section_data=section_data,
        skills_data=skills_data,
        format_data=format_data,
        header_data=header_data,
        repetition_data=repetition_data,
        spelling_data=spelling_data,
        job_match_score=job_data["match_score"],
        has_job_description=has_jd,
    )

    # 9. Interview Question Generation
    questions = generate_interview_questions(raw_sections, skills, custom_core)

    return {
        "resume_text": resume_text,
        "job_description": job_description,
        "ats": ats_data,
        "sections": section_data,
        "raw_sections": raw_sections,
        "header": header_data,
        "format": format_data,
        "spelling": spelling_data,
        "repetition": repetition_data,
        "skills": skills_data,
        "job_match": job_data,
        "questions": questions,
    }


def main() -> None:
    st.set_page_config(
        page_title="AI Resume Analyzer & ATS Evaluation Engine",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    set_custom_styles()

    # Sidebar: Configurations and Core Question Bank
    with st.sidebar:
        st.title("⚙️ Configurations")
        st.markdown("**Core CS Question Bank**")
        st.caption("Customize interview questions for Part 2:")
        core_questions: Dict[str, List[str]] = {}
        for subject in CORE_SUBJECTS:
            raw = st.text_area(
                subject,
                value="\n".join([
                    f"Explain a practical {subject} concept in distributed systems.",
                    f"What is a common architectural trade-off in {subject}?",
                ]),
                height=75,
                key=f"core_q_{subject}",
            )
            core_questions[subject] = [line.strip() for line in raw.splitlines() if line.strip()]

        st.divider()
        st.markdown("**Sample Profile**")
        if st.button("🚀 Load Sample Resume & Job", use_container_width=True):
            st.session_state["resume_input_text"] = SAMPLE_RESUME_TEXT
            st.session_state["job_input_text"] = SAMPLE_JOB_DESCRIPTION
            st.session_state["auto_analyze"] = True
            st.rerun()

    # Header Title Banner
    st.title("📄 AI Resume Analyzer & ATS Readiness Engine")
    st.caption("Comprehensive evaluation of ATS score, Spelling & Grammar, Design & Format, Header Links, Essential Sections, Repetition, and Job Alignment.")

    # Input Section
    col_input1, col_input2 = st.columns([1, 1])

    with col_input1:
        st.subheader("1. Resume Input")
        uploaded_file = st.file_uploader("Upload resume file (PDF or TXT)", type=["pdf", "txt"])
        
        default_resume = st.session_state.get("resume_input_text", "")
        resume_text_area = st.text_area(
            "Or paste resume text directly:",
            value=default_resume,
            height=200,
            placeholder="Paste raw resume text here...",
            key="resume_text_area_key",
        )

    with col_input2:
        st.subheader("2. Target Job Description (Optional)")
        default_jd = st.session_state.get("job_input_text", "")
        job_text_area = st.text_area(
            "Paste target job description for keyword matching:",
            value=default_jd,
            height=265,
            placeholder="Paste job posting / requirements here to calculate keyword overlap and skill gap...",
            key="job_text_area_key",
        )

    # Action Buttons
    c_btn1, c_btn2 = st.columns([3, 1])
    with c_btn1:
        analyze_clicked = st.button("🔍 Analyze Resume Across All Parameters", type="primary", use_container_width=True)
    with c_btn2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # Determine execution
    should_run = analyze_clicked or st.session_state.get("auto_analyze", False)

    if should_run:
        st.session_state["auto_analyze"] = False
        pdf_page_count = None
        extracted_text = ""

        with st.spinner("Analyzing resume structure, parameters, grammar, and ATS compatibility..."):
            try:
                if uploaded_file is not None:
                    file_bytes = uploaded_file.getvalue()
                    if uploaded_file.name.lower().endswith(".pdf"):
                        extracted_text, pdf_page_count, is_empty = extract_pdf_text_and_meta(file_bytes)
                        if is_empty:
                            st.warning("⚠️ The uploaded PDF has minimal text. It might be a scanned image. For best results, use a text-based PDF or paste text.")
                    else:
                        extracted_text = file_bytes.decode("utf-8", errors="ignore")
                else:
                    extracted_text = resume_text_area

                if not extracted_text.strip():
                    st.error("Please upload a PDF/TXT file or paste your resume text to begin analysis.")
                    return

                # Run full suite
                analysis_results = run_full_analysis(
                    resume_text=extracted_text,
                    job_description=job_text_area,
                    pdf_pages=pdf_page_count,
                    custom_core=core_questions,
                )
                st.session_state["analysis_results"] = analysis_results
            except Exception as e:
                st.error(f"Error during resume analysis: {str(e)}")
                return

    # Check if results exist
    results = st.session_state.get("analysis_results")
    if not results:
        st.info("💡 Upload your resume or click 'Load Sample Resume & Job' in the sidebar to view full parameter analysis.")
        return

    # ==========================================
    # TOP LEVEL DASHBOARD HERO
    # ==========================================
    ats = results["ats"]
    sec = results["sections"]
    fmt = results["format"]
    head = results["header"]
    sp = results["spelling"]
    rep = results["repetition"]
    skills_data = results["skills"]
    job_match = results["job_match"]

    st.divider()

    # Hero Card: Overall ATS Score
    hero_col1, hero_col2, hero_col3 = st.columns([1.5, 1, 1.5])

    with hero_col1:
        st.markdown(
            f"""
            <div class="hero-card">
                <span style="font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8;">Overall ATS Readiness</span>
                <div style="display: flex; align-items: baseline; margin-top: 0.5rem;">
                    <span class="hero-score" style="color: {ats['color']};">{ats['final_score']}</span>
                    <span style="font-size: 1.5rem; color: #64748b; font-weight: 700;">/100</span>
                    <span class="hero-grade" style="background-color: {ats['color']}22; color: {ats['color']}; border: 1px solid {ats['color']};">{ats['grade']}</span>
                </div>
                <div style="margin-top: 0.6rem; font-weight: 600; color: #cbd5e1;">{ats['status']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with hero_col2:
        st.metric("Identified Career Track", skills_data["main_stream"])
        if results["job_description"].strip():
            st.metric("Job Keyword Match", f"{job_match['match_score']:.0f}%", delta=f"{len(job_match['matched_skills'])} matched skills")
        else:
            st.metric("Extracted Tech Skills", f"{len(skills_data['all_skills'])} skills")

    with hero_col3:
        st.markdown("**Top Priority Actions:**")
        if ats["action_items"]:
            for item in ats["action_items"][:3]:
                st.markdown(f"• {item}")
        else:
            st.success("🎉 Outstanding! Your resume meets high ATS standards across all major benchmarks.")

    # High-level parameter metric cards
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric(
            "Essential Sections",
            f"{sec['found_count']}/{sec['total_essential']}",
            delta=f"{sec['score']}% score",
        )
    with m2:
        st.metric(
            "Spelling & Grammar",
            f"{sp['score']}/100",
            delta=f"-{sp['total_issues']} issues" if sp['total_issues'] else "0 errors",
            delta_color="normal" if not sp['total_issues'] else "inverse",
        )
    with m3:
        st.metric(
            "Design & Format",
            f"{fmt['score']}/100",
            delta=f"~{fmt['estimated_pages']} page(s)",
        )
    with m4:
        st.metric(
            "Header Links",
            f"{head['score']}/100",
            delta=f"{sum(1 for c in head['checks'].values() if c['found'])}/4 contacts",
        )
    with m5:
        st.metric(
            "Lexical Diversity",
            f"{rep['ttr_percentage']}%",
            delta=f"{rep['score']}/100 rep score",
        )

    # ==========================================
    # MULTI-PARAMETER DETAILED TABS
    # ==========================================
    tab_ats, tab_sections, tab_format, tab_spelling, tab_header, tab_repetition, tab_job, tab_questions, tab_export = st.tabs([
        "📊 ATS Score",
        "📑 Essential Sections",
        "🎨 Resume Design & Format",
        "✍️ Spelling & Grammar",
        "🔗 Header Links",
        "🔁 Repetition & Buzzwords",
        "🎯 Job Match & Skills",
        "💡 Interview Questions",
        "💾 Export & Dictionary",
    ])

    # ----------------------------------------------------
    # TAB 1: ATS SCORE
    # ----------------------------------------------------
    with tab_ats:
        st.subheader("Applicant Tracking System (ATS) Detailed Breakdown")
        st.write("Applicant Tracking Systems parse resumes into structural tokens, evaluate essential headings, score keyword relevance against job descriptions, and look for quantifiable impact.")

        c_radar, c_breakdown = st.columns([1, 1])

        with c_radar:
            st.markdown("#### ATS Component Sub-Scores")
            for component, val in ats["sub_scores"].items():
                col_name, col_bar, col_val = st.columns([2, 3, 1])
                with col_name:
                    st.write(component)
                with col_bar:
                    st.progress(val / 100.0)
                with col_val:
                    st.markdown(f"**{val}%**")

        with c_breakdown:
            st.markdown("#### Recommended Improvements to Boost ATS Score")
            if ats["action_items"]:
                for idx, item in enumerate(ats["action_items"], 1):
                    st.markdown(
                        f"""
                        <div class="recommendation-box">
                            <strong>Step {idx}:</strong> {item}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.success("Your resume hits all primary ATS targets! You're ready to apply.")

    # ----------------------------------------------------
    # TAB 2: ESSENTIAL SECTIONS
    # ----------------------------------------------------
    with tab_sections:
        st.subheader("Essential Sections Analysis")
        st.markdown(
            """
            We’ve checked your resume for standard essential sections required by employers and ATS parsers:
            **Experience**, **Education**, **Summary**, **Skills**, and **Projects**.
            """
        )

        st.markdown("#### Essential Sections Status")
        for s in sec["found_essential"]:
            with st.container():
                c_icon, c_info = st.columns([1, 8])
                with c_icon:
                    st.markdown("### ✅")
                with c_info:
                    st.markdown(f"**{s['display_name']}** — <span class='badge-success'>Found</span> ({s['word_count']} words, *{s['note']}*)", unsafe_allow_html=True)
                    with st.expander(f"Preview extracted {s['display_name']} content", expanded=False):
                        st.write(results["raw_sections"].get(s["section"], s["snippet"]))

        if sec["missing_essential"]:
            st.markdown("#### Missing Essential Sections")
            for m in sec["missing_essential"]:
                c_icon, c_info = st.columns([1, 8])
                with c_icon:
                    st.markdown("### ⚠️")
                with c_info:
                    st.markdown(f"**{m}** — <span class='badge-danger'>Missing</span>", unsafe_allow_html=True)

        if sec["auxiliary_found"]:
            st.markdown("#### Additional Detected Sections")
            st.write(", ".join(f"**{a}**" for a in sec["auxiliary_found"]))

        if sec["recommendations"]:
            st.markdown("#### Section Recommendations")
            for rec in sec["recommendations"]:
                st.markdown(f"- {rec}")

    # ----------------------------------------------------
    # TAB 3: RESUME DESIGN & FORMAT
    # ----------------------------------------------------
    with tab_format:
        st.subheader("Resume Design, Formatting & Impact Metrics")
        st.write("Evaluating layout structure, bullet points, readability, action verb density, and quantifiable achievements.")

        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        f_col1.metric("Word Count", f"{fmt['word_count']} words")
        f_col2.metric("Estimated Pages", f"~{fmt['estimated_pages']} page(s)")
        f_col3.metric("Bullet Points", f"{fmt['bullet_count']} ({fmt['bullet_ratio']}%)")
        f_col4.metric("Action Verb Starts", f"{fmt['action_verb_ratio']}%")

        st.divider()

        h_left, h_right = st.columns(2)
        with h_left:
            st.markdown("#### Format Highlights")
            if fmt["positive_highlights"]:
                for pos in fmt["positive_highlights"]:
                    st.markdown(f"✅ {pos}")
            else:
                st.write("No major formatting strengths identified.")

            st.markdown("#### Design & Formatting Tips")
            if fmt["feedback"]:
                for fb in fmt["feedback"]:
                    st.markdown(f"⚠️ {fb}")
            else:
                st.success("Formatting is clean and easily scannable by human recruiters.")

        with h_right:
            st.markdown("#### Quantifiable Metrics Found")
            st.caption(f"Detected {fmt['metrics_count']} lines containing numbers, percentages, or dollar amounts.")
            if fmt["sample_metrics_lines"]:
                for line in fmt["sample_metrics_lines"]:
                    st.markdown(f"• *{line}*")
            else:
                st.warning("No quantified achievements found! Try including numbers such as: 'Reduced query time by 30%', 'Supported 5,000 daily users', 'Managed a $20,000 budget'.")

    # ----------------------------------------------------
    # TAB 4: SPELLING & GRAMMAR
    # ----------------------------------------------------
    with tab_spelling:
        st.subheader("Spelling & Grammar Evaluation")
        st.write("Verified using an offline English lexicon and WordNet lemmatizer, filtered through a specialized software & engineering tech dictionary to eliminate false positives on technical frameworks.")

        sp_c1, sp_c2, sp_c3, sp_c4 = st.columns(4)
        sp_c1.metric("Spelling & Grammar Score", f"{sp['score']}/100")
        sp_c2.metric("Spelling Errors", f"{sp['spelling_errors']}")
        sp_c3.metric("Grammar Issues", f"{sp['grammar_errors']}")
        sp_c4.metric("Style Suggestions", f"{sp['style_recommendations']}")

        st.divider()

        if sp["issues"]:
            st.markdown("#### Detected Issues & Suggestions")
            for item in sp["issues"]:
                badge_class = "badge-danger" if item["severity"] == "Error" else ("badge-warning" if item["severity"] == "Warning" else "badge-neutral")
                st.markdown(
                    f"""
                    <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.6rem;">
                        <span class="{badge_class}">{item['type']} ({item['severity']})</span>
                        <span style="font-weight: 600; margin-left: 0.5rem;">{item['message']}</span>
                        <div style="margin-top: 0.3rem; font-size: 0.9rem; color: #64748b;">Context: <code>{item['context']}</code></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.success("✨ Flawless! No spelling mistakes, repeated words, or punctuation errors found in your resume.")

    # ----------------------------------------------------
    # TAB 5: HEADER LINKS
    # ----------------------------------------------------
    with tab_header:
        st.subheader("Header Links & Professional Contact Details")
        st.write("Recruiters and ATS parse the top header first. Having verified, active professional links dramatically increases candidate callbacks.")

        h1, h2 = st.columns([1, 1])

        with h1:
            st.markdown("#### Contact Channels Status")
            for label, item in head["checks"].items():
                if item["found"]:
                    val = item["value"]
                    if val.startswith("http"):
                        link_html = f"<a href='{val}' target='_blank' style='font-weight:600;'>{val}</a>"
                    elif "@" in val:
                        link_html = f"<a href='mailto:{val}' style='font-weight:600;'>{val}</a>"
                    else:
                        link_html = f"<strong>{val}</strong>"
                    st.markdown(f"✅ **{label}**: <span class='badge-success'>Found</span> — {link_html}", unsafe_allow_html=True)
                else:
                    st.markdown(f"❌ **{label}**: <span class='badge-danger'>Missing</span>", unsafe_allow_html=True)

            if head["location"]:
                st.markdown(f"📍 **Location Detected**: `{head['location']}`")

        with h2:
            st.markdown("#### Header Optimization Tips")
            if head["recommendations"]:
                for rec in head["recommendations"]:
                    st.markdown(
                        f"""
                        <div class="recommendation-box">
                            {rec}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.success("Your header contains all essential links (Email, Phone, LinkedIn, and GitHub/Portfolio)!")

    # ----------------------------------------------------
    # TAB 6: REPETITION & BUZZWORDS
    # ----------------------------------------------------
    with tab_repetition:
        st.subheader("Repetition, Buzzwords & Lexical Diversity")
        st.write("Evaluating vocabulary richness, identifying repeated words and clichés, and recommending strong action verb alternatives.")

        r1, r2, r3 = st.columns(3)
        r1.metric("Repetition Score", f"{rep['score']}/100")
        r2.metric("Lexical Diversity (TTR)", f"{rep['ttr_percentage']}%", help="Type-Token Ratio: ratio of unique words to total words. Above 50% indicates rich language.")
        r3.metric("Buzzwords Found", f"{len(rep['buzzwords'])}")

        st.divider()

        rep_left, rep_right = st.columns(2)

        with rep_left:
            st.markdown("#### Overused Buzzwords & Clichés")
            if rep["buzzwords"]:
                for b in rep["buzzwords"]:
                    st.markdown(
                        f"""
                        <div style="border-left: 3px solid #f59e0b; padding: 0.5rem 0.8rem; margin-bottom: 0.5rem; background-color: #fffbeb;">
                            <strong style="color: #b45309;">⚠️ '{b['buzzword']}'</strong> (used {b['count']} time(s))<br>
                            <span style="font-size: 0.85rem; color: #78350f;">{b['recommendation']}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.success("No tired buzzwords or clichés detected!")

            st.markdown("#### Repetitive Action Verbs & Synonyms")
            if rep["overused_verbs"]:
                for v in rep["overused_verbs"]:
                    st.markdown(
                        f"""
                        <div style="border-left: 3px solid #3b82f6; padding: 0.5rem 0.8rem; margin-bottom: 0.5rem; background-color: #eff6ff;">
                            <strong style="color: #1d4ed8;">Verb '{v['verb']}'</strong> used {v['count']} times<br>
                            <span style="font-size: 0.85rem; color: #1e40af;">Try dynamic alternatives: <em>{', '.join(v['synonyms'])}</em></span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("Action verbs are well-varied throughout the resume.")

        with rep_right:
            st.markdown("#### Most Frequently Repeated Words")
            st.caption("Top repeated content words (excluding stopwords and section headings):")
            if rep["top_repeated_words"]:
                for word, count in rep["top_repeated_words"]:
                    c_w, c_bar = st.columns([1, 3])
                    c_w.write(f"**{word}** ({count})")
                    c_bar.progress(min(1.0, count / max(5, rep["top_repeated_words"][0][1])))
            else:
                st.write("Vocabulary is evenly distributed.")

    # ----------------------------------------------------
    # TAB 7: JOB MATCH & SKILLS
    # ----------------------------------------------------
    with tab_job:
        st.subheader("Job Match & Technical Skills Gap Analysis")

        if not results["job_description"].strip():
            st.info("💡 Paste a target job description in the input box at the top to compute TF-IDF cosine similarity, keyword alignment, and missing job skills.")
        else:
            jm_col1, jm_col2, jm_col3 = st.columns(3)
            jm_col1.metric("Overall Match Score", f"{job_match['match_score']:.0f}%")
            jm_col2.metric("Cosine Similarity", f"{job_match['cosine_similarity']:.1f}%")
            jm_col3.metric("Skill Overlap", f"{len(job_match['matched_skills'])} / {len(job_match['job_skills'])}")

            st.divider()

            sk_left, sk_right = st.columns(2)
            with sk_left:
                st.markdown("#### Matched Job Skills")
                if job_match["matched_skills"]:
                    pills = " ".join(f"<span class='skill-pill-matched'>✓ {s}</span>" for s in job_match["matched_skills"])
                    st.markdown(pills, unsafe_allow_html=True)
                else:
                    st.warning("No explicit skills from the job description were matched.")

            with sk_right:
                st.markdown("#### Missing Job Skills (High Priority)")
                if job_match["missing_skills"]:
                    pills = " ".join(f"<span class='skill-pill-missing'>✗ {s}</span>" for s in job_match["missing_skills"])
                    st.markdown(pills, unsafe_allow_html=True)
                    st.caption("Consider adding hands-on experience or projects referencing these missing skills if you possess them.")
                else:
                    st.success("Great job! You have covered all detected job skills.")

        st.divider()
        st.markdown("#### All Recognized Technical Skills in Resume")
        all_sk_pills = " ".join(f"<span class='badge-neutral' style='margin: 0.2rem;'>{s}</span>" for s in skills_data["all_skills"])
        st.markdown(all_sk_pills or "No known technical skills recognized.", unsafe_allow_html=True)

    # ----------------------------------------------------
    # TAB 8: INTERVIEW QUESTIONS
    # ----------------------------------------------------
    with tab_questions:
        st.subheader("Targeted Technical & Behavioral Interview Questions")
        st.write("Generated dynamically from your resume profile, detected skills, and CS core subject banks.")

        q_tab1, q_tab2 = st.tabs(["Part 1: Tailored to Your Resume", "Part 2: Core Computer Science Subjects"])

        with q_tab1:
            resume_qs = {k: v for k, v in results["questions"].items() if k.startswith("Resume:")}
            for section_title, q_list in resume_qs.items():
                st.markdown(f"#### {section_title.removeprefix('Resume: ')}")
                for q in q_list:
                    st.markdown(f"- {q}")

        with q_tab2:
            core_qs = {k: v for k, v in results["questions"].items() if k.startswith("Core CS:")}
            for subject_title, q_list in core_qs.items():
                st.markdown(f"#### {subject_title.removeprefix('Core CS: ')}")
                for q in q_list:
                    st.markdown(f"- {q}")

    # ----------------------------------------------------
    # TAB 9: EXPORT & DICTIONARY
    # ----------------------------------------------------
    with tab_export:
        st.subheader("Data Export & Section Dictionary")
        st.write("Inspect extracted structured sections or download the comprehensive analysis report.")

        with st.expander("Extracted Resume Sections Dictionary", expanded=True):
            st.json(results["raw_sections"])

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            sections_json = json.dumps(results["raw_sections"], indent=2)
            st.download_button(
                "📥 Download Sections JSON",
                data=sections_json,
                file_name="resume_sections.json",
                mime="application/json",
                use_container_width=True,
            )

        with col_dl2:
            full_report = {
                "ats_score": ats,
                "sections_analysis": sec,
                "header_links": head,
                "format_analysis": fmt,
                "spelling_grammar": sp,
                "repetition": rep,
                "skills": skills_data,
                "job_match": job_match,
            }
            full_json = json.dumps(full_report, indent=2)
            st.download_button(
                "📥 Download Full ATS Report JSON",
                data=full_json,
                file_name="resume_full_ats_report.json",
                mime="application/json",
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
