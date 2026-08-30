import re


def clean_text(text: str) -> str:
    """
    Utility helper function to sanitize and normalize text inputs.
    """
    if not text:
        return ""
    # Normalize extra whitespaces
    return re.sub(r"\s+", " ", text.strip())
