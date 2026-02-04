import urllib.request
import urllib.parse
import urllib.error
import urllib.robotparser
import json
from bs4 import BeautifulSoup
import re


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


def parse_survey_page(html, limit=20):
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

        # Find the /result/ link in this row
        a = tr.find("a", href=True)
        if not a:
            continue

        href = a["href"].strip()
        if not href.startswith("/result/"):
            continue

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
        if len(records) >= limit:
            break

    return records


def parse_result_page(html):
    """
    Parse ONE result (/result/xxxxxx) page.
    We'll start by extracting the main text and pulling simple fields.
    (We'll refine once we see the exact page structure.)
    """
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text(" ", strip=True)

    # Very simple placeholder extraction using regex.
    # These may return "" if not found (that's okay for now).
    term = ""
    m = re.search(r"\b(Spring|Summer|Fall|Winter)\s+\d{4}\b", page_text)
    if m:
        term = m.group(0)

    degree = ""
    m = re.search(r"\b(Masters|PhD|MFA|MA|MS|MBA|JD|MD)\b", page_text)
    if m:
        degree = m.group(0)

    citizenship = ""
    m = re.search(r"\b(American|International)\b", page_text)
    if m:
        citizenship = m.group(0)

    gpa = ""
    m = re.search(r"\bGPA\s*[: ]\s*([0-4]\.\d{1,2})\b", page_text)
    if m:
        gpa = m.group(1)

    # Comments: this is tricky because the site structure can vary.
    # For now, grab a best-effort snippet by searching for common label words.
    comments = ""
    # If you find a better selector later, we'll replace this.
    # This just prevents empty forever.
    return {
        "term": term,
        "Degree": degree,
        "US/International": citizenship,
        "GPA": gpa,
        "comments_full": comments
    }


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
    scrape_one_page()