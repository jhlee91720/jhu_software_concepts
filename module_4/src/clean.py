"""Utility functions for cleaning and normalizing GradCafe fields."""


def clean_text(value):
    """Convert input to text and remove NUL bytes unsupported by Postgres TEXT."""
    if value is None:
        return None
    return str(value).replace("\x00", "").strip()


def to_float(value):
    """Best-effort conversion of noisy numeric strings to float."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    filtered = ""
    for ch in text:
        if ch.isdigit() or ch == ".":
            filtered += ch

    if not filtered:
        return None

    try:
        return float(filtered)
    except ValueError:
        return None


def normalize_text(value):
    """Normalize text for robust matching across punctuation/casing variants."""
    if not value:
        return ""

    text = str(value).lower()
    for ch in [",", ".", "-", "_", "/", "(", ")", ":", ";", "'", '"']:
        text = text.replace(ch, " ")
    return " ".join(text.split())
