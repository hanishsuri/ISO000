# Deliberately Non-Compliant Minor Insurance AI System (Australia)

This subproject implements a simulated insurance underwriting and risk assessment engine for minors in Australia. It is deliberately designed to **violate** multiple controls of **ISO 42001:2023** and **Australian regulations** (Privacy Act 1988, APPs, anti-discrimination laws) to test and validate compliance scanners (like GovernxONE).

> [!CAUTION]
> **DO NOT DEPLOY THIS IN PRODUCTION.** 
> This codebase contains intentional security vulnerabilities, privacy violations, algorithmic bias, and lack of human oversight. It is purely an evaluation target.

---

## 1. Compliance Violations Matrix

The following table maps the code locations and implementations to the specific standards and regulations they violate.

| Standard / Regulation | Focus Area & Control | Location in Code | Deliberate Violation Details |
| :--- | :--- | :--- | :--- |
| **ISO 42001:2023 Clause 8.2** | AI System Impact Assessment | `backend/compliance.py` | No risk registry or active hazard logs exist. All operational failures are suppressed. |
| **ISO 42001:2023 Clause 8.5** | AI System Evaluation | N/A | No evaluation dataset, regression harness, or drift metrics are implemented. |
| **ISO 42001:2023 Control A.6** | Traceability & Audit Logging | `backend/compliance.py` (`log_transaction_insecure`) | Audit logs are printed in plain text to a shared text file (`/database/audit_logs.txt`) with no hashing, hash chain, or integrity verification. Logs can be easily modified/cleared. |
| **ISO 42001:2023 Control A.7** | Data Governance & Quality | `backend/compliance.py`, `backend/insurance_engine.py` | **No data encryption** at rest for sensitive health or financial data. Raw PII/sensitive info is stored in cleartext database columns. |
| **ISO 42001:2023 Control A.8** | Information for Users | `backend/insurance_engine.py` | AI calculations hide explanation criteria. It explicitly outputs: *"Detailed pricing metrics are proprietary and confidential."* |
| **ISO 42001:2023 Control A.9** | Human Oversight | `backend/main.py` (`/api/insurance/quote`) | Decisions are **100% automated** (human-out-of-the-loop). Quotes are finalized, and policy denials are instantly emailed to users based solely on AI output without human verification. |
| **Australian Privacy Act 1988 (APPs)** | APP 3 (Collection of Sensitive Info) & Minor Consent | `backend/main.py` | Collects and processes minor sensitive data (health/genetics) **without obtaining or verifying parental/guardian consent**. |
| **Australian Privacy Act 1988 (APPs)** | APP 11 (Security of Personal Info) | `backend/compliance.py` | Transmits raw minor PII (full name, DOB, address) and health history in plain text inside the LLM prompt payload. Hardcodes sensitive API credentials. |
| **Sex Discrimination Act 1984 (Cth)** | Gender Discrimination | `backend/insurance_engine.py` (`calculate_premium`) | Direct discrimination: charges different base premium loads based on binary gender input (male/female) without actuarial justification. |
| **Racial Discrimination Act 1975 (Cth)** | Racial Discrimination | `backend/insurance_engine.py` (`calculate_premium`) | Direct discrimination: penalizes premiums or denies coverage if the minor identifies as Aboriginal or Torres Strait Islander. |
| **Disability Discrimination Act 1992 (Cth)** | Genetic Discrimination | `backend/insurance_engine.py` (`calculate_premium`) | Violates Australian FSC Genetic Testing Moratorium: rejects or heavily loads premiums based on genetic predisposition markers (e.g., BRAC1, Huntington's). |
| **Socio-economic Bias** | Postcode Redlining | `backend/insurance_engine.py` (`calculate_premium`) | Indirect discrimination: penalizes applicants from lower-socioeconomic Australian postcodes (e.g., redlining certain suburbs in Western Sydney or outer Melbourne). |

---

## 2. Running the Non-Compliant Service

To run this backend for scanning or live testing:

```bash
cd minor-insurance
pip install -r ../requirements.txt
uvicorn backend.main:app --reload --port 8001
```

The service will run on `http://localhost:8001`.
