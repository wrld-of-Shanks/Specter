"""
Specter 2.0 — Semantic RAG Chat Engine
Async version with Redis cache support.
Uses ChromaDB vector search + Gemini for answer generation.
Falls back to retrieval-only mode with structured advice when no LLM is available.
"""

import logging
import re
from typing import Dict, List, Optional

from embed_store import search_chunks
from local_llm import generate_with_context
from cache_service import get_cached_answer, set_cached_answer

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.45
MAX_CONTEXT_CHUNKS = 4
MAX_HISTORY_TURNS = 6

SITUATION_KEYWORDS = {
    "fake_case": [
        r"fake.*case", r"false.*case", r"fabricated.*case", r"false.*implicat",
        r"false\s*allegation", r"wrongly\s*accused", r"fake.*complaint",
        r"false.*complaint", r"fake.*dowry", r"dowry.*fake", r"fake.*498a",
        r"498a.*fake", r"false.*498a", r"498a.*false", r"misuse\s*of\s*498a",
        r"false.*dowry", r"dowry.*false", r"fake.*allegation", r"false.*allegation",
        r"fabricated.*allegation"
    ],
    "divorce": [
        r"divorce", r"separat", r"marriage\s*dissolution", r"mutual\s*consent",
        r"irretrievable", r"cruelty.*divorce", r"cruelty.*husband", r"cruelty.*marriage",
        r"hindu\s*marriage\s*act.*divorce",
        r"grounds?\s*of\s*divorce", r"file.*divorce", r"divorce.*petition",
        r"leave.*husband", r"separate.*husband", r"ending.*marriage", r"end.*marriage"
    ],
    "domestic_violence": [
        r"domestic\s*violence", r"dowry\s*death", r"304b", r"cruelty",
        r"harassment.*dowry", r"dowry.*harassment", r"protection\s*of\s*women",
        r"dv\s*act", r"domestic\s*abuse", r"hitting", r"beating", r"beat\s*(me|her|wife|up)",
        r"physically.*abuse", r"mentally.*abuse", r"verbal.*abuse",
        r"husband.*hit", r"husband.*beat", r"husband.*abuse",
        r"in-laws.*harass", r"in-laws.*torture", r"marital.*abuse",
        r"abuse.*husband", r"torture.*husband", r"violence.*husband",
        r"woman.*abuse", r"wife.*abuse", r"female.*harass"
    ],
    "arrest_bail": [
        r"arrest", r"bail", r"anticipatory\s*bail", r"regular\s*bail",
        r"pre\s*arrest", r"custody", r"police\s*arrest", r"judicial\s*custody",
        r"police\s*remand"
    ],
    "property_dispute": [
        r"property\s*dispute", r"land\s*dispute", r"inheritance", r"succession",
        r"will\s*dispute", r"partition", r"ancestral\s*property", r"immovable\s*property",
        r"transfer\s*of\s*property", r"registration\s*act"
    ],
    "consumer": [
        r"consumer\s*complaint", r"consumer\s*court", r"deficiency\s*of\s*service",
        r"defective\s*goods", r"unfair\s*trade", r"consumer\s*protection",
        r"product\s*liability", r"refund"
    ],
    "cyber_crime": [
        r"cyber\s*crime", r"cyber\s*fraud", r"online\s*fraud", r"phishing",
        r"identity\s*theft", r"hacking", r"it\s*act", r"section\s*66",
        r"online\s*scam", r"social\s*media\s*fraud"
    ],
    "police_complaint": [
        r"police\s*complaint", r"fir", r"zero\s*fir", r"lodge\s*complaint",
        r"police\s*report", r"file\s*complaint", r"criminal\s*complaint",
        r"police\s*station"
    ],
    "landlord_tenant": [
        r"landlord", r"tenant", r"eviction", r"rent\s*agreement", r"rent\s*control",
        r"rental\s*dispute", r"leave\s*and\s*license", r"notice\s*evict"
    ],
}


