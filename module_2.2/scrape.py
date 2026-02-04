import urllib.request
import urllib.parse
import urllib.error
import urllib.robotparser
import json
from bs4 import BeautifulSoup
import re
import time

BASE_URL = "https://www.thegradcafe.com"
USER_AGENT = "Mozilla/5.0 (compatible; Module2Scraper/1.0)"


def check_robots(target_url):
    """
    Requirement A: confirm robots.txt permits scraping.
    Returns True/False.
    """
    robots_url = urllib.parse.urljoin(BASE_URL, "/robots.txt")
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()

    allowed = rp.can_fetch(USER_AGENT, target_url)
    print("robots.txt:", robots_url)
    print("target url:", target_url)
    print("allowed:", allowed)
    return allowed


def fetch_html(url):
    """
    Requirement B: use urllib to request data.
    """
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req) as resp:
            html_bytes = resp.read()
            return html_bytes.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        print("HTTPError:", e.code, url)
        return ""
    except Exception as e:
        print("Error:", str(e), url)
        return ""


def parse_survey_page(html, limit=None):
    """
    Parse one survey page and extract structured fields from table rows.
    Based on debug output: each row has 5 <td> cells:
      0 university, 1 program/degree text, 2 date, 3 decision/status, 4 comments/ui
    """
    soup = BeautifulSoup(html, "html.parser")

    records = []
    seen = set()

    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) != 5:
            continue

        # Find a /result/ link specifically inside this row (avoid other links)
        a = tr.find("a", href=lambda x: x and x.startswith("/result/"))
        if not a:
            continue

        href = a["href"].strip()
        full_url = urllib.parse.urljoin(BASE_URL, href)
        if full_url in seen:
            continue
        seen.add(full_url)

        university = tds[0].get_text(" ", strip=True)
        program_text = tds[1].get_text(" ", strip=True)
        date_added = tds[2].get_text(" ", strip=True)
        status = tds[3].get_text(" ", strip=True)

        # This cell contains UI words; keep a cleaned version for now
        comments_cell = tds[4].get_text(" ", strip=True)
        # remove common UI fragments
        for junk in ["Total comments", "Open options", "See More", "Report"]:
            comments_cell = comments_cell.replace(junk, "")
        comments = comments_cell.strip()

        record = {
            "program": program_text,          # matches professor tool input key name
            "university": university,         # useful even before LLM cleaning
            "date_added": date_added,
            "url": full_url,
            "status": status,
            "comments": comments
        }

        records.append(record)
        if limit is not None and len(records) >= limit:
            break

    return records


def parse_result_page(html):
    """
    Parse ONE /result/ page.

    We target the main content column:
    div.tw-w-full.lg:tw-w-3/4.lg:tw-pr-8

    Then we extract "Label Value" pairs from its text.
    """
    soup = BeautifulSoup(html, "html.parser")

    main_div = soup.find("div", class_="tw-w-full")
    # We'll be a bit safer by checking it contains the expected phrase
    if not main_div:
        return {
            "term": "",
            "Degree": "",
            "US/International": "",
            "GPA": "",
            "comments_full": ""
        }

    text = main_div.get_text(" ", strip=True)

    # Helper: pull the value that comes after a label word.
    def after_label(label, stop_labels):
        if label not in text:
            return ""
        start = text.find(label) + len(label)
        # cut off at the next label we recognize
        remainder = text[start:].strip()
        cut = len(remainder)
        for s in stop_labels:
            idx = remainder.find(s)
            if idx != -1 and idx < cut:
                cut = idx
        return remainder[:cut].strip()

    # These labels appeared in your candidate preview
    # We'll use a "stop list" to avoid grabbing too much.
    stop = [
        "Institution", "Program", "Degree Type", "Degree's",
        "GPA", "GRE", "Term", "Season", "Status", "Decision",
        "Application Information", "Details", "Acceptance Rate"
    ]

    institution = after_label("Institution", stop)
    program = after_label("Program", stop)
    degree_type = after_label("Degree Type", stop)

    # term: sometimes present as "Term" or "Season"
    term = after_label("Term", stop)
    if not term:
        term = after_label("Season", stop)

    # citizenship sometimes appears as "American" or "International"
    citizenship = ""
    if "International" in text:
        citizenship = "International"
    elif "American" in text:
        citizenship = "American"

    # GPA: look for "GPA" then a number nearby
    gpa = ""
    m = re.search(r"\bGPA\b[^0-9]*([0-4]\.\d{1,2})", text)
    if m:
        gpa = m.group(1)

    # Comments: sometimes not present at all
    comments_full = ""
    # If the word "Comments" exists, we can attempt to pull text after it
    if "Comments" in text:
        comments_full = after_label("Comments", stop)

    return {
        "term": term,
        "Degree": degree_type if degree_type else "",
        "US/International": citizenship,
        "GPA": gpa,
        "comments_full": comments_full,
        # extra helpful fields you can merge back into your record later:
        "institution_detail": institution,
        "program_detail": program
    }

def enrich_with_detail(records, max_records=5, delay_seconds=1.0):
    """
    For each record (from survey page), fetch its /result/ page and merge extra fields.
    Start with a small max_records for testing.
    """
    enriched = []

    for i, rec in enumerate(records[:max_records]):
        url = rec.get("url", "")
        print(f"DETAIL {i+1}/{max_records}:", url)

        # Respect robots for each detail URL (conservative)
        if not check_robots(url):
            print("  Skipped (robots disallow):", url)
            enriched.append(rec)
            continue

        html = fetch_html(url)
        if not html:
            print("  Skipped (no html):", url)
            enriched.append(rec)
            continue

        detail = parse_result_page(html)

        # Merge: keep original fields + add detail fields
        merged = dict(rec)
        merged.update(detail)

        enriched.append(merged)

        # Polite delay so we don't hammer the site
        time.sleep(delay_seconds)

    return enriched


