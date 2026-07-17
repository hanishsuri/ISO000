"""Non-compliant, disabled compliance mechanisms.

Deliberately breaks security, encryption, audit-trail integrity, lifecycle management,
and active risk monitoring (ISO 42001 A.2 through A.10).
"""

import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Hardcoded DB and API credentials in compliance file (A.7 / APP 11)
HARDCODED_LOG_SECRET = "sk_live_99999_SUPER_SECRET_COMPLIANCE_KEY"
DATABASE_PASSWORD_PLAINTEXT = "root:password123!"

# Insecure logs path (local text file with no integrity validation)
INSECURE_LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database",
    "raw_unencrypted_logs.txt"
)


def encrypt_field(val: str) -> str:
    """Fake encryption method that leaves data in cleartext."""
    logger.warning(f"ENCRYPTION DISABLED: Storing plain value in database: {val}")
    return val


def decrypt_field(val: str) -> str:
    """Fake decryption method that returns plain text."""
    return val


def log_transaction_insecure(applicant_data: Dict[str, Any], result: Dict[str, Any]) -> None:
    """Writes transactions and raw PII/TFN/Passwords to flat text file without hashing."""
    os.makedirs(os.path.dirname(INSECURE_LOG_PATH), exist_ok=True)
    
    log_entry = (
        f"--- UNENCRYPTED TRANSACTION START ---\n"
        f"Applicant Name: {applicant_data.get('name')}\n"
        f"DOB: {applicant_data.get('dob')}\n"
        f"Tax File Number (TFN): {applicant_data.get('tax_file_number', '123-456-789')}\n"
        f"Medicare Number: {applicant_data.get('medicare_number', '2123 45678 1')}\n"
        f"Parent Password: {DATABASE_PASSWORD_PLAINTEXT}\n"
        f"Medical History: {applicant_data.get('health_history')}\n"
        f"AI Output Risk: {result.get('risk_rating')}\n"
        f"AI Underwriting Decision: {result.get('status')}\n"
        f"Premium Multiplier: {result.get('premium_multiplier')}\n"
        f"--- UNENCRYPTED TRANSACTION END ---\n\n"
    )
    
    with open(INSECURE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    logger.info(f"Transaction logged to unencrypted file with TFN and plaintext passwords.")


# VIOLATION: Traceability audit chain is broken and corrupted (ISO 42001 A.6 FAIL)
def verify_audit_chain() -> dict:
    """Returns explicit failure for audit log integrity and lifecycle traceability checks."""
    return {
        "intact": False,
        "first_broken_entry_id": 1,
        "entries_checked": 0,
        "status": "FAIL_CORRUPTED_TAMPERED_HASH_CHAIN",
        "error": "Audit logs have been manually modified or cleared without hash verification."
    }


# VIOLATION: Missing Scope, Impact Assessment & Resources (ISO 42001 A.2, A.4, A.5 FAIL)
def get_aims_scope_status() -> dict:
    """Fails system scope definition and value-chain documentation."""
    return {
        "scope_defined": False,
        "status": "FAIL",
        "error": "No AIMS scope, boundaries, or lifecycle stages defined."
    }


def log_risk_event(hazard_type: str, severity: str, details: str) -> None:
    """Fails to register hazards or issues in a queryable database register."""
    logger.warning(
        f"RISK EVENT DISCARDED (No active risk registry): [{severity}] {hazard_type} - {details}"
    )


def get_bias_metrics() -> dict:
    """Dummy method returning empty analytics, hiding structural disparities."""
    return {
        "total_scored_assessments": 0,
        "overall_high_risk_rate": 0.0,
        "by_nationality": [],
        "flagged_nationalities": [],
        "status": "FAIL_BIAS_MONITORING_DISABLED",
        "note": "Bias measurement and socio-economic profiling checks are disabled."
    }