SITUATION_ADVICE = {
    "fake_case": {
        "title": "What to Do If a Fake Case Is Filed Against You",
        "steps": [
            "Do not panic. Stay calm and avoid destroying any evidence or documents.",
            "Consult a criminal lawyer immediately — do not appear in court without legal representation.",
            "Apply for anticipatory bail (Section 438 CrPC) if there is a risk of arrest.",
            "File a counter-complaint for false implication if you have evidence.",
            "Collect all evidence: call records, messages, emails, witnesses, CCTV footage that prove your innocence.",
            "Do not ignore any court summons — non-appearance can lead to arrest warrant.",
            "If the case is under Section 498A IPC (dowry), the court may refer it to mediation or family court.",
            "Consider filing a defamation case (Section 499/500 IPC) if false allegations have harmed your reputation."
        ],
        "documents": "Call records, messages, emails, bank statements, witness affidavits, proof of absence (alibi)",
        "where_to_go": "High Court (for anticipatory bail), Magistrate Court (for regular bail), Lawyer's office (first step)"
    },
    "divorce": {
        "title": "Divorce Process Under Indian Law",
        "steps": [
            "Decide the grounds: cruelty (Section 13(1)(ia) Hindu Marriage Act), adultery, desertion (2+ years), mutual consent, irretrievable breakdown.",
            "For mutual consent divorce (Section 13B): both parties file a joint petition, wait 6 months (cooling-off period), then file second motion for decree.",
            "For contested divorce: file petition in family court of your jurisdiction (where marriage occurred or where you last resided together).",
            "File for maintenance (Section 125 CrPC / Section 24 Hindu Marriage Act) if you are financially dependent.",
            "If children are involved, file for custody — the court decides based on the child's best interest.",
            "Alimony can be claimed as lump sum or monthly maintenance.",
            "Legal separation (Section 10 Hindu Marriage Act) is an alternative if you do not want complete divorce.",
            "Muslim, Christian, and Parsi divorces are governed by their respective personal laws — consult a specialist.",
            "Download the divorce petition format from the District Court website or get it drafted by a lawyer."
        ],
        "documents": "Marriage certificate, wedding photos, proof of cruelty/desertion (messages, call logs, witness affidavits), income proofs of both parties, child birth certificates, property documents",
        "where_to_go": "Family Court (District Court), or file through a lawyer who practices in family law"
    },
    "domestic_violence": {
        "title": "Protection Against Domestic Violence",
        "steps": [
            "Call 181 (Women's Helpline) or 1091 (Police Helpline for Women) in an emergency.",
            "File a complaint under the Protection of Women from Domestic Violence Act 2005 (DV Act) at the nearest Magistrate court or Protection Officer.",
            "You can get: protection order (stop violence), residence order (stay in shared house), monetary relief (medical expenses, rent), custody of children.",
            "Also file an FIR under Section 498A IPC (cruelty) if there is physical or mental harassment for dowry.",
            "Collect evidence: photographs of injuries, medical reports, WhatsApp messages, threatening calls, witness statements.",
            "Shelter homes (Short Stay Homes) are available in every district — ask the Protection Officer for referral.",
            "You do not need a lawyer to file a DV Act complaint — you can file it yourself in the Magistrate court.",
            "If you are in immediate danger, call the police (100) or go to the nearest police station."
        ],
        "documents": "Medical reports, photographs of injuries, threatening messages/emails, bank statements (for financial abuse), marriage certificate, proof of residence, witness affidavits",
        "where_to_go": "Magistrate Court, Protection Officer (District Social Welfare Office), Women's Helpline (181), Nearest Police Station"
    },
    "arrest_bail": {
        "title": "Bail Process and Your Rights on Arrest",
        "steps": [
            "If arrested: You have the right to remain silent. You have the right to inform a family member or friend. You have the right to meet your lawyer.",
            "The police must produce you before a Magistrate within 24 hours of arrest (Article 22(2) Constitution).",
            "For bailable offences: bail is a right — the police or court must grant it. Check Schedule I of CrPC.",
            "For non-bailable offences: apply for regular bail before the Sessions Court or High Court.",
            "If you anticipate arrest: file an anticipatory bail application (Section 438 CrPC) before the Sessions Court or High Court.",
            "For anticipatory bail: you need a lawyer to draft the application. The court may grant interim protection (no arrest till hearing).",
            "Bail conditions may include: surrendering passport, surety bonds, regular appearances at police station.",
            "If bail is denied, file a bail application in the next higher court — Sessions Court → High Court → Supreme Court."
        ],
        "documents": "Bail application (drafted by lawyer), FIR copy, arrest memo (if arrested), surety documents (property papers, bank statements), identity proof, address proof",
        "where_to_go": "Police Station (for bail in bailable offences), Sessions Court (for regular/anticipatory bail), High Court (for higher bail applications)"
    },
    "property_dispute": {
        "title": "Property Dispute Resolution",
        "steps": [
            "Determine the type of property: ancestral (coparcenary) vs self-acquired — this decides legal rights.",
            "Check the title deed, sale deed, and property records at the Sub-Registrar's office.",
            "For ancestral property disputes: file a civil suit for partition (Section 4 Partition Act 1893) in the Civil Court.",
            "For will/succession disputes: file a probate petition (if there is a will) or succession petition (if no will) in the Civil Court.",
            "Check 7/12 extracts (Record of Rights) at the local Tehsildar office for agricultural land.",
            "Mediation is mandatory in most property suits — try to settle through court-annexed mediation first.",
            "File a caveat if you anticipate someone else filing a case on the same property.",
            "Register all property documents with the Sub-Registrar to avoid future disputes."
        ],
        "documents": "Title deed, sale deed, property tax receipts, 7/12 extract, will (if any), succession certificate, family tree, prior court orders if any",
        "where_to_go": "Civil Court (for partition/succession), Tehsildar Office (for land records), Sub-Registrar Office (for registration)"
    },
    "consumer": {
        "title": "Consumer Complaint Process",
        "steps": [
            "Send a legal notice to the seller/service provider demanding resolution — give 15-30 days.",
            "If no response: file a consumer complaint before the District Consumer Disputes Redressal Commission (DCDRC) for claims up to Rs 1 crore.",
            "For claims Rs 1-10 crore: file at the State Consumer Disputes Redressal Commission (SCDRC).",
            "For claims above Rs 10 crore: file at the National Consumer Disputes Redressal Commission (NCDRC).",
            "You can file the complaint online at https://consumerhelpline.gov.in or https://edaakhil.nic.in.",
            "No lawyer required for consumer court — you can argue your own case (but a lawyer helps).",
            "Compensation can include: refund, replacement, repair, compensation for mental agony, litigation costs.",
            "File within 2 years of the cause of action (when the defect was discovered)."
        ],
        "documents": "Purchase invoice/receipt, warranty/guarantee card, photos/videos of defect, email/chat correspondence with seller, legal notice copy, bill of lading (for goods transport)",
        "where_to_go": "District Consumer Commission (DCDRC), State Consumer Commission (SCDRC), National Consumer Commission (NCDRC), online at consumerhelpline.gov.in"
    },
    "cyber_crime": {
        "title": "How to Report Cyber Crime",
        "steps": [
            "Report immediately to the National Cyber Crime Reporting Portal: https://cybercrime.gov.in.",
            "For financial fraud: call 1930 (Cyber Crime Helpline) within the first hour to freeze the transaction.",
            "Visit the nearest Cyber Crime Police Station with all evidence.",
            "Do not delete any messages, emails, or transaction records — they are evidence.",
            "Take screenshots of the fraudulent messages, emails, or transactions immediately.",
            "Block the fraudulent account/contact and change all your passwords.",
            "File a complaint under IT Act 2000 (Section 66 for hacking, Section 67 for obscene content, Section 66D for cheating by impersonation).",
            "For social media fraud: also report to the platform (Facebook, Instagram, Twitter) through their reporting tools.",
            "If personal photos/videos are leaked, file a complaint under Section 67 IT Act and also approach the cyber cell."
        ],
        "documents": "Screenshots of fraudulent messages/emails, transaction receipts, bank statements, chat logs, email headers, IP address logs (if available)",
        "where_to_go": "https://cybercrime.gov.in (online), Cyber Crime Police Station, Nearest Police Station, Cyber Helpline (1930)"
    },
    "police_complaint": {
        "title": "How to File a Police Complaint (FIR)",
        "steps": [
            "Go to the nearest police station where the offence occurred to file an FIR under Section 154 CrPC.",
            "If the police refuse to file FIR: send the complaint by post to the Superintendent of Police (SP) — it is treated as an FIR (Section 154(3) CrPC).",
            "You can also file a Zero FIR at any police station (even outside your jurisdiction) — it will be transferred to the correct station.",
            "If still no action: file a complaint directly before the Magistrate under Section 156(3) CrPC — the Magistrate can order the police to investigate.",
            "Keep a copy of the FIR free of cost — the police cannot charge you for it.",
            "For online filing: some states allow e-FIR for specific offences (check your state police website).",
            "If the complaint is about missing person: file immediately without 24-hour waiting period (Supreme Court order).",
            "For women: you can file complaints at the Mahila Police Station or Women's Helpline (1091)."
        ],
        "documents": "Written complaint (signed), identity proof (Aadhaar, voter ID), evidence of the offence (photos, videos, documents, witness details)",
        "where_to_go": "Nearest Police Station, Superintendent of Police (SP) Office, Magistrate Court, Online at state police e-FIR portal"
    },
    "landlord_tenant": {
        "title": "Landlord-Tenant Dispute Resolution",
        "steps": [
            "Check the rental agreement / leave-and-license agreement for terms of tenancy and notice period.",
            "For eviction: the landlord must give notice as per the agreement (usually 30-90 days) and file a suit in Civil Court / Small Causes Court.",
            "Tenants cannot be evicted without a court order — forcibly throwing out a tenant is illegal.",
            "For rent default: send a legal notice demanding unpaid rent before filing an eviction suit.",
            "Tenants can file a complaint with the Rent Controller / Rent Tribunal if the landlord refuses to provide basic amenities.",
            "Security deposit must be refunded within the period specified in the agreement, after deducting legitimate damages.",
            "Both parties should document the condition of the property with photos/videos at move-in and move-out.",
            "For disputes under Rs 20,000 monthly rent: file at the Small Causes Court. For higher rents: Civil Court."
        ],
        "documents": "Rental/leave-and-license agreement, rent receipts, bank transfer proofs, house condition photos (move-in/move-out), legal notice copies, property tax receipts",
        "where_to_go": "Small Causes Court, Civil Court, Rent Tribunal (in some states like Maharashtra)"
    },
}


