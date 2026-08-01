"""
Verification Service

This module contains the core business logic
for TrustGate-AI verification.
"""


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

    return {
        "success": True,
        "question": question,
        "response": response
    }