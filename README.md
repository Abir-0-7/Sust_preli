 QueueStorm Investigator

SUST CSE Carnival 2026 · Codex Community Hackathon · Online Preliminary

When money is on the line, customer support can't afford to guess. That's why we built QueueStorm Investigator—an AI-powered SupportOps copilot that acts as a lightning-fast detective for digital finance.

Instead of blindly classifying a customer's chat message, our API reads the complaint, cross-references their actual transaction history, and figures out exactly what went wrong. Most importantly? It does it all safely, without ever making unauthorized financial promises or asking for passwords.

🌍 Live Deployment (Ready for Judging)

We've already deployed our API, so you don't need to spin anything up to evaluate us!

Base URL: https://sust-preli-qdwe.onrender.com

Health Check: GET https://sust-preli-qdwe.onrender.com/health

Analyze Ticket: POST https://sust-preli-qdwe.onrender.com/analyze-ticket

(Note: We're hosted on Render's free/starter tier, so the very first request might take a few extra seconds if the server is waking up from sleep. Subsequent requests will be lightning fast!)

🧠 Our AI Strategy: Brains + Brawn

Model: qwen/qwen3.6-27b (via Groq)
Approach: Hybrid (LLM + Strict Rule-Based Guardrails)

Our philosophy is simple: Let the AI do the reasoning, but let the code do the enforcing.

We chose the Qwen 3.6 27B model because it’s surprisingly smart at matching transaction timestamps and amounts, and it handles the mix of English, Bangla, and Banglish natively. Plus, Groq's LPU inference engine ensures we secure maximum performance points and stay well under the judges' 30-second timeout limit.

However, we do not trust the LLM to govern itself. The AI handles the natural language understanding, and our Python layer acts as the absolute bouncer.

🛡️ The "Ironclad" Safety Layer

To score maximum points in the Safety & Escalation category, we built this system assuming the AI might occasionally try to give away the bank's money. We implemented strict safety guardrails that override the LLM:

The Credential Firewall: If the AI's generated customer_reply accidentally asks for a "PIN", "OTP", "card number", or "password", a regex filter instantly intercepts it and rewrites the message to warn the user never to share those details.

No Empty Promises: The AI cannot authorize refunds. If it tries to say "We will refund you" or "We are reversing the transaction", our system aggressively strips that out and replaces it with the safe, legal-approved phrase: "any eligible amount will be returned through official channels."

Schema Coercion: Pydantic V2 strictly coerces any AI hallucinations. If the model invents a non-existent department, field validators catch it and silently default it to a safe value (like customer_support) so the API never crashes.

The Ultimate Timeout Fallback: The Groq API call is wrapped in a strict 20-second timeout. If the LLM hangs, we immediately yield a hardcoded, perfectly validated JSON response. We will never fail the judge's 30-second timeout.

📡 API Endpoints at a Glance

GET /health

A quick pulse check for the automated judging harness.

curl https://sust-preli-qdwe.onrender.com/health


Response:

{
  "status": "ok"
}


POST /analyze-ticket

The brains of the operation. Feed it a complaint and a transaction list, and watch it work.

Sample Request:

curl -X POST https://sust-preli-qdwe.onrender.com/analyze-ticket \
-H "Content-Type: application/json" \
-d '{
  "ticket_id": "TKT-001",
  "complaint": "I sent 5000 taka to a wrong number around 2pm today. Please help me get my money back.",
  "language": "en",
  "transaction_history": [
    {
      "transaction_id": "TXN-9101",
      "timestamp": "2026-04-14T14:08:22Z",
      "type": "transfer",
      "amount": 5000,
      "counterparty": "+8801719876543",
      "status": "completed"
    }
  ]
}'


Sample Response:

{
  "ticket_id": "TKT-001",
  "relevant_transaction_id": "TXN-9101",
  "evidence_verdict": "consistent",
  "case_type": "wrong_transfer",
  "severity": "high",
  "department": "dispute_resolution",
  "agent_summary": "Customer reports sending 5000 BDT via TXN-9101 to +8801719876543, which they now believe was the wrong recipient.",
  "recommended_next_action": "Verify TXN-9101 details with the customer and initiate the wrong-transfer dispute workflow per policy.",
  "customer_reply": "We have noted your concern about transaction TXN-9101. Please do not share your PIN or OTP with anyone. Our dispute team will review the case.",
  "human_review_required": true,
  "confidence": 0.9,
  "reason_codes": [
    "wrong_transfer",
    "transaction_match"
  ]
}


🚀 Local Setup (If you really want to)

Want to spin this up locally anyway? It takes less than two minutes.

1. Prerequisites

Python 3.9+

A valid Groq API Key

2. Installation

Clone the repository and jump into the directory:

git clone <your-repo-url>
cd <your-repo-directory>

# Create and activate a fresh virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the essentials
pip install -r requirements.txt


3. Environment Variables

Create a .env file in the root directory. (Note: As per the hackathon rules, we never commit real secrets to GitHub!)

GROQ_API_KEY=your_real_groq_api_key_here


4. Boot the Server

Run the FastAPI application.

uvicorn main:app --host 0.0.0.0 --port 8000


Your local API is now live at: http://localhost:8000

⚠️ Known Limitations & Disclaimers

Let's be real—no hackathon project is perfect. Here is what we're keeping an eye on:

Super Ambiguous Complaints: If a user submits total gibberish without any matching transaction data, our AI is instructed not to guess. It conservatively defaults to insufficient_data and asks for clarification.

Cold Starts: Because we are deployed on a serverless/free-tier hosting platform (Render), the API might take an extra 30-50 seconds to boot up if it hasn't received traffic in a while.

Data Privacy Promise: This application uses synthetic data only. We are not connecting this to any real customer databases, live payment APIs, or actual production environments.

Built with ❤️ (and a lot of coffee) for the SUST CSE Carnival 2026.