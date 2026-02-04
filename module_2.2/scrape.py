import urllib.request
import urllib.parse
import urllib.error
import urllib.robotparser
import json
from bs4 import BeautifulSoup


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


if __name__ == "__main__":
    scrape_one_page()