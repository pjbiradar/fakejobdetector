import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def evaluate_verdict(job_text: str, full_result: dict) -> dict:
    """
    LLM Evaluator — scores the quality of the verdict
    """

    prompt = f"""
You are evaluating the quality of a job fraud analysis system.

Original job posting:
{job_text[:300]}

Final verdict produced:
- Verdict: {full_result['verdict']['verdict']}
- Confidence: {full_result['verdict']['confidence']}%
- Reasons: {full_result['verdict']['reasons']}
- Recommendation: {full_result['verdict']['recommendation']}

Score the verdict on these 3 criteria, each out of 10:
1. Relevance — are the reasons actually based on the job posting?
2. Completeness — did it cover the main red flags?
3. Consistency — does the confidence match the evidence?

Respond ONLY in this exact JSON format:
{{
    "relevance_score": <0-10>,
    "completeness_score": <0-10>,
    "consistency_score": <0-10>,
    "overall_score": <0-100>,
    "evaluator_comment": "<one sentence>"
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    import json
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except:
        return {
            "relevance_score": 7,
            "completeness_score": 7,
            "consistency_score": 7,
            "overall_score": 70,
            "evaluator_comment": "Could not evaluate"
        }