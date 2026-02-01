import json
import re


def _clean_text(s: str) -> str:
    if s is None:
        return ""
    return " ".join(s.replace("\n", " ").replace("\t", " ").split()).strip()


def _none_if_empty(s: str):
    s2 = _clean_text(s)
    return None if s2 == "" else s2


def _extract_scores_and_flags(comment: str) -> dict:
    """
    Extract optional fields from messy comments using regex.
    Keeps it conservative: if not found, return None.
    """
    c = _clean_text(comment)

    # GPA patterns (examples: "GPA 3.8", "GPA: 3.72/4.0")
    gpa = None
    m = re.search(r"\bGPA\b\s*[:=]?\s*([0-4](?:\.\d{1,3})?)", c, re.IGNORECASE)
    if m:
        gpa = m.group(1)

    # GRE total (examples: "GRE 320", "GRE: 327")
    gre_total = None
    m = re.search(r"\bGRE\b\s*[:=]?\s*(\d{3})\b", c, re.IGNORECASE)
    if m:
        gre_total = m.group(1)

    # GRE Verbal (examples: "V 160", "Verbal: 158", "GRE V: 162")
    gre_v = None
    m = re.search(r"\b(?:GRE\s*)?(?:V|Verbal)\b\s*[:=]?\s*(\d{2,3})\b", c, re.IGNORECASE)
    if m:
        gre_v = m.group(1)

    # GRE Quant (examples: "Q 167", "Quant: 165")
    gre_q = None
    m = re.search(r"\b(?:GRE\s*)?(?:Q|Quant|Quantitative)\b\s*[:=]?\s*(\d{2,3})\b", c, re.IGNORECASE)
    if m:
        gre_q = m.group(1)

    # GRE AW (examples: "AW 4.5", "AWA: 3.0", "Writing 4.0")
    gre_aw = None
    m = re.search(r"\b(?:AW|AWA|Writing)\b\s*[:=]?\s*([0-6](?:\.\d)?)\b", c, re.IGNORECASE)
    if m:
        gre_aw = m.group(1)

    # International/American (very heuristic)
    intl = None
    if re.search(r"\binternational\b", c, re.IGNORECASE):
        intl = "International"
    elif re.search(r"\bamerican\b|\bus citizen\b|\bdomestic\b", c, re.IGNORECASE):
        intl = "American"

    # Semester/year start (examples: "Fall 2025", "Spring 2026")
    semester_start = None
    m = re.search(r"\b(Fall|Spring|Summer|Winter)\s+(20\d{2})\b", c, re.IGNORECASE)
    if m:
        semester_start = f"{m.group(1).title()} {m.group(2)}"

    # Masters/PhD (heuristic)
    degree = None
    if re.search(r"\bphd\b|\bph\.d\b|\bdoctor", c, re.IGNORECASE):
        degree = "PhD"
    elif re.search(r"\bmasters\b|\bm\.s\b|\bms\b|\bma\b|\bmeng\b", c, re.IGNORECASE):
        degree = "Masters"

    return {
        "gpa": gpa,
        "gre_score": gre_total,
        "gre_v_score": gre_v,
        "gre_q_score": gre_q,
        "gre_aw": gre_aw,
        "international_or_american": intl,
        "semester_and_year_start": semester_start,
        "masters_or_phd": degree,
    }


def clean_data(raw_entries: list) -> list:
    cleaned = []

    for e in raw_entries:
        # Pull expected fields (and sanitize)
        program = _none_if_empty(e.get("program_name", ""))
        university = _none_if_empty(e.get("university", ""))
        status = _none_if_empty(e.get("applicant_status", ""))
        decision_date = _none_if_empty(e.get("decision_date", ""))
        date_added = _none_if_empty(e.get("date_added", ""))
        entry_url = _none_if_empty(e.get("entry_url", ""))
        comments = _none_if_empty(e.get("comments", ""))

        # Extract optional fields from comments
        extracted = _extract_scores_and_flags(comments or "")

        cleaned_entry = {
            "program_name": program,
            "university": university,
            "comments": comments,
            "date_added_to_gradcafe": date_added,
            "url_link_to_applicant_entry": entry_url,
            "applicant_status": status,
            # If your professor expects separate accept/reject dates, we store decision_date
            # and keep it as None when missing.
            "acceptance_or_rejection_date": decision_date,
            "semester_and_year_of_program_start": extracted["semester_and_year_start"],
            "international_or_american_student": extracted["international_or_american"],
            "gre_score": extracted["gre_score"],
            "gre_v_score": extracted["gre_v_score"],
            "gre_aw": extracted["gre_aw"],
            "gpa": extracted["gpa"],
            "masters_or_phd": extracted["masters_or_phd"],
        }

        cleaned.append(cleaned_entry)

    return cleaned


def save_data(data: list, out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[save] wrote {len(data)} entries to {out_path}")


def load_data(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    raw = load_data("applicant_data.json")
    cleaned = clean_data(raw)
    save_data(cleaned, "llm_extend_applicant_data.json")


if __name__ == "__main__":
    main()