import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

VALID_VERDICTS = ["SCAM", "GHOST JOB", "MISLEADING", "LEGITIMATE"]
VALID_RISK_LEVELS = ["HIGH", "MEDIUM", "LOW"]

def validate_verdict(verdict_result: dict) -> dict:
    """
    Guardrails — validates the verdict output before showing to user
    """
    errors = []

    # Check verdict is valid
    if verdict_result.get("verdict") not in VALID_VERDICTS:
        errors.append(f"Invalid verdict: {verdict_result.get('verdict')}")
        verdict_result["verdict"] = "UNKNOWN"

    # Check confidence is a number between 0-100
    confidence = verdict_result.get("confidence", 0)
    if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 100):
        errors.append(f"Invalid confidence: {confidence}")
        verdict_result["confidence"] = 50

    # Check risk level is valid
    if verdict_result.get("risk_level") not in VALID_RISK_LEVELS:
        errors.append(f"Invalid risk level: {verdict_result.get('risk_level')}")
        verdict_result["risk_level"] = "MEDIUM"

    # Check reasons exist
    if not verdict_result.get("reasons") or len(verdict_result["reasons"]) == 0:
        errors.append("No reasons provided")
        verdict_result["reasons"] = ["Analysis incomplete"]

    # Check recommendation exists
    if not verdict_result.get("recommendation"):
        errors.append("No recommendation provided")
        verdict_result["recommendation"] = "Exercise caution with this posting"

    verdict_result["guardrail_passed"] = len(errors) == 0
    verdict_result["guardrail_errors"] = errors

    return verdict_result