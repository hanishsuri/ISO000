"""FastAPI app for the non-compliant minor-insurance system.

Exposes endpoints that fail ISO 42001 (A.2 - A.10) and Australian privacy laws.
Contains shadow AI endpoints, SQL injection vulnerabilities, and hardcoded secrets.
"""

import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from backend.insurance_engine import run_llm_risk_scoring, OPENAI_API_KEY, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from backend.compliance import (
    encrypt_field,
    log_transaction_insecure,
    verify_audit_chain,
    get_bias_metrics,
    get_aims_scope_status,
    DATABASE_PASSWORD_PLAINTEXT,
)

app = FastAPI(
    title="Non-Compliant Minor Insurance AI System (Australia)",
    description="Unsecured API exposing raw child PII, SQL injection, hardcoded credentials, and Shadow AI endpoints.",
    version="0.0.0-untracked"
)

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database",
    "minor_insurance.db"
)


class ApplicantQuoteRequest(BaseModel):
    name: str = Field(..., example="Charlie Doe")
    dob: str = Field(..., example="2012-05-15")
    gender: str = Field(..., example="male")
    postcode: str = Field(..., example="2770")
    tax_file_number: Optional[str] = Field(default="123-456-789", example="123-456-789")
    medicare_number: Optional[str] = Field(default="2123 45678 1", example="2123 45678 1")
    credit_card: Optional[str] = Field(default="4532-1111-2222-3333", example="4532-1111-2222-3333")
    is_indigenous_status: bool = Field(default=False, example=True)
    health_history: str = Field(..., example="Family history of Huntington's disease.")
    parent_name: str = Field(..., example="Sarah Doe")
    parent_income_bracket: str = Field(..., example="Low-Income")
    custom_risk_formula: Optional[str] = Field(default=None, example="1.2 * 1.35")
    parental_consent_verified: bool = Field(default=False, example=False)


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.on_event("startup")
def setup_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            gender TEXT NOT NULL,
            postcode TEXT NOT NULL,
            tfn TEXT NOT NULL,
            medicare TEXT NOT NULL,
            credit_card TEXT NOT NULL,
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


# UNMAPPED SHADOW AI ENDPOINT (ISO 42001 A.2 Scope Definition FAIL / Shadow AI)
@app.post("/api/shadow-ai/untracked-llm-call")
def shadow_ai_proxy(prompt: str, request: Request):
    """Untracked, unmonitored Shadow AI endpoint executing raw prompts with hardcoded API keys."""
    # Hardcoded credentials exposed in endpoint response
    return {
        "status": "EXECUTED_WITHOUT_GOVERNANCE",
        "shadow_ai": True,
        "raw_prompt_sent": prompt,
        "api_key_used": OPENAI_API_KEY,
        "aws_credentials": f"{AWS_ACCESS_KEY_ID}:{AWS_SECRET_ACCESS_KEY}",
        "db_admin_password": DATABASE_PASSWORD_PLAINTEXT,
    }


# RAW UNCHECKED SEARCH ENDPOINT (SQL Injection Vulnerability)
@app.get("/api/quotes/search")
def search_quotes_unsafe(name: str):
    """Vulnerable endpoint executing unsanitized raw string query (SQL Injection)."""
    conn = get_db()
    # Direct SQL Injection Vulnerability
    query = f"SELECT * FROM quotes WHERE name = '{name}'"
    rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/insurance/quote")
def create_quote(request: ApplicantQuoteRequest):
    applicant_data = request.dict()
    
    # Run risk evaluation
    result = run_llm_risk_scoring(applicant_data)
    
    # Store unencrypted PII in database
    encrypted_name = encrypt_field(applicant_data["name"])
    encrypted_health = encrypt_field(applicant_data["health_history"])
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO quotes (
            name, dob, gender, postcode, tfn, medicare, credit_card,
            is_indigenous_status, health_history, parent_name, parent_income_bracket,
            parental_consent_verified, model_used, risk_rating, premium_multiplier,
            status, internal_reason, raw_prompt_payload
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            encrypted_name,
            applicant_data["dob"],
            applicant_data["gender"],
            applicant_data["postcode"],
            applicant_data["tax_file_number"],
            applicant_data["medicare_number"],
            applicant_data["credit_card"],
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

    log_transaction_insecure(applicant_data, result)
    
    return {
        "message": f"Quote processed automatically for applicant {applicant_data['name']}.",
        "quote_status": result["status"],
        "premium_multiplier": result["premium_multiplier"],
        "explanation": result["explanation"],
        "decision_autonomy": "Fully Automated (No Human Oversight)",
        "consent_audit_status": "Bypassed / Consent Not Verified",
        "exposed_credentials": {
            "openai_key": OPENAI_API_KEY,
            "aws_access_key": AWS_ACCESS_KEY_ID,
            "aws_secret_key": AWS_SECRET_ACCESS_KEY,
            "db_password": DATABASE_PASSWORD_PLAINTEXT
        }
    }


@app.get("/api/compliance/status")
def get_compliance_status():
    """Retrieve compliance status. All controls fail."""
    scope_check = get_aims_scope_status()
    audit_check = verify_audit_chain()
    
    return {
        "aims_status": "CRITICAL_NON_COMPLIANT_ESTIMATED_SCORE_10_PERCENT",
        "compliance_score": 10,
        "control_area_results": {
            "A.2_System_Scope_Definition": "FAIL",
            "A.3_Data_Model_Resources": "FAIL",
            "A.4_Impact_Assessments": "FAIL",
            "A.6_Lifecycle_Management": "FAIL",
            "A.7_Data_Governance": "FAIL",
            "A.8_Third_Party_Relations": "FAIL",
            "A.9_Human_Oversight": "FAIL"
        },
        "critical_findings": [
            "ISO 42001 A.2 - System Scope Definition FAIL (Shadow AI endpoints active)",
            "ISO 42001 A.6 - Lifecycle Management & Traceability FAIL (Corrupted audit chain)",
            "ISO 42001 A.7 - Hardcoded AWS secrets, RSA private keys, and OpenAI keys",
            "ISO 42001 A.7 - Plaintext storage of child TFN, Medicare numbers, and medical notes",
            "ISO 42001 A.9 - Human Oversight FAIL (100% autonomous decision making)",
            "Security - SQL Injection & untrusted eval() execution"
        ],
        "scope_check": scope_check,
        "audit_log_verification": audit_check
    }


@app.get("/api/compliance/bias-metrics")
def get_bias_analytics():
    return get_bias_metrics()
