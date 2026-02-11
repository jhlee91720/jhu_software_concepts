import json


def jsonl_to_list(jsonl_path):
    rows = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    src = "module_2/out_all.jsonl"
    dst = "module_2/llm_cleaned_applicant_data.json"

    rows = jsonl_to_list(src)
    save_json(dst, rows)

    print("Saved:", dst, "records:", len(rows))
