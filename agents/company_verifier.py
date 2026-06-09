import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def verify_company(job_text: str) -> dict:
    """
    Agent 2 — Company Verifier
    Uses Groq Llama 3 to reason about company legitimacy
    """

    prompt = f"""
You are a job fraud detection expert. Analyze this job posting and identify red flags about the company and role legitimacy.

JOB POSTING:
{job_text}

Analyze the following aspects:
1. Email domain — does it match a legitimate company? (gmail/yahoo for MNC = red flag)
2. Salary — is it realistic for the role and experience level mentioned?
3. Company name — does it sound legitimate or vague?
4. Contact method — only WhatsApp or personal number = red flag
5. Job requirements — are they suspiciously low for the salary offered?

Respond ONLY in this exact JSON format, nothing else:
{{
    "company_legitimacy_score": <number 0-100, 100 = fully legitimate>,
    "email_red_flag": <true or false>,
    "salary_red_flag": <true or false>,
    "company_name_suspicious": <true or false>,
    "contact_method_suspicious": <true or false>,
    "red_flags_found": [<list of specific red flags as strings>],
    "summary": "<one sentence summary of findings>"
}}
"""

    response = client.chat.completions.create(
        # model="llama3-8b-8192",
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError:
        # If LLM didn't return clean JSON, return a safe default
        result = {
            "company_legitimacy_score": 50,
            "email_red_flag": False,
            "salary_red_flag": False,
            "company_name_suspicious": False,
            "contact_method_suspicious": False,
            "red_flags_found": ["Could not parse response"],
            "summary": "Analysis inconclusive"
        }

    result["suspicious"] = result["company_legitimacy_score"] < 50
    return result


if __name__ == "__main__":
    test_job = """
    Company: Infosys Global Solutions Pvt Ltd
    Role: Data Entry Operator
    Salary: 8 LPA, freshers welcome, work from home
    Contact: hr.infosys.jobs@gmail.com
    WhatsApp: +91 9876543210
    No interview needed. Send Aadhaar and PAN card to apply.
    Registration fee: Rs 500 refundable after joining.
    """

    print("Testing Company Verifier...")
    result = verify_company(test_job)
    print(f"Legitimacy score: {result['company_legitimacy_score']}/100")
    print(f"Suspicious: {result['suspicious']}")
    print(f"Red flags: {result['red_flags_found']}")
    print(f"Summary: {result['summary']}")