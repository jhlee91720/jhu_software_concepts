import json


def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_data(rows):
    cleaned = []
    for r in rows:
        program = (r.get("program") or "").strip()
        university = (r.get("university") or "").strip()

        # LLM expects "program" text that may include both parts
        combined_program = program
        if university:
            combined_program = f"{program}, {university}".strip(", ").strip()

        out = {
            "program": combined_program,
            "university": university,
            "comments": (r.get("comments") or "").strip(),
            "date_added": (r.get("date_added") or "").strip(),
            "url": (r.get("url") or "").strip(),
            "status": (r.get("status") or "").strip(),
            "term": (r.get("term") or "").strip(),
            "US/International": (r.get("US/International") or "").strip(),
            "Degree": (r.get("Degree") or "").strip(),
            "GPA": (r.get("GPA") or "").strip(),
        }
        cleaned.append(out)
    return cleaned


def save_data(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    src = "module_2.2/applicant_data.json"
    dst = "module_2.2/cleaned_applicant_data.json"

    rows = load_data(src)
    cleaned = clean_data(rows)
    save_data(dst, cleaned)

    print("Saved:", dst, "records:", len(cleaned))
