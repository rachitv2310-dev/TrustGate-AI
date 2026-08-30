"""
Claim Classification Service

This module is responsible for classifying
claims extracted from AI-generated responses.
"""


def classify_claim(claim):
    """
    Classify a claim into a basic category.

    Parameters:
        claim (str): Extracted claim text.

    Returns:
        str: Claim category.
    """

    claim_lower = claim.lower().strip()

    opinion_markers = [
        "i think",
        "i believe",
        "in my opinion",
        "i feel",
        "i like",
        "i love",
        "i hate",
        "beautiful",
        "amazing",
        "wonderful",
        "terrible"
    ]
    
    unverifiable_markers = [
    "the best",
    "the worst",
    "the greatest",
    "the most beautiful",
    "the most amazing",
    "better than",
    "worse than"
]
    if any(marker in claim_lower for marker in unverifiable_markers):
            return "UNVERIFIABLE"
    if any(marker in claim_lower for marker in opinion_markers):
        return "OPINION"

    return "FACTUAL"

if __name__ == "__main__":
    from claim_extraction_service import (
    extract_claims,
    split_compound_claim,
    clean_claim
)

    test_response = (
        "Who is the Prime Minister of India? "
        "Mumbai is the capital of Maharashtra. "
        "India has a large population and China has a large population. "
        "I think Mumbai is a beautiful city."
    )

    claims = extract_claims(test_response)

    final_claims = []

    for claim in claims:
        split_claims = split_compound_claim(claim)

        for split_claim in split_claims:
            cleaned_claim = clean_claim(split_claim)

            if cleaned_claim is not None:
                final_claims.append(cleaned_claim)

    print("\nClassified Claims:")

    for claim in final_claims:
        category = classify_claim(claim)

        print("-", claim)
        print("  Type:", category)