# **QueueStorm Investigator**

### **SUST CSE Carnival 2026 · Codex Community Hackathon · Online Preliminary**

When customers contact a financial service, they expect fast and accurate support not generic replies.

**QueueStorm Investigator** is an AI powered SupportOps copilot that helps support teams understand customer complaints by comparing them with transaction history. Instead of simply classifying a message, it identifies the most relevant transaction, determines what likely happened, and recommends the appropriate next step.

Since financial support requires a high level of trust, the system is built with strict safety guardrails. It never asks customers for sensitive information, never makes unauthorized financial promises, and always prefers a safe response over an uncertain one.

---

# **Live Deployment**

The API is already deployed and ready for evaluation.

**Base URL**

```text
https://sust-preli-qdwe.onrender.com
```

**Health Check**

```http
GET /health
```

**Analyze Ticket**

```http
POST /analyze-ticket
```

> **Note:** The project is hosted on Render's free tier. If the service has been idle, the first request may take a little longer while the server wakes up.

---

# **How It Works**

**Model:** `qwen/qwen3.6-27b` (via Groq)

**Architecture:** Hybrid (LLM + Rule-Based Validation)

We use the language model for what it does best understanding natural language and connecting customer complaints with transaction records.

Everything else is enforced by our application logic.

The AI analyzes the complaint, identifies the most relevant transaction, summarizes the issue, and prepares a response. Before anything is returned to the user, our validation layer checks every field to ensure it follows predefined rules and company policies.

This combination gives us the flexibility of an LLM with the reliability of deterministic code.

---

# **Safety First**

Financial applications shouldn't rely solely on AI-generated responses. That's why every response passes through multiple safety checks.

## **Credential Protection**

If the generated reply accidentally asks for a customer's PIN, OTP, password, or card number, our safety filter immediately removes it and replaces it with a reminder **never to share sensitive information**.

---

## **No Unauthorized Refund Promises**

The model is never allowed to promise refunds or transaction reversals.

If it generates statements such as:

* "We will refund your money."
* "Your transaction has been reversed."

they are automatically replaced with a safer message indicating that **any eligible amount will be processed through official channels after review.**

---

## **Strict Response Validation**

Every AI response is validated using **Pydantic V2**.

If an unexpected value appears for example, an invalid department name the system automatically replaces it with a safe default instead of returning an invalid response.

---

## **Reliable Fallback**

The Groq API is protected by a 20 seconds timeout.

If the model becomes unavailable or takes too long to respond, the application immediately returns a predefined, fully validated fallback response. This ensures the API always stays within the hackathon's response time requirements.

---

# **API Endpoints**

## **GET `/health`**

Returns a simple health status.

```bash
curl https://sust-preli-qdwe.onrender.com/health
```

**Response**

```json
{
  "status": "ok"
}
```

---

## **POST `/analyze-ticket`**

Analyzes a customer complaint together with transaction history.

The endpoint:

* Finds the matching transaction
* Determines the likely issue
* Assigns severity
* Routes the ticket to the correct department
* Generates a safe customer response

### **Sample Request**

```bash
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
```

### **Sample Response**

```json
{
  "ticket_id": "TKT-001",
  "relevant_transaction_id": "TXN-9101",
  "evidence_verdict": "consistent",
  "case_type": "wrong_transfer",
  "severity": "high",
  "department": "dispute_resolution",
  "agent_summary": "Customer reports sending 5000 BDT via TXN-9101 to the wrong recipient.",
  "recommended_next_action": "Verify the transaction details and begin the standard dispute process.",
  "customer_reply": "We've received your report regarding transaction TXN-9101. Please don't share your PIN or OTP with anyone. Our support team will review the case and guide you through the next steps.",
  "human_review_required": true,
  "confidence": 0.9,
  "reason_codes": [
    "wrong_transfer",
    "transaction_match"
  ]
}
```

---

# **Running the Project Locally**

## **Requirements**

* Python 3 or later
* A valid Groq API key

### **Installation**

```bash
git clone <your-repo-url>
cd <your-repo-directory>

python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### **Environment Variables**

Create a `.env` file:

```env
GROQ_API_KEY=your_real_groq_api_key_here
```

### **Start the Server**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The application will be available at:

```text
http://localhost:8000
```

---

# **Known Limitations**

### **Highly Ambiguous Complaints**

If a complaint doesn't provide enough information and no transaction can be matched, the system avoids making assumptions. Instead, it classifies the case as `insufficient_data` and asks the customer for more details.

### **Cold Starts**

Since the application is hosted on Render's free tier, the first request after a period of inactivity may take **30-50 seconds** while the service starts.

### **Data Privacy**

This project uses **synthetic data only** and is intended for demonstration purposes. It does not connect to real banking systems, customer databases, or payment gateways.