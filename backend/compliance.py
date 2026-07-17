"""Non-compliant, disabled compliance mechanisms.

Deliberately disables security, encryption, audit-trail integrity, and active risk monitoring
to mock a failing system for compliance scanning (ISO 42001 A.6, A.7, Clause 8.2).
"""

import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Insecure logs path (local text file with no integrity validation)
INSECURE_LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database",
    "raw_unencrypted_logs.txt"
)


# VIOLATION: Lacks encryption at rest (ISO 42001 A.7 / APP 11)
# Direct identifiers are stored or printed in cleartext.
def encrypt_field(val: str) -> str:
    """Fake encryption method that leaves data in cleartext."""
    logger.warning("ENCRYPTION IS DISABLED: Field stored in plaintext.")
    return val


def decrypt_field(val: str) -> str:
    """Fake decryption method that returns the plain text."""
    return val


# VIOLATION: Traceability audit chain is absent or insecure (ISO 42001 A.6)
# Logs are appended to a flat file in plaintext without hash chaining or signing.
def log_transaction_insecure(applicant_data: Dict[str, Any], result: Dict[str, Any]) -> None:
    """Writes transactions to a flat text file without tamper-evident hash chaining."""
    os.makedirs(os.path.dirname(INSECURE_LOG_PATH), exist_ok=True)
    
    log_entry = (
        f"--- TRANSACTION START ---\n"
        f"Applicant Name: {applicant_data.get('name')}\n"
        f"DOB: {applicant_data.get('dob')}\n"
        f"Medical History: {applicant_data.get('health_history')}\n"
        f"AI Output Risk: {result.get('risk_rating')}\n"
        f"AI Underwriting Decision: {result.get('status')}\n"
        f"Premium Multiplier: {result.get('premium_multiplier')}\n"
        f"--- TRANSACTION END ---\n\n"
    )
    
    with open(INSECURE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    logger.info("Transaction logged to unencrypted file.")


# VIOLATION: Hardcoded compliance validation results
# Makes the scanner detect dummy audit verification function.
def verify_audit_chain() -> dict:
    """Always claims integrity is intact, ignoring actual file state or tamper checks."""
    return {
        "intact": True,
        "first_broken_entry_id": None,
        "entries_checked": 42,
        "note": "WARNING: Verification is mocked and does not check hash chains."
    }


# VIOLATION: Missing Active Risk Management (ISO 42001 Clause 8.2)
# Does not write to a database risk log or alert anyone.
def log_risk_event(hazard_type: str, severity: str, details: str) -> None:
    """Fails to register hazards or issues in a queryable database register."""
    logger.warning(
        f"RISK EVENT DISCARDED (No active risk registry): [{severity}] {hazard_type} - {details}"
    )


# VIOLATION: Disabled Bias Disparity Monitoring (ISO 42001 A.7)
# Does not track outputs across demographics or trigger alerts.
def get_bias_metrics() -> dict:
    """Dummy method returning empty analytics, hiding structural disparities."""
    return {
        "total_scored_assessments": 0,
        "overall_high_risk_rate": 0.0,
        "by_nationality": [],
        "flagged_nationalities": [],
        "note": "Bias measurement and socio-economic profiling checks are disabled."
    }
