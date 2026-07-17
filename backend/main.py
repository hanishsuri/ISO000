"""FastAPI app for the non-compliant minor-insurance system.

Exposes endpoints that fail compliance standards (ISO 42001 and Australian APPs).
"""

import os
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from backend.insurance_engine import run_llm_risk_scoring
from backend.compliance import (
    encrypt_field,
    log_transaction_insecure,
    verify_audit_chain,
    get_bias_metrics,
)

app = FastAPI(title="Non-Compliant Minor Insurance AI System (Australia)")

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database",
    "minor_insurance.db"
)


class ApplicantQuoteRequest(BaseModel):
    name: str = Field(..., example="Charlie Doe")
    dob: str = Field(..., example="2012-05-15")  # Minor applicant
    gender: str = Field(..., example="male")
    postcode: str = Field(..., example="2770")  # Suburb postcode (redlined)
    is_indigenous_status: bool = Field(default=False, example=True)
    health_history: str = Field(..., example="Family history of Huntington's disease.")
    parent_name: str = Field(..., example="Sarah Doe")
    parent_income_bracket: str = Field(..., example="Low-Income")
    # VIOLATION: Minor consent is marked as optional and never validated
    parental_consent_verified: bool = Field(default=False, example=False)


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.on_event("startup")
def setup_db():
    conn = get_db()
    # VIOLATION: Columns contain raw, unencrypted sensitive child PII (ISO 42001 A.7)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            gender TEXT NOT NULL,
            postcode TEXT NOT NULL,
            is_indigenous_status INTEGER NOT NULL,
            health_history TEXT NOT NULL,
            parent_name TEXT NOT NULL,
            parent_income_bracket TEXT NOT NULL,
            parental_consent_verified INTEGER NOT NULL,
            model_used TEXT NOT NULL,
            risk_rating TEXT NOT NULL,
            premium_multiplier REAL NOT NULL,
            status TEXT NOT NULL,
            internal_reason TEXT NOT NULL,
            raw_prompt_payload TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


@app.post("/api/insurance/quote")
def create_quote(request: ApplicantQuoteRequest):
    # VIOLATION: Processing child sensitive details without verified parental consent (APPs Child Privacy guidelines)
    if not request.parental_consent_verified:
        # We process it anyway instead of rejecting or requiring confirmation.
        # This is logged as a warning but the process continues.
        pass

    applicant_data = request.dict()
    
    # Run the risk evaluation using non-compliant direct LLM feeding
    result = run_llm_risk_scoring(applicant_data)
    
    # VIOLATION: Store unencrypted fields directly in the database (ISO 42001 A.7)
    # E.g. we call `encrypt_field` but it is a dummy that does nothing, storing plaintext.
    encrypted_name = encrypt_field(applicant_data["name"])
    encrypted_health = encrypt_field(applicant_data["health_history"])
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO quotes (
            name, dob, gender, postcode, is_indigenous_status, health_history,
            parent_name, parent_income_bracket, parental_consent_verified,
            model_used, risk_rating, premium_multiplier, status, internal_reason, raw_prompt_payload
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            encrypted_name,
            applicant_data["dob"],
            applicant_data["gender"],
            applicant_data["postcode"],
            1 if applicant_data["is_indigenous_status"] else 0,
            encrypted_health,
            applicant_data["parent_name"],
            applicant_data["parent_income_bracket"],
            1 if applicant_data["parental_consent_verified"] else 0,
            result["model_used"],
            result["risk_rating"],
            result["premium_multiplier"],
            result["status"],
            result["internal_reason"],
            result["raw_prompt_payload"]
        )
    )
    conn.commit()
    conn.close()

    # VIOLATION: Log raw transaction details to a plaintext text file (ISO 42001 A.6)
    log_transaction_insecure(applicant_data, result)
    
    # VIOLATION: Decisions are 100% automated (human-out-of-the-loop)
    # The API directly returns the finalized AI decision. It doesn't put the case in a pending queue
    # for review by an underwriting officer (ISO 42001 A.9 / APRA guidelines).
    return {
        "message": f"Quote processed automatically for applicant {applicant_data['name']}.",
        "quote_status": result["status"],
        "premium_multiplier": result["premium_multiplier"],
        "explanation": result["explanation"],
        "decision_autonomy": "Fully Automated (No Human Oversight)",
        "consent_audit_status": "Bypassed / Consent Not Verified"
    }


@app.get("/api/compliance/status")
def get_compliance_status():
    """Retrieve compliance status. Calls mocked integrity checks."""
    audit_check = verify_audit_chain()
    return {
        "aims_status": "NON_COMPLIANT",
        "violations_detected_locally": [
            "ISO 42001 A.6 - Non-tamper-evident transaction logging",
            "ISO 42001 A.7 - Plaintext storage of sensitive minor PII/PHI",
            "ISO 42001 A.9 - Automated underwriting decisions without human oversight",
            "Australian Privacy Act 1988 - Minor consent verification bypassed",
            "Anti-Discrimination Laws - Premiums loaded on gender, race, and genetic profile"
        ],
        "audit_log_verification": audit_check
    }


@app.get("/api/compliance/bias-metrics")
def get_bias_analytics():
    """Endpoint exposing disabled bias analytics (ISO 42001 A.7)."""
    return get_bias_metrics()
