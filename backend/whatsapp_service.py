"""
WhatsApp Service — Twilio webhook to receive WhatsApp messages and respond via RAG engine.
"""

import logging
from fastapi import APIRouter, Request, HTTPException, Form
from typing import Optional
from chat_engine_rag import answer_query_with_rag

logger = logging.getLogger(__name__)

whatsapp_router = APIRouter()


@whatsapp_router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    try:
        form = await request.form()
        body = form.get("Body", "").strip()
        from_number = form.get("From", "").strip()
        wa_id = form.get("WaId", "").strip()

        if not body:
            return {"error": "Empty message"}

        logger.info(f"[WhatsApp] From: {from_number}, Body: {body[:100]}")

        result = await answer_query_with_rag(
            query=body,
            user_id=f"whatsapp:{wa_id or from_number}",
            namespace="global",
        )

        response_text = result.get("answer", "I'm sorry, I couldn't process your request.")
        if result.get("low_confidence"):
            response_text += "\n\n⚠️ Please note: I couldn't find a precise match in my legal database for this question."

        return {"message": response_text}
    except Exception as e:
        logger.error(f"[WhatsApp] Webhook error: {e}", exc_info=True)
        return {"message": "Sorry, an error occurred processing your message. Please try again later."}


@whatsapp_router.get("/whatsapp/webhook")
async def whatsapp_webhook_verify(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    hub_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")

    verify_token = "specter_whatsapp_verify_2025"

    if hub_mode == "subscribe" and hub_token == verify_token:
        logger.info("[WhatsApp] Webhook verified successfully")
        return int(hub_challenge) if hub_challenge and hub_challenge.isdigit() else hub_challenge

    logger.warning("[WhatsApp] Webhook verification failed")
    raise HTTPException(status_code=403, detail="Verification failed")
