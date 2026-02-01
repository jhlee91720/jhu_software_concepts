from urllib import request, error
import json

from scrape_one_page import parse_one_page


def fetch_html(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    req = request.Request(url, headers=headers)

    try:
        page = request.urlopen(req, timeout=10)
        html_bytes = page.read()
        html = html_bytes.decode("utf-8", errors="replace")
        return html
    except error.HTTPError as err:
        print("HTTPError:", err.code, url)
        return ""
    except Exception as err:
        print("Error:", err, url)
        return ""


def _count_jsonl(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return 0


def _append_jsonl(entries, filename):
    # Append each entry as one JSON object per line
    with open(filename, "a", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


def _jsonl_to_json(jsonl_file, json_file):
    data = []
    with open(jsonl_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))

    with open(json_file, "w", encoding="utf-8") as out:
        json.dump(data, out, ensure_ascii=False)

    print("Saved final JSON:", json_file)
    print("Total entries:", len(data))


def main():
    base_url = "https://www.thegradcafe.com/survey/"
    target_count = 30000

    jsonl_file = "module_2/applicant_data.jsonl"
    json_file = "module_2/applicant_data.json"

    # Resume support
    already = _count_jsonl(jsonl_file)
    print("Already saved (resume):", already)

    total_saved = already
    page_num = 1

    # Optional: avoid duplicates if you re-run and pages overlap
    seen_urls = set()

    # If resuming, rebuild seen_urls from existing jsonl (lightweight pass)
    if already > 0:
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    u = obj.get("entry_url")
                    if u:
                        seen_urls.add(u)
                except Exception:
                    pass

    while total_saved < target_count:
        survey_url = f"{base_url}?page={page_num}"
        print("fetching:", survey_url, "| saved:", total_saved)

        html = fetch_html(survey_url)
        if html == "":
            print("No HTML returned. Stopping to avoid repeated failures.")
            break

        page_entries = parse_one_page(html)

        # Safety stop: if no entries, stop (prevents infinite loops)
        if len(page_entries) == 0:
            print("No entries found on this page. Stopping.")
            break

        # De-dupe + only write what we need
        to_write = []
        for e in page_entries:
            u = e.get("entry_url")
            if u and u in seen_urls:
                continue
            if total_saved >= target_count:
                break
            to_write.append(e)
            if u:
                seen_urls.add(u)
            total_saved += 1

        _append_jsonl(to_write, jsonl_file)

        # checkpoint message every 1000
        if total_saved % 1000 == 0:
            print("checkpoint:", total_saved)

        page_num += 1

    # Convert to required JSON file
    _jsonl_to_json(jsonl_file, json_file)


if __name__ == "__main__":
    main()