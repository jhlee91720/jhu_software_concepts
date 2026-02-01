import json
import re


def load_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_canon_list(filename):
    canon = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s == "":
                continue
            if s.startswith("#"):
                continue
            canon.append(s)
    return canon


def normalize_text(s):
    """
    Normalize spacing/case.
    Only uses string methods + regex.
    """
    if s is None:
        return ""

    s = str(s)
    s = s.replace("\xa0", " ")
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s


def canon_key(s):
    """
    Key used for matching canon values.
    Lowercase + remove non-alphanumeric.
    """
    s = normalize_text(s).lower()
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def match_canon(value, canon_list):
    """
    Exact match to canonical list AFTER normalization.
    No fuzzy matching (no difflib allowed).
    If not found, return normalized value as fallback.
    """
    value = normalize_text(value)
    if value == "":
        return ""

    value_k = canon_key(value)

    for c in canon_list:
        if canon_key(c) == value_k:
            return c

    return value


def clean_data(rows, canon_programs, canon_universities):
    """
    Part E:
    - Use LLM output fields if present
    - Create clean_program / clean_university fields
    - Ensure consistent formatting / no strange whitespace
    """
    cleaned = []

    for r in rows:
        # Use LLM output when available
        llm_prog = normalize_text(r.get("llm-generated-program", ""))
        llm_uni = normalize_text(r.get("llm-generated-university", ""))

        # Fall back to original fields if LLM empty
        raw_prog = normalize_text(r.get("program", ""))
        raw_uni = normalize_text(r.get("university", ""))

        chosen_prog = llm_prog if llm_prog != "" else raw_prog
        chosen_uni = llm_uni if llm_uni != "" else raw_uni

        clean_prog = match_canon(chosen_prog, canon_programs)
        clean_uni = match_canon(chosen_uni, canon_universities)

        out = dict(r)  # copy original row

        # overwrite / ensure fields are normalized
        out["program"] = raw_prog
        out["university"] = raw_uni

        # keep llm fields normalized
        out["llm-generated-program"] = llm_prog
        out["llm-generated-university"] = llm_uni

        # add cleaned final fields
        out["clean_program"] = clean_prog
        out["clean_university"] = clean_uni

        cleaned.append(out)

    return cleaned


def main():
    # IMPORTANT: run clean.py from repo root, like:
    # python module_2/clean.py

    in_file = "module_2/out_10.json"
    out_file = "module_2/llm_extend_applicant_data_10.json"

    canon_programs_file = "module_2/llm_hosting/canon_programs.txt"
    canon_universities_file = "module_2/llm_hosting/canon_universities.txt"

    rows = load_json(in_file)
    canon_programs = load_canon_list(canon_programs_file)
    canon_universities = load_canon_list(canon_universities_file)

    cleaned = clean_data(rows, canon_programs, canon_universities)

    save_json(cleaned, out_file)

    print("Input rows:", len(rows))
    print("Output rows:", len(cleaned))
    print("Wrote:", out_file)
    print("Example keys:", list(cleaned[0].keys()))


if __name__ == "__main__":
    main()