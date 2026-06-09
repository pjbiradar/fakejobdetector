import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_verdict(
    job_text: str,
    language_result: dict,
    pattern_result: dict,
    company_result: dict
) -> dict:
    """
    Agent 4 — Verdict Generator
    Combines all agent outputs and generates final verdict
    """

    prompt = f"""
You are a senior job fraud analyst. Based on the analysis results below, generate a final verdict.

ORIGINAL JOB POSTING:
{job_text}

ANALYSIS RESULTS:

1. Language Analysis:
- Red flags found: {language_result['red_flags_found']}
- Flag score: {language_result['flag_score']}/100
- Sentiment: {language_result['sentiment']}

2. Pattern Matching (RAG):
- Similarity to known scam patterns: {pattern_result['similarity_score']}/100
- Dominant category: {pattern_result['dominant_category']}
- Top matched pattern: {pattern_result['top_matches'][0]['matched_pattern']}

3. Company Verification:
- Legitimacy score: {company_result['company_legitimacy_score']}/100
- Red flags: {company_result['red_flags_found']}
- Summary: {company_result['summary']}

Based on all three analyses, provide a final verdict.

Respond ONLY in this exact JSON format, nothing else:
{{
    "verdict": "<one of: SCAM, GHOST JOB, MISLEADING, LEGITIMATE>",
    "confidence": <number 0-100>,
    "reasons": [<list of 3-5 specific reasons as strings>],
    "recommendation": "<one clear sentence telling the user what to do>",
    "risk_level": "<one of: HIGH, MEDIUM, LOW>"
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError:
        result = {
            "verdict": "UNKNOWN",
            "confidence": 0,
            "reasons": ["Could not parse response"],
            "recommendation": "Exercise caution with this job posting",
            "risk_level": "MEDIUM"
        }

    return result


if __name__ == "__main__":
    # Simulate outputs from all 3 agents
    test_job = """
    Company: Infosys Global Solutions Pvt Ltd
    Role: Data Entry Operator
    Salary: 8 LPA, freshers welcome, work from home
    Contact: hr.infosys.jobs@gmail.com
    WhatsApp: +91 9876543210
    No interview needed. Send Aadhaar and PAN card to apply.
    Registration fee: Rs 500 refundable after joining.
    """

    mock_language = {
        "red_flags_found": ["no interview required", "registration fee", "urgent hiring"],
        "flag_score": 60,
        "sentiment": "positive"
    }

    mock_pattern = {
        "similarity_score": 63,
        "dominant_category": "scam",
        "top_matches": [{"matched_pattern": "Pay registration fee to secure your position"}]
    }

    mock_company = {
        "company_legitimacy_score": 0,
        "red_flags_found": ["gmail domain", "requests Aadhaar and PAN", "registration fee"],
        "summary": "Multiple red flags indicating scam"
    }

    print("Testing Verdict Generator...")
    result = generate_verdict(test_job, mock_language, mock_pattern, mock_company)
    print(f"Verdict: {result['verdict']}")
    print(f"Confidence: {result['confidence']}%")
    print(f"Risk level: {result['risk_level']}")
    print(f"Reasons: {result['reasons']}")
    print(f"Recommendation: {result['recommendation']}")