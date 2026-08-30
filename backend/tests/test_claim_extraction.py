from backend.services.claim_extraction_service import (
    extract_claims,
    split_compound_claim,
    clean_claim
)


test_cases = [
    {
        "name": "Simple Factual Claim",
        "input": "Mumbai is the capital of Maharashtra."
    },
    {
        "name": "Multiple Factual Claims",
        "input": (
            "Mumbai is the capital of Maharashtra. "
            "New Delhi is the capital of India."
        )
    },
    {
        "name": "Compound Claims",
        "input": (
            "India has a large population and "
            "China has a large population."
        )
    },
    {
        "name": "Question Plus Claim",
        "input": (
            "What is the capital of India? "
            "New Delhi is the capital of India."
        )
    },
    {
        "name": "Opinion Plus Fact",
        "input": (
            "Mumbai is the capital of Maharashtra. "
            "I think Mumbai is a beautiful city."
        )
    },
    {
        "name": "Duplicate Claims",
        "input": (
            "Mumbai is the capital of Maharashtra. "
            "MUMBAI IS THE CAPITAL OF MAHARASHTRA."
        )
    },
    {
        "name": "Complex Sentence",
        "input": (
            "India, which is located in South Asia, "
            "became independent in 1947."
        )
    },
    {
        "name": "Numerical Claim",
        "input": (
            "India has a population of over 1.4 billion people."
        )
    },
    {
        "name": "Negative Claim",
        "input": (
            "Mumbai is not the capital of India."
        )
    },
    {
        "name": "Uncertain Statement",
        "input": (
            "The treatment may reduce symptoms in some patients."
        )
    },
    {
        "name": "Comparative Claim",
        "input": (
            "China has a larger population than Japan."
        )
    },
    {
        "name": "Pronoun Compound Claim",
        "input": (
            "The Earth revolves around the Sun and "
            "it rotates on its axis."
        )
    },
    {
        "name": "Mixed Fact and Description",
        "input": (
            "The Taj Mahal was built by Shah Jahan "
            "and is a beautiful monument."
        )
    }
]


for test in test_cases:

    print("\n" + "=" * 70)
    print("TEST:", test["name"])
    print("=" * 70)

    print("\nINPUT:")
    print(test["input"])

    claims = extract_claims(test["input"])

    final_claims = []

    for claim in claims:

        split_claims = split_compound_claim(claim)

        for split_claim in split_claims:

            cleaned_claim = clean_claim(split_claim)

            if cleaned_claim:
                final_claims.append(cleaned_claim)

    print("\nOUTPUT CLAIMS:")

    if final_claims:
        for i, claim in enumerate(final_claims, start=1):
            print(f"{i}. {claim}")
    else:
        print("No claims extracted.")