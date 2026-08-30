"""
Verification Service

This module contains the core business logic
for TrustGate-AI verification.
"""

from backend.services.claim_extraction_service import (
    extract_claims,
    split_compound_claim,
    clean_claim
)

from backend.services.claim_classification_service import classify_claim


def verify_response(question, response):
    """
    Process the user input.

    Parameters:
        question (str)
        response (str)

    Returns:
        dict
    """

    question = question.strip()
    response = response.strip()

    if not question:
        return {
            "success": False,
            "message": "Question cannot be empty."
        }

    if not response:
        return {
            "success": False,
            "message": "AI response cannot be empty."
        }

    claims = extract_claims(response)

    final_claims = []

    for claim in claims:
        split_claims = split_compound_claim(claim)

        for split_claim in split_claims:
            cleaned_claim = clean_claim(split_claim)

            if cleaned_claim is not None:
                claim_type = classify_claim(cleaned_claim)

                final_claims.append({
                    "text": cleaned_claim,
                    "type": claim_type
                })

    return {
        "success": True,
        "question": question,
        "response": response,
        "claims": final_claims
    }