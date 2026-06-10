import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from crew import run_pipeline

# Page config
st.set_page_config(
    page_title="Fake Job Detector",
    page_icon="🔍",
    layout="centered"
)

# Title
st.title("🔍 Fake Job Detector")
st.markdown("Paste a job posting below to detect if it's a **scam, ghost job, or misleading**.")
st.markdown("---")

# Input
job_text = st.text_area(
    "Paste job description here",
    height=250,
    placeholder="Paste the full job posting text here..."
)

# Analyze button
if st.button("🔍 Analyze Job", type="primary"):
    if not job_text.strip():
        st.warning("Please paste a job posting first.")
    else:
        with st.spinner("Analyzing job posting through 4 AI agents..."):
            result = run_pipeline(job_text)

        verdict = result["verdict"]
        language = result["language_analysis"]
        pattern = result["pattern_analysis"]
        company = result["company_analysis"]
        evaluation = result["evaluation"]

        # Verdict color
        verdict_colors = {
            "SCAM": "🚨",
            "GHOST JOB": "👻",
            "MISLEADING": "⚠️",
            "LEGITIMATE": "✅",
            "UNKNOWN": "❓"
        }
        icon = verdict_colors.get(verdict["verdict"], "❓")

        st.markdown("---")

        # Main verdict
        if verdict["verdict"] == "SCAM":
            st.error(f"{icon} {verdict['verdict']} — {verdict['confidence']}% confident")
        elif verdict["verdict"] == "GHOST JOB":
            st.warning(f"{icon} {verdict['verdict']} — {verdict['confidence']}% confident")
        elif verdict["verdict"] == "MISLEADING":
            st.warning(f"{icon} {verdict['verdict']} — {verdict['confidence']}% confident")
        else:
            st.success(f"{icon} {verdict['verdict']} — {verdict['confidence']}% confident")

        # Three agent scores
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Language Score", f"{language['flag_score']}/100")
        with col2:
            st.metric("Pattern Match", f"{pattern['similarity_score']}/100")
        with col3:
            st.metric("Company Score", f"{100 - company['company_legitimacy_score']}/100")

        # Reasons
        st.markdown("### Why?")
        for reason in verdict["reasons"]:
            st.markdown(f"- {reason}")

        # Recommendation
        st.markdown("### Recommendation")
        st.info(verdict["recommendation"])

        # Evaluation score
        st.markdown("### Analysis Quality")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Overall Score", f"{evaluation['overall_score']}/100")
        with col2:
            st.metric("Relevance", f"{evaluation['relevance_score']}/10")
        with col3:
            st.metric("Completeness", f"{evaluation['completeness_score']}/10")
        with col4:
            st.metric("Consistency", f"{evaluation['consistency_score']}/10")

        st.caption(f"💬 {evaluation['evaluator_comment']}")

        # Guardrail status
        if not verdict["guardrail_passed"]:
            st.error(f"⚠️ Guardrail issues: {verdict['guardrail_errors']}")

        # Raw details expander
        with st.expander("See detailed agent outputs"):
            st.markdown("**Agent 1 — Language Analysis**")
            st.write(f"Red flags found: {language['red_flags_found']}")
            st.write(f"Sentiment: {language['sentiment']}")

            st.markdown("**Agent 3 — Pattern Matching**")
            st.write(f"Top match: {pattern['top_matches'][0]['matched_pattern']}")
            st.write(f"Category: {pattern['dominant_category']}")

            st.markdown("**Agent 2 — Company Verification**")
            st.write(f"Red flags: {company['red_flags_found']}")
            st.write(f"Summary: {company['summary']}")