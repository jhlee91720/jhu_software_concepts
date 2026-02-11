import json
import os


def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    src = "module_2/cleaned_applicant_data.json"
    out_dir = "module_2/llm_chunks"
    os.makedirs(out_dir, exist_ok=True)

    rows = load_data(src)
    n = len(rows)
    k = 5
    chunk_size = (n + k - 1) // k  # ceiling

    for i in range(k):
        chunk = rows[i * chunk_size : (i + 1) * chunk_size]
        out_path = os.path.join(out_dir, f"chunk_{i:02d}.json")
        save_data(out_path, chunk)
        print("Wrote:", out_path, "records:", len(chunk))
