"""
Template Service — Legal document template generator.
Provides common Indian legal document templates with AI-powered content generation.
"""

import logging
from typing import Dict, List, Optional
from local_llm import generate_with_context

logger = logging.getLogger(__name__)

TEMPLATE_CATEGORIES = {
    "agreements": ["rent_agreement", "employment_contract", "nda", "service_agreement", "partnership_deed"],
    "notices": ["legal_notice", "cheque_bounce_notice", "eviction_notice", "termination_notice"],
    "affidavits": ["general_affidavit", "income_affidavit", "marriage_affidavit"],
    "property": ["sale_deed", "gift_deed", "will", "power_of_attorney"],
    "family": ["marriage_certificate", "divorce_petition", "maintenance_application"],
}

TEMPLATE_STRUCTURES = {
    "rent_agreement": {
        "title": "Rent Agreement",
        "description": "Standard residential rent agreement as per Indian law",
        "sections": ["Parties", "Property Description", "Term", "Rent", "Security Deposit", "Utilities", "Maintenance", "Termination", "Jurisdiction"],
    },
    "nda": {
        "title": "Non-Disclosure Agreement",
        "description": "Mutual NDA for business confidentiality",
        "sections": ["Parties", "Definition of Confidential Information", "Obligations", "Exclusions", "Term", "Remedies", "Jurisdiction"],
    },
    "legal_notice": {
        "title": "Legal Notice",
        "description": "Formal legal notice under Section 80 CPC or other relevant acts",
        "sections": ["Sender Details", "Recipient Details", "Subject", "Facts", "Cause of Action", "Relief Sought", "Deadline for Compliance"],
    },
    "general_affidavit": {
        "title": "General Affidavit",
        "description": "Sworn affidavit for use before Indian courts or authorities",
        "sections": ["Deponent Details", "Statement of Facts", "Verification", "Attestation"],
    },
    "sale_deed": {
        "title": "Sale Deed",
        "description": "Property sale deed for immovable property transfer",
        "sections": ["Parties", "Property Schedule", "Sale Consideration", "Payment Terms", "Possession", "Title Warranty", "Indemnity", "Jurisdiction"],
    },
}


def list_categories() -> Dict:
    return TEMPLATE_CATEGORIES


def list_templates_in_category(category: str) -> List[Dict]:
    template_keys = TEMPLATE_CATEGORIES.get(category, [])
    result = []
    for key in template_keys:
        info = TEMPLATE_STRUCTURES.get(key, {})
        result.append({
            "id": key,
            "title": info.get("title", key.replace("_", " ").title()),
            "description": info.get("description", ""),
            "sections": info.get("sections", []),
        })
    return result


def get_template_structure(template_id: str) -> Optional[Dict]:
    info = TEMPLATE_STRUCTURES.get(template_id)
    if not info:
        return None
    return {
        "id": template_id,
        "title": info["title"],
        "description": info["description"],
        "sections": info["sections"],
    }


def generate_template_document(template_id: str, user_inputs: Dict) -> str:
    info = TEMPLATE_STRUCTURES.get(template_id)
    if not info:
        raise ValueError(f"Unknown template: {template_id}")

    system_prompt = f"""You are an expert legal document drafter specialized in Indian law.
Generate a professional {info['title']} based on the user's inputs.
Use proper Indian legal format and language.
Include all necessary legal clauses, parties, dates, and jurisdictional details.
Format with clear section headings and proper indentation."""

    inputs_str = "\n".join([f"- {k}: {v}" for k, v in user_inputs.items()])
    sections_str = "\n".join([f"- {s}" for s in info["sections"]])

    user_prompt = f"""Generate a complete {info['title']} with the following details:

User Provided Information:
{inputs_str}

Required Sections to Include:
{sections_str}

Output a complete, ready-to-use legal document in plain text format.
Use proper formatting with section headers (e.g., "SECTION 1: PARTIES").
Include placeholders in [brackets] for any missing information."""

    try:
        document = generate_with_context(system_prompt, user_prompt, temperature=0.15)
        return document
    except Exception as e:
        logger.error(f"Template generation failed: {e}")
        return f"Error generating template: {str(e)}. Please ensure the LLM service is running."
