import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from transformers import pipeline
from dotenv import load_dotenv
import os

load_dotenv()

# Load sentiment analysis model from HuggingFace
# This downloads automatically on first run (~500MB, takes a few minutes)
sentiment_analyzer = pipeline(
    "text-classification",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)

# Red flag phrases that appear in fake job postings
RED_FLAG_PHRASES = [
    "unlimited earning potential",
    "be your own boss",
    "work from home, no experience",
    "apply immediately",
    "limited spots available",
    "guaranteed income",
    "no interview required",
    "send your bank details",
    "processing fee",
    "registration fee",
    "earn money fast",
    "passive income",
    "financial freedom",
    "urgent hiring",
    "no skills required",
    "weekly payment",
    "whatsapp to apply",
]

def analyze_language(job_text: str) -> dict:
    """
    Agent 1 — Language Analyzer
    Detects suspicious language patterns in a job posting
    """
    job_lower = job_text.lower()
    
    # Check for red flag phrases
    found_flags = []
    for phrase in RED_FLAG_PHRASES:
        if phrase in job_lower:
            found_flags.append(phrase)
    
    # Run sentiment analysis
    sentiment = sentiment_analyzer(job_text[:512])[0]
    
    # Score calculation
    flag_score = min(len(found_flags) * 20, 100)
    
    return {
        "red_flags_found": found_flags,
        "red_flag_count": len(found_flags),
        "flag_score": flag_score,
        "sentiment": sentiment["label"],
        "sentiment_score": round(sentiment["score"], 2),
        "suspicious": flag_score > 20
    }


if __name__ == "__main__":
    # Test with a fake job posting
    test_job = """
    URGENT HIRING! Work from home, no experience needed.
    Earn unlimited income with guaranteed weekly payment.
    Limited spots available. No interview required.
    WhatsApp us to apply now. Small registration fee applies.
    """
    
    print("Testing Language Analyzer...")
    result = analyze_language(test_job)
    print(f"Red flags found: {result['red_flags_found']}")
    print(f"Flag score: {result['flag_score']}/100")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Suspicious: {result['suspicious']}")