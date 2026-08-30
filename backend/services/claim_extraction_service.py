"""
Claim Extraction Service

This module is responsible for extracting
factual claims from AI-generated responses.
"""

import spacy

nlp = spacy.load("en_core_web_sm")


def is_question(sentence):
    """
    Check whether a sentence is a question.

    Parameters:
        sentence (str): Sentence text.

    Returns:
        bool: True if the sentence is a question.
    """

    return sentence.strip().endswith("?")

def is_opinion(sentence):
    """
    Detect obvious subjective/opinion-based sentences.

    Parameters:
        sentence (str): Sentence text.

    Returns:
        bool: True if the sentence contains obvious opinion markers.
    """

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

    sentence_lower = sentence.lower()

    return any(marker in sentence_lower for marker in opinion_markers)

def inspect_dependencies(sentence):
    """
    Display dependency information for each token in a sentence.
    """

    doc = nlp(sentence)

    print("\nDependency Analysis:")
    print("-" * 60)

    for token in doc:
        print(
            f"Word: {token.text:<15} "
            f"POS: {token.pos_:<10} "
            f"Dependency: {token.dep_:<10} "
            f"Head: {token.head.text}"
        )

def extract_claims(response):
    """
    Extract candidate factual claims from an AI-generated response.

    Parameters:
        response (str): AI-generated response.

    Returns:
        list: Extracted candidate factual claims.
    """

    doc = nlp(response)

    claims = []
    seen_claims = set()

    for sentence in doc.sents:

        sentence_text = sentence.text.strip()

        if is_question(sentence_text):
            continue

        # First split the sentence into smaller candidate claims
        split_claims = split_compound_claim(sentence_text)

        for claim in split_claims:

            cleaned_claim = clean_claim(claim)

            if cleaned_claim is None:
                continue

            # Check opinion AFTER splitting
            if is_opinion(cleaned_claim):
                continue

            claim_key = cleaned_claim.lower().rstrip(".")

            if claim_key not in seen_claims:
                claims.append(cleaned_claim)
                seen_claims.add(claim_key)

    return claims

import re

def split_compound_claim(text):
    """
    Split compound sentences into individual candidate claims.

    Handles:
    - independent clauses
    - shared-subject clauses
    - simple pronoun continuation
    """

    doc = nlp(text)

    # Find the main subject of the root verb
    main_subject = None

    for token in doc:
        if (
            token.dep_ in {"nsubj", "nsubjpass"}
            and token.head.dep_ == "ROOT"
        ):
            main_subject = token.text
            break

    # Find coordinated verbs
    coordinated_verbs = [
        token
        for token in doc
        if token.dep_ == "conj"
        and token.pos_ in {"VERB", "AUX"}
    ]

    # No compound verb found
    if not coordinated_verbs:
        return [text.strip()]

    claims = []

    # First coordinated verb
    first_conj_verb = coordinated_verbs[0]

    # Everything before the conjunction leading to that verb
    first_clause_tokens = []

    for token in doc:
        if token.i >= first_conj_verb.i:
            break

        if token.dep_ == "cc":
            continue

        # Remove explicit pronoun that belongs to second clause
        if (
            token.pos_ == "PRON"
            and token.dep_ in {"nsubj", "nsubjpass"}
        ):
            continue

        first_clause_tokens.append(token.text)

    first_clause = " ".join(first_clause_tokens).strip()

    # Remove trailing conjunction safely
    for conjunction in [" and", " but", " while", " whereas"]:
        if first_clause.lower().endswith(conjunction):
            first_clause = first_clause[:-len(conjunction)].strip()

    if first_clause:
        claims.append(first_clause)

    # Process coordinated clauses
    for verb in coordinated_verbs:

        explicit_subject = None

        for child in verb.children:
            if child.dep_ in {"nsubj", "nsubjpass"}:
                explicit_subject = child
                break

        # Determine subject
        if explicit_subject is None:
            subject = main_subject

        elif explicit_subject.text.lower() in {"it", "they"}:
            subject = main_subject

        else:
            subject = explicit_subject.text

        # Build predicate starting from the coordinated verb
        predicate_tokens = []

        for token in doc:
            if token.i < verb.i:
                continue

            # Stop if another coordinated verb starts
            if (
                token.i > verb.i
                and token.dep_ == "conj"
                and token.pos_ in {"VERB", "AUX"}
            ):
                break

            if token.dep_ == "punct":
                continue

            if (
                token.dep_ in {"nsubj", "nsubjpass"}
                and token.text.lower() in {"it", "they", "he", "she"}
            ):
                continue

            predicate_tokens.append(token.text)

        predicate = " ".join(predicate_tokens).strip()

        if subject and predicate:
            claims.append(f"{subject} {predicate}")

    return claims

def clean_claim(claim):
    """
    Clean an extracted claim before further processing.
    """

    claim = claim.strip()

    # Remove unnecessary spaces
    claim = " ".join(claim.split())
    if not claim:
        return None
    
    return claim

if __name__ == "__main__":
    test_response = (
        "Who is the Prime Minister of India? "
        "Mumbai is the capital of Maharashtra. "
        "MUMBAI IS THE CAPITAL OF MAHARASHTRA. "
        "India has a large population and China has a large population. "
        "India has a large population and China has a large population. "
        "I think Mumbai is a beautiful city."
    )

    claims = extract_claims(test_response)

    final_claims = []

    for claim in claims:
        split_claims = split_compound_claim(claim)

        for split_claim in split_claims:
            cleaned_split_claim = clean_claim(split_claim)

            if cleaned_split_claim is not None:
                final_claims.append(cleaned_split_claim)

    print("\nFinal Claims:")
    for claim in final_claims:
        print("-", claim)