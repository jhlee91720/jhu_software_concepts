import json
import re


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def strip_html(text):
    """Remove any HTML tags if they exist (safety)."""
    text = text or ""
    return re.sub(r"<[^>]+>", "", text).strip()


def clean_value(v):
    if v is None:
        return ""
    return strip_html(str(v)).strip()


def parse_status_dates(status_text):
    """
    Examples:
      'Accepted on 1 Mar' -> acceptance_date='1 Mar'
      'Rejected on 3 Feb' -> rejection_date='3 Feb'
    """
    status_text = clean_value(status_text)

    acceptance_date = ""
    rejection_date = ""

    m_acc = re.search(r"\bAccepted on\s+(.+)$", status_text, re.IGNORECASE)
    if m_acc:
        acceptance_date = m_acc.group(1).strip()

    m_rej = re.search(r"\bRejected on\s+(.+)$", status_text, re.IGNORECASE)
    if m_rej:
        rejection_date = m_rej.group(1).strip()

    return status_text, acceptance_date, rejection_date


def finalize_rows(rows):
    out = []
    for r in rows:
        status_clean, acc_date, rej_date = parse_status_dates(r.get("status", ""))

        obj = {
            "program": clean_value(r.get("llm-generated-program", r.get("program", ""))),
            "university": clean_value(r.get("llm-generated-university", r.get("university", ""))),
            "comments": clean_value(r.get("comments", "")),
            "date_added": clean_value(r.get("date_added", "")),
            "url": clean_value(r.get("url", "")),
            "status": status_clean,
            "acceptance_date": acc_date,
            "rejection_date": rej_date,
            "term": clean_value(r.get("term", "")),
            "US/International": clean_value(r.get("US/International", "")),
            "Degree": clean_value(r.get("Degree", "")),
            "GPA": clean_value(r.get("GPA", "")),
        }
        out.append(obj)
    return out


if __name__ == "__main__":
    src = "module_2.2/llm_cleaned_applicant_data.json"
    dst = "module_2.2/final_applicant_data.json"

    rows = load_json(src)
    final_rows = finalize_rows(rows)
    save_json(dst, final_rows)

    print("Saved:", dst, "records:", len(final_rows))

