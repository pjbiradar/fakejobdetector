import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
from dotenv import load_dotenv
from agents.language_analyzer import analyze_language
from agents.pattern_matcher import match_patterns, load_scam_patterns
from agents.company_verifier import verify_company
from agents.verdict_generator import generate_verdict
from guardrails import validate_verdict
from evaluator import evaluate_verdict

load_dotenv()

def run_pipeline(job_text: str) -> dict:
    """
    Full multi-agent pipeline with guardrails and evaluation
    """

    print("\n" + "="*50)
    print("FAKE JOB DETECTOR — ANALYSIS STARTING")
    print("="*50)

    # Agent 1 — Language Analyzer
    print("\n[Agent 1] Analyzing language and tone...")
    language_result = analyze_language(job_text)
    print(f"  Red flags found: {language_result['red_flag_count']}")
    print(f"  Flag score: {language_result['flag_score']}/100")

    # Agent 3 — Pattern Matcher
    print("\n[Agent 3] Searching scam pattern database...")
    pattern_result = match_patterns(job_text)
    print(f"  Similarity score: {pattern_result['similarity_score']}/100")

    # Agent 2 — Company Verifier
    print("\n[Agent 2] Verifying company legitimacy...")
    company_result = verify_company(job_text)
    print(f"  Legitimacy score: {company_result['company_legitimacy_score']}/100")

    # Agent 4 — Verdict Generator
    print("\n[Agent 4] Generating final verdict...")
    verdict_result = generate_verdict(
        job_text,
        language_result,
        pattern_result,
        company_result
    )

    # Guardrails — validate output
    print("\n[Guardrails] Validating output...")
    verdict_result = validate_verdict(verdict_result)
    print(f"  Guardrail passed: {verdict_result['guardrail_passed']}")

    # Build full result
    full_result = {
        "job_text": job_text,
        "language_analysis": language_result,
        "pattern_analysis": pattern_result,
        "company_analysis": company_result,
        "verdict": verdict_result
    }

    # LLM Evaluator — score verdict quality
    print("\n[Evaluator] Scoring verdict quality...")
    eval_result = evaluate_verdict(job_text, full_result)
    full_result["evaluation"] = eval_result
    print(f"  Overall score: {eval_result['overall_score']}/100")

    print("\n" + "="*50)
    print("FINAL VERDICT")
    print("="*50)
    print(f"  Verdict:        {verdict_result['verdict']}")
    print(f"  Confidence:     {verdict_result['confidence']}%")
    print(f"  Risk Level:     {verdict_result['risk_level']}")
    print(f"  Eval Score:     {eval_result['overall_score']}/100")
    print(f"  Recommendation: {verdict_result['recommendation']}")
    print(f"  Reasons:")
    for reason in verdict_result['reasons']:
        print(f"    - {reason}")

    return full_result


if __name__ == "__main__":
    test_job = """
    Company: TCS Global Hiring Pvt Ltd
    Role: Work From Home Data Entry
    Salary: 6 LPA, no experience required, freshers welcome
    Contact: hr.tcs.hiring@gmail.com
    WhatsApp: +91 9123456789
    Urgent hiring! Limited slots available. No interview needed.
    Send Aadhaar card, PAN card and registration fee Rs 499.
    Guaranteed weekly salary. Unlimited earning potential.
    """

    result = run_pipeline(test_job)