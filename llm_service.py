import os
import json
import re
import asyncio
from groq import AsyncGroq
from models import TicketRequest

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = AsyncGroq(api_key=GROQ_API_KEY)
MODEL_NAME = "qwen/qwen3.6-27b"

def clean_json_response(raw_text: str) -> str:
    """Extracts JSON even if the LLM adds conversational text or markdown before/after it."""
    clean_text = raw_text.strip()
    start_idx = clean_text.find('{')
    end_idx = clean_text.rfind('}')
    
    if start_idx != -1 and end_idx != -1:
        return clean_text[start_idx:end_idx+1]
    return clean_text

def apply_safety_guardrails(response_dict: dict) -> dict:
    """
    The Ironclad Safety Layer.
    Independently verifies user-facing replies and internal actions.
    """
    customer_reply = response_dict.get("customer_reply", "")
    next_action = response_dict.get("recommended_next_action", "")

    # Safety Rule 1: NEVER ask for PIN, OTP, password, or card number
    credential_pattern = re.compile(r"(?i)\b(pin|otp|password|card number)\b")
    if credential_pattern.search(customer_reply):
        response_dict["customer_reply"] = (
            "We have received your request. Our support team is currently reviewing your case. "
            "Please remember we will never ask for your PIN, OTP, or password. Do not share them with anyone."
        )

    # Safety Rule 2A: Never confirm a refund/reversal to the CUSTOMER
    reply_promise_pattern = re.compile(r"(?i)(will refund|refund you|process a refund for you|issue a refund|refund is completed|reversing your|reverse the|unblock your account|get your money back)")
    if reply_promise_pattern.search(customer_reply):
        response_dict["customer_reply"] = (
            "We have noted your concern. Our team will carefully review the case "
            "and any eligible amount will be returned through official channels. "
            "Please do not share your PIN or OTP with anyone."
        )

    # Safety Rule 2B: Never explicitly COMMAND an unauthorized financial action internally
    action_promise_pattern = re.compile(r"(?i)(refund the customer immediately|unblock the account automatically)")
    if action_promise_pattern.search(next_action):
        response_dict["recommended_next_action"] = "Investigate the case and determine eligibility for financial action per company policy."

    return response_dict

def build_system_prompt() -> str:
  
    return """You are the QueueStorm Investigator, an AI copilot for fintech support agents.
Your job is to analyze a customer complaint alongside their recent transaction history.

CRITICAL RULES:
1. MATCHING: If the complaint perfectly matches one transaction, output its ID. 
2. AMBIGUOUS MATCHES: If MULTIPLE transactions plausibly match (e.g. duplicate amounts on the same day) and you cannot confidently tell which one the user means, you MUST output "relevant_transaction_id": null (as a JSON null value, DO NOT use string "null"). Set "evidence_verdict": "insufficient_data", "case_type": "wrong_transfer" (or relevant type), and ask the user to clarify. DO NOT GUESS.
3. AGENT ISSUES: If the user complains about a pending agent cash-in not reflecting, set "severity" to "high", "department" to "agent_operations", and "human_review_required" to true.
4. PHISHING/SCAM: If the user reports suspicious calls asking for OTP/PIN, set severity to "critical", department to "fraud_risk", and relevant_transaction_id to null.
5. MERCHANT REFUNDS: If a user wants a refund for a completed merchant payment, route to "customer_support".
6. SAFETY: NEVER ask the user for PIN, OTP, or password. NEVER promise a refund to the user (instead, say "any eligible amount will be returned through official channels").
7. LANGUAGE: Write the "customer_reply" in the SAME language as the user's complaint (English, Bangla, or Banglish).

Respond ONLY with a valid JSON object matching this schema exactly. BE EXTREMELY CONCISE in your text fields:
{
  "relevant_transaction_id": "TXN-ID" or null,
  "evidence_verdict": "consistent | inconsistent | insufficient_data",
  "case_type": "wrong_transfer | payment_failed | refund_request | duplicate_payment | merchant_settlement_delay | agent_cash_in_issue | phishing_or_social_engineering | other",
  "severity": "low | medium | high | critical",
  "department": "customer_support | dispute_resolution | payments_ops | merchant_operations | agent_operations | fraud_risk",
  "agent_summary": "Strictly 1 short sentence summarizing the case",
  "recommended_next_action": "Strictly 1 short operational next step",
  "customer_reply": "Strictly 1 to 2 short sentences. Safe reply to the customer in their language",
  "human_review_required": true | false,
  "confidence": 0.9,
  "reason_codes": ["array", "of", "1-word", "reasons"]
}"""

async def process_ticket_with_llm(ticket: TicketRequest) -> dict:
    """Calls Groq API with a 20-second timeout, extracts JSON safely, and applies safety filters."""
    
    safe_fallback = {
        "ticket_id": ticket.ticket_id,
        "relevant_transaction_id": None,
        "evidence_verdict": "insufficient_data",
        "case_type": "other",
        "severity": "medium",
        "department": "customer_support",
        "agent_summary": "Automated fallback triggered due to processing delay, formatting error, or missing evidence. Manual review required.",
        "recommended_next_action": "Review the customer's transaction history manually.",
        "customer_reply": "Thank you for reaching out. Our support team is currently reviewing your request. Please do not share your PIN or OTP with anyone.",
        "human_review_required": True,
        "confidence": 0.0,
        "reason_codes": ["fallback_triggered"]
    }
    
    user_prompt = f"""
<transaction_history>
{json.dumps([t.model_dump() for t in ticket.transaction_history], indent=2)}
</transaction_history>

<user_complaint>
{ticket.complaint}
</user_complaint>
"""
    try:
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": build_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=4096
            ),
            timeout=20.0
        )
    
        raw_text = response.choices[0].message.content
        clean_json_str = clean_json_response(raw_text)
        response_dict = json.loads(clean_json_str)
     
        response_dict["ticket_id"] = ticket.ticket_id
        
        return apply_safety_guardrails(response_dict)

    except (asyncio.TimeoutError, Exception) as e:
        error_msg = str(e).replace('"', "'") 
        print(f"Groq API Error/Timeout for ticket {ticket.ticket_id}: {error_msg}")
        safe_fallback["reason_codes"] = ["fallback_triggered", f"Error: {error_msg}"[:60]]
        return safe_fallback