def debug_result_page_structure(html):
    soup = BeautifulSoup(html, "html.parser")

    # Print the <title> so we know we're on the right page
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    print("RESULT PAGE TITLE:", title)

    # Print the first few <h1>/<h2> headings (often near the main content)
    headings = soup.find_all(["h1", "h2"])
    for i, h in enumerate(headings[:5]):
        print("HEADING", i, ":", h.get_text(" ", strip=True))

    # Print candidate main containers by id/class
    candidates = soup.find_all(["main", "article", "section", "div"])
    printed = 0
    for tag in candidates:
        attrs = []
        if tag.get("id"):
            attrs.append(f"id={tag.get('id')}")
        if tag.get("class"):
            attrs.append("class=" + " ".join(tag.get("class")))

        # Only show ones that have a lot of text (likely real content)
        text = tag.get_text(" ", strip=True)
        if len(text) < 300:
            continue

        print("CANDIDATE:", tag.name, " ".join(attrs))
        print("TEXT PREVIEW:", text[:250])
        print("---")
        printed += 1
        if printed >= 5:
            break
        
    
def debug_print_first_row_cells(html):
    soup = BeautifulSoup(html, "html.parser")

    # Find the first table row that actually has <td> cells
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) == 0:
            continue

        print("FOUND A ROW WITH", len(tds), "CELLS")
        for i, td in enumerate(tds):
            text = td.get_text(" ", strip=True)
            print("CELL", i, ":", text)
        break


def load_data(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        print("load_data error:", str(e))
        return []


def save_data(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def scrape_many_pages(target_records=500, start_page=1, max_pages=10, checkpoint_every_pages=2):

    """
    Scrape multiple survey pages, dedupe by URL, and save progress to applicant_data.json.
    Start small (e.g., 3 pages / 100 records) before scaling to 30,000.
    """
    output_path = "module_2.2/applicant_data.json"

    # Load existing data so you can resume
    existing = load_data(output_path)
    by_url = {rec["url"]: rec for rec in existing if "url" in rec}

    print("Loaded existing records:", len(by_url))

    for page in range(start_page, max_pages + 1):
        page_url = urllib.parse.urljoin(BASE_URL, f"/survey/?page={page}")
        print("\nSCRAPING PAGE:", page, page_url)

        if not check_robots(page_url):
            print("Robots disallows:", page_url)
            break

        html = fetch_html(page_url)
        if not html:
            print("No HTML for page:", page)
            continue

        new_records = parse_survey_page(html, limit=None)  # get all rows on that page
        print("Parsed records from page:", len(new_records))
        added = 0
        
        for rec in new_records:
            u = rec.get("url", "")
            if not u:
                continue
            if u in by_url:
                continue
            by_url[u] = rec
            added += 1

        print("Added from this page:", added)
        print("Total unique records:", len(by_url))

        # checkpoint save
        if page % checkpoint_every_pages == 0:
            save_data(output_path, list(by_url.values()))
            print("Checkpoint saved:", output_path)

        if len(by_url) >= target_records:
            print("Reached target_records:", target_records)
            break

    # final save
    save_data(output_path, list(by_url.values()))
    print("Final saved:", output_path, "records:", len(by_url))

   
def scrape_one_page():
    """
    First test: download ONE survey page and save html locally.
    """
    survey_url = urllib.parse.urljoin(BASE_URL, "/survey/")

    if not check_robots(survey_url):
        print("Robots.txt does not allow scraping this URL. Stopping.")
        return

    html = fetch_html(survey_url)
    if not html:
        print("No HTML downloaded.")
        return
    
    debug_print_first_row_cells(html)

    # Save raw html so you can inspect it and debug parsing.
    with open("module_2.2/survey_page_1.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Saved:", "module_2.2/survey_page_1.html")
    
     # Parse a small sample of rows and save as JSON
    sample = parse_survey_page(html, limit=20)
    with open("module_2.2/sample_applicant_data.json", "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)

    print("Saved:", "module_2.2/sample_applicant_data.json", "records:", len(sample))
    
        # Enrich a small subset with detail-page fields (start with 5)
    enriched = enrich_with_detail(sample, max_records=20, delay_seconds=1.0)
    with open("module_2.2/sample_applicant_data_with_detail_20.json", "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print("Saved:", "module_2.2/sample_applicant_data_with_detail_20.json", "records:", len(enriched))



    # --- Detail-page test: fetch and parse ONE result page ---
    if len(sample) > 0:
        test_url = sample[0]["url"]
        if check_robots(test_url):
            detail_html = fetch_html(test_url)
            
            with open("module_2.2/result_test.html", "w", encoding="utf-8") as f:
                f.write(detail_html)
            print("Saved:", "module_2.2/result_test.html")
            debug_result_page_structure(detail_html)
            
            soup = BeautifulSoup(detail_html, "html.parser")
            text_preview = soup.get_text(" ", strip=True)
            print("DETAIL TEXT PREVIEW:", text_preview[:400])
            
            detail_fields = parse_result_page(detail_html)
            print("DETAIL TEST URL:", test_url)
            print("DETAIL FIELDS:", detail_fields)
        else:
            print("Robots.txt does not allow fetching result page:", test_url)

if __name__ == "__main__":
    scrape_many_pages(target_records=999999, start_page=15, max_pages=15, checkpoint_every_pages=1)

