# QueueStorm Investigator

An AI-powered SupportOps copilot built for the SUST CSE Carnival 2026 Hackathon. It rapidly analyzes fintech customer complaints, cross-references transaction histories, and safely routes tickets without making unauthorized financial promises.

## Tech Stack
*   **Web Framework:** FastAPI (Python) - Chosen for high-performance async processing and robust error handling.
*   **Validation:** Pydantic V2 - Ensures strict compliance with the 15-point API Contract schema and gracefully coerces AI hallucinations.
*   **LLM Provider:** OpenRouter API (`google/gemini-1.5-flash`). 
    *   *Why Gemini?* It delivers sub-5-second latency (guaranteeing maximum performance points) and possesses superior native understanding of Bangla and Banglish script.

## Safety & Escalation Logic (The Ironclad Layer)
We do not trust the LLM with fintech safety. After the LLM generates a response, it passes through a strict Python Regex verification layer:
1.  **Credential Protection:** If the `customer_reply` contains "PIN", "OTP", or "password", it is programmatically overwritten with a safe warning template.
2.  **Financial Promise Protection:** If either the `customer_reply` or `recommended_next_action` attempts to confirm a refund or reversal, it is stripped and replaced with *"any eligible amount will be returned through official channels."*
3.  **Prompt Injection Sandbox:** User complaints are wrapped in `<user_complaint>` XML tags in the prompt to prevent adversarial instructions from overriding system rules.

## Known Limitations & Edge Cases
*   **API Timeouts:** If the external LLM API takes longer than 15 seconds, the system automatically aborts the request and yields a hardcoded, perfectly validated "Safe Fallback" JSON response. This ensures the 30-second judge harness timeout is never breached.
*   **Enum Hallucinations:** If the LLM generates an invalid category (e.g. `department: tech_support`), Pydantic `@field_validator` functions intercept it and coerce it to a safe default (`customer_support`) instead of crashing.

---

## 🚀 RUNBOOK (Local Deployment)

**1. Clone and Navigate**
```bash
git clone <your-repo-url>
cd <your-repo-directory>