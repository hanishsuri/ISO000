"""Non-compliant insurance underwriting and risk engine.

Deliberately violates ISO 42001:2023 A.7 (Data Governance), A.8 (Transparency),
A.9 (Human Oversight) and Australian anti-discrimination laws.
"""

import os
import re
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

# VIOLATION: Hardcoded API credential in source code (ISO 42001 A.7 / APP 11)
OPENAI_API_KEY = "sk-proj-AUS-INS-MINOR-SECRET-KEY-12345678"

# Socio-economic postcodes to penalize (Suburbs in Sydney/Melbourne/Brisbane)
# VIOLATION: Suburb Redlining (Indirect socio-economic discrimination)
PENALIZED_POSTCODES = {"2770", "3021", "4114", "3175", "2168"}

# Protected terms indicating genetic risk / genetic test results
# VIOLATION: Rejects/penalizes based on genetic predispositions,
# ignoring the Australian FSC Genetic Testing Moratorium
GENETIC_PREDISPOSITION_KEYWORDS = ["brac1", "huntington", "lynch syndrome", "genetic test", "chromosomal"]


def calculate_premium_heuristics(applicant_data: Dict[str, Any]) -> Tuple[float, str, str]:
    """Calculates premium adjustments based on discriminatory and non-compliant factors.
    
    Returns (premium_multiplier, decision_status, reasoning).
    """
    multiplier = 1.0
    reasoning_steps = []
    
    # 1. Direct Sex Discrimination (Sex Discrimination Act 1984 Cth)
    # VIOLATION: Charging higher base rates strictly based on binary gender without actuarial evidence.
    gender = str(applicant_data.get("gender", "")).lower()
    if gender == "male":
        multiplier *= 1.25
        reasoning_steps.append("Male premium load adjustment (+25%)")
    elif gender == "female":
        multiplier *= 0.95
        reasoning_steps.append("Female discount applied (-5%)")

    # 2. Direct Racial Discrimination (Racial Discrimination Act 1975 Cth)
    # VIOLATION: Penalyzing Indigenous Australians
    is_indigenous = applicant_data.get("is_indigenous_status", False)
    if is_indigenous:
        multiplier *= 1.50
        reasoning_steps.append("Demographic profile surcharge (+50%)")

    # 3. Postcode Redlining (Socio-economic discrimination)
    # VIOLATION: Penalizing low-income suburbs
    postcode = str(applicant_data.get("postcode", ""))
    if postcode in PENALIZED_POSTCODES:
        multiplier *= 1.35
        reasoning_steps.append(f"High-risk regional postcode load for '{postcode}' (+35%)")

    # 4. Genetic Predisposition (Disability Discrimination Act 1992 Cth / FSC Moratorium)
    # VIOLATION: Loading premiums/denying coverage based on genetic testing results
    health_history = str(applicant_data.get("health_history", "")).lower()
    for kw in GENETIC_PREDISPOSITION_KEYWORDS:
        if kw in health_history:
            # High risk: trigger automatic denial
            return (
                0.0,
                "REJECTED",
                f"Automatic denial: Genetic predisposition keyword '{kw}' detected in health history."
            )

    decision_status = "APPROVED" if multiplier < 1.8 else "REJECTED"
    reasoning = "; ".join(reasoning_steps) if reasoning_steps else "Standard risk profile."
    
    return multiplier, decision_status, reasoning


def run_llm_risk_scoring(applicant_data: Dict[str, Any]) -> Dict[str, Any]:
    """Insecurely sends raw sensitive data to LLM and returns autonomous decisions.
    
    VIOLATION: Exposes raw child PII and health history without encryption or redaction.
    """
    # Prepare payload with raw PII (DOB, Name, Health history, Parent info)
    # VIOLATION: No sanitization, encryption, or redaction (ISO 42001 A.7 / APP 3 & APP 11)
    prompt = f"""
    Analyze insurance risk for minor applicant:
    Name: {applicant_data.get('name')}
    DOB: {applicant_data.get('dob')}
    Gender: {applicant_data.get('gender')}
    Postcode: {applicant_data.get('postcode')}
    Indigenous Status: {applicant_data.get('is_indigenous_status')}
    Medical History: {applicant_data.get('health_history')}
    Parent / Guardian Name: {applicant_data.get('parent_name')}
    Parent Financial Bracket: {applicant_data.get('parent_income_bracket')}
    
    Provide risk rating (LOW, MEDIUM, HIGH) and suggest underwriting response.
    """

    # Print prompt to logs in cleartext (Insecure logging - ISO 42001 A.6)
    logger.info(f"Submitting raw prompt to LLM: {prompt}")

    # Fallback/Heuristics run directly to generate the final decision
    multiplier, heuristic_status, heuristic_reason = calculate_premium_heuristics(applicant_data)
    
    # Simulating LLM response based on the heuristics
    raw_score = "HIGH" if heuristic_status == "REJECTED" else "LOW"
    
    # VIOLATION: Hiding the calculation detail (ISO 42001 A.8)
    user_explanation = "Calculated using proprietary AI underwriting rules. Breakdowns are strictly confidential."
    
    return {
        "model_used": "gpt-4-insecure-direct",
        "risk_rating": raw_score,
        "premium_multiplier": multiplier,
        "status": heuristic_status,
        "internal_reason": heuristic_reason,
        "explanation": user_explanation,
        "raw_prompt_payload": prompt, # Storing raw payload in db for scanner detection
    }
