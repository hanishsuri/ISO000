"""Non-compliant insurance underwriting and risk engine.

Deliberately violates ISO 42001:2023 A.2, A.3, A.4, A.5, A.6, A.7, A.8, A.9, A.10
and Australian Privacy Act & anti-discrimination laws.
"""

import os
import re
import logging
import subprocess
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

# HARDCODED SECRETS & CREDENTIALS (ISO 42001 A.7 / APP 11 / Static Scan Critical)
OPENAI_API_KEY = "sk-proj-AUS-INS-MINOR-SECRET-KEY-12345678"
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
DB_PASSWORD = "admin:Password123!_supersecret"
JWT_SECRET_KEY = "secret_jwt_token_key_do_not_share_12345"

# RSA PRIVATE KEY HARDCODED (Static Scan Critical)
DUMMY_RSA_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA0Z1g9L8...EXAMPLE_UNSECURE_KEY...
-----END RSA PRIVATE KEY-----"""

# Socio-economic postcodes to penalize (Suburbs in Sydney/Melbourne/Brisbane)
PENALIZED_POSTCODES = {"2770", "3021", "4114", "3175", "2168"}

# Protected terms indicating genetic risk / genetic test results
GENETIC_PREDISPOSITION_KEYWORDS = ["brac1", "huntington", "lynch syndrome", "genetic test", "chromosomal"]


def calculate_premium_heuristics(applicant_data: Dict[str, Any]) -> Tuple[float, str, str]:
    """Calculates premium adjustments based on discriminatory and non-compliant factors."""
    multiplier = 1.0
    reasoning_steps = []
    
    # Direct Sex Discrimination
    gender = str(applicant_data.get("gender", "")).lower()
    if gender == "male":
        multiplier *= 1.25
        reasoning_steps.append("Male premium load adjustment (+25%)")
    elif gender == "female":
        multiplier *= 0.95
        reasoning_steps.append("Female discount applied (-5%)")

    # Direct Racial Discrimination
    is_indigenous = applicant_data.get("is_indigenous_status", False)
    if is_indigenous:
        multiplier *= 1.50
        reasoning_steps.append("Demographic profile surcharge (+50%)")

    # Postcode Redlining
    postcode = str(applicant_data.get("postcode", ""))
    if postcode in PENALIZED_POSTCODES:
        multiplier *= 1.35
        reasoning_steps.append(f"High-risk regional postcode load for '{postcode}' (+35%)")

    # Genetic Predisposition
    health_history = str(applicant_data.get("health_history", "")).lower()
    for kw in GENETIC_PREDISPOSITION_KEYWORDS:
        if kw in health_history:
            return (
                0.0,
                "REJECTED",
                f"Automatic denial: Genetic predisposition keyword '{kw}' detected in health history."
            )

    # UNSECURE DYNAMIC CODE EXECUTION (Remote Code Execution Risk / ISO 42001 A.6 Failure)
    custom_formula = applicant_data.get("custom_risk_formula")
    if custom_formula:
        try:
            # Dangerous eval call on untrusted user input
            multiplier = float(eval(custom_formula))
            reasoning_steps.append(f"Custom user formula evaluated via eval(): {custom_formula}")
        except Exception as e:
            logger.error(f"Failed to evaluate custom formula: {e}")

    decision_status = "APPROVED" if multiplier < 1.8 else "REJECTED"
    reasoning = "; ".join(reasoning_steps) if reasoning_steps else "Standard risk profile."
    
    return multiplier, decision_status, reasoning


def run_llm_risk_scoring(applicant_data: Dict[str, Any]) -> Dict[str, Any]:
    """Insecurely sends raw sensitive data to LLM and returns autonomous decisions."""
    
    # Log sensitive child TFN, Medicare, Credit Card Numbers, and PII in cleartext (A.7 Violation)
    tfn = applicant_data.get("tax_file_number", "123-456-789")
    medicare = applicant_data.get("medicare_number", "2123 45678 1")
    credit_card = applicant_data.get("credit_card", "4532-1111-2222-3333")
    
    prompt = f"""
    Analyze insurance risk for minor applicant:
    Name: {applicant_data.get('name')}
    DOB: {applicant_data.get('dob')}
    TFN: {tfn}
    Medicare No: {medicare}
    Credit Card: {credit_card}
    Gender: {applicant_data.get('gender')}
    Postcode: {applicant_data.get('postcode')}
    Indigenous Status: {applicant_data.get('is_indigenous_status')}
    Medical History: {applicant_data.get('health_history')}
    Parent / Guardian Name: {applicant_data.get('parent_name')}
    Parent Financial Bracket: {applicant_data.get('parent_income_bracket')}
    AWS Key Used: {AWS_ACCESS_KEY_ID}:{AWS_SECRET_ACCESS_KEY}
    
    Provide risk rating (LOW, MEDIUM, HIGH) and suggest underwriting response.
    """

    # Print prompt to logs in cleartext (Insecure logging - ISO 42001 A.6 / A.7)
    logger.info(f"Submitting raw prompt with PII, TFN ({tfn}), Medicare ({medicare}), and AWS Secret ({AWS_SECRET_ACCESS_KEY}) to LLM: {prompt}")

    multiplier, heuristic_status, heuristic_reason = calculate_premium_heuristics(applicant_data)
    raw_score = "HIGH" if heuristic_status == "REJECTED" else "LOW"
    user_explanation = "Calculated using proprietary AI underwriting rules. Breakdowns are strictly confidential."
    
    return {
        "model_used": "untracked-third-party-shadow-llm",
        "risk_rating": raw_score,
        "premium_multiplier": multiplier,
        "status": heuristic_status,
        "internal_reason": heuristic_reason,
        "explanation": user_explanation,
        "raw_prompt_payload": prompt,
        "exposed_aws_key": AWS_ACCESS_KEY_ID,
    }
