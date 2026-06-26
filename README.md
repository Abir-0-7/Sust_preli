QueueStorm Investigator

An AI-powered SupportOps copilot built for the SUST CSE Carnival 2026 Hackathon. It rapidly analyzes fintech customer complaints, cross-references transaction histories, and safely routes tickets without making unauthorized financial promises.
Tech Stack

Web Framework: FastAPI (Python) - Chosen for high-performance async processing and robust error handling.

Validation: Pydantic V2 - Ensures strict compliance with the 15-point API Contract schema and gracefully coerces AI hallucinations.

LLM Provider: Groq API (qwen/qwen3.6-27b).

Why Groq & Qwen? Groq's LPU inference engine delivers ultra-low latency, guaranteeing we secure maximum performance points and stay well under the 30-second strict limit. The qwen3.6-27b model provides excellent logical reasoning for transaction matching and handles Bangla/Banglish contexts effectively.

Safety & Escalation Logic (The Ironclad Layer)

We do not trust the LLM with fintech safety. After the LLM generates a response, it passes through a strict Python Regex verification layer:

Credential Protection: If the customer_reply contains "PIN", "OTP", or "password", it is programmatically overwritten with a safe warning template.

Financial Promise Protection: If either the customer_reply or recommended_next_action attempts to confirm a refund or reversal, it is stripped and replaced with "any eligible amount will be returned through official channels."

Prompt Injection Sandbox: User complaints are wrapped in <user_complaint> XML tags in the prompt to prevent adversarial instructions from overriding system rules.

Known Limitations & Edge Cases

API Timeouts: If the external LLM API takes longer than 20 seconds, the system automatically aborts the request and yields a hardcoded, perfectly validated "Safe Fallback" JSON response. This ensures the 30-second judge harness timeout is never breached.

Enum Hallucinations: If the LLM generates an invalid category (e.g. department: tech_support), Pydantic @field_validator functions intercept it and coerce it to a safe default (customer_support) instead of crashing the endpoint.

🚀 RUNBOOK (Local Deployment)

1. Clone and Navigate

git clone <your-repo-url>
cd <your-repo-directory>


2. Set Up Virtual Environment

python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate


3. Install Dependencies

pip install fastapi uvicorn pydantic groq
# Or if using requirements.txt: pip install -r requirements.txt


4. Environment Variables
Create a .env file in the root directory (do NOT commit this file to GitHub). You will need:

GROQ_API_KEY=your_real_groq_api_key_here


5. Run the Service

uvicorn main:app --host 0.0.0.0 --port 8000


6. Testing the API
The API will be available at http://localhost:8000.

Check Health: curl http://localhost:8000/health

Test Ticket Analysis: Send a POST request to http://localhost:8000/analyze-ticket matching the schema provided in the hackathon guidelines.