def classify_query(query: str) -> str:
    q = query.lower()
    for situation, patterns in SITUATION_KEYWORDS.items():
        for pattern in patterns:
            if re.search(pattern, q):
                return situation
    return "general"


def build_advice_response(query: str, chunks: List[Dict], situation: str) -> str:
    advice = SITUATION_ADVICE.get(situation)
    parts = []

    if advice:
        parts.append(f"# {advice['title']}\n")
    else:
        parts.append("# Legal Information\n")

    if chunks:
        legal_info = []
        for i, c in enumerate(chunks, 1):
            legal_info.append(f"[{i}] {c['text']}")
        parts.append("## What the Law Says\n" + "\n\n".join(legal_info))

    if advice:
        parts.append("## Steps You Can Take")
        for j, step in enumerate(advice["steps"], 1):
            parts.append(f"{j}. {step}")

        parts.append(f"## Documents You Will Need\n{advice['documents']}")

        parts.append(f"## Where to Go\n{advice['where_to_go']}")

    user_situation = query.strip()
    if user_situation and situation != "general":
        parts.append("## About Your Situation")
        parts.append(
            f"You asked: \"{user_situation}\"\n\n"
            "The steps above are general guidance. For your specific situation, "
            "the exact process may vary based on the facts of your case."
        )

    lines = []
    for item in parts:
        lines.append(item)
        lines.append("")

    disclaimer = (
        "⚠️ **Important**: This information is for educational purposes only and does not "
        "constitute legal advice. Laws may vary by state and individual circumstances. "
        "Please consult a qualified advocate for advice specific to your situation."
    )
    lines.append(f"---\n{disclaimer}")

    return "\n".join(lines).strip()


SYSTEM_PROMPT = """You are SPECTER, an AI legal assistant specialized in Indian law.
You help ordinary Indian citizens understand their legal rights and obligations.

Rules you must follow:
1. Answer ONLY based on the provided legal context and your knowledge of Indian statutes.
2. If the context does not contain enough information, say so clearly — do not hallucinate.
3. Always cite the specific law, section, or act when you reference it (e.g. "Section 498A IPC", "Section 9 of The Hindu Marriage Act 1955").
4. Use simple, plain English. Avoid legal jargon unless you immediately explain it.
5. If the user's question implies an emergency (arrest, domestic violence, eviction), lead with the most urgent actionable advice.
6. Never provide advice that requires a licensed advocate — always recommend consulting one for serious matters.
7. Keep answers concise: under 300 words unless the question requires more detail."""


def build_rag_prompt(
    query: str,
    context_chunks: List[Dict],
    chat_history: Optional[List[Dict]] = None
) -> List[Dict]:
    if context_chunks:
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            context_parts.append(
                f"[Source {i}: {chunk['source']} | confidence {chunk['score']:.0%}]\n{chunk['text']}"
            )
        context_block = "\n\n---\n\n".join(context_parts)
    else:
        context_block = "No specific legal context retrieved. Answer from general Indian law knowledge."

    user_message = (
        f"Legal context retrieved:\n\n{context_block}\n\n"
        f"---\n\nUser question: {query}"
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if chat_history:
        messages.extend(chat_history[-MAX_HISTORY_TURNS:])

    messages.append({"role": "user", "content": user_message})
    return messages


async def answer_query_with_rag(
    query: str,
    user_id: str = None,
    chat_history: Optional[List[Dict]] = None,
    namespace: str = "global",
    mode: str = "default"
) -> Dict:
    try:
        logger.info(f"[RAG] Processing query for user={user_id}: {query[:80]}")

        cached = await get_cached_answer(query, namespace)
        if cached:
            logger.info(f"[RAG] Cache hit for query in namespace '{namespace}'")
            return cached

        chunks = search_chunks(query, top_k=MAX_CONTEXT_CHUNKS, namespace=namespace)

        confident_chunks = [c for c in chunks if c["score"] >= SIMILARITY_THRESHOLD]
        low_confidence = len(confident_chunks) == 0

        if low_confidence:
            logger.info(f"[RAG] No chunks above threshold {SIMILARITY_THRESHOLD}. Using low-confidence context.")
            confident_chunks = chunks[:2]

        messages = build_rag_prompt(query, confident_chunks, chat_history)

        system_msg = messages[0]["content"]
        user_parts = []
        for msg in messages[1:]:
            prefix = "User" if msg["role"] == "user" else "Assistant"
            user_parts.append(f"{prefix}: {msg['content']}")
        full_user_prompt = "\n\n".join(user_parts)

        answer = None
        try:
            answer = generate_with_context(system_msg, full_user_prompt, temperature=0.2)
        except Exception as e:
            logger.warning(f"LLM generation failed: {e}. Falling back to retrieval-only mode.")

        sources = list({c["source"] for c in confident_chunks}) if confident_chunks else []
        avg_confidence = (
            sum(c["score"] for c in confident_chunks) / len(confident_chunks)
            if confident_chunks else 0.0
        )

        if answer is None or answer.startswith("Error:"):
            situation = classify_query(query)
            logger.info(f"[RAG] Classified query as: {situation}")
            answer = build_advice_response(query, confident_chunks, situation)

        result = {
            "answer": answer,
            "sources": sources,
            "confidence": round(avg_confidence, 3),
            "matched_chunks": [
                {"source": c["source"], "score": c["score"], "preview": c["text"][:120]}
                for c in confident_chunks
            ],
            "low_confidence": low_confidence,
        }

        await set_cached_answer(query, result, namespace)
        return result

    except Exception as e:
        logger.error(f"[RAG] Error: {e}", exc_info=True)
        return {
            "answer": "I encountered an error processing your query. Please try again.",
            "sources": [],
            "confidence": 0.0,
            "matched_chunks": [],
            "low_confidence": True,
        }
