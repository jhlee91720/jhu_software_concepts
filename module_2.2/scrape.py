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
    Requirement C (first pass): parse one survey page and extract result links.
    We'll start simple: collect the /result/ links and row text.
    """
    soup = BeautifulSoup(html, "html.parser")

    records = []
    seen = set()

    # Find all <a> tags with an href, and keep only /result/ links
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()

        if not href.startswith("/result/"):
            continue

        full_url = urllib.parse.urljoin(BASE_URL, href)

        # Deduplicate
        if full_url in seen:
            continue
        seen.add(full_url)

        # Try to capture full row text (usually in the <tr>)
        tr = a.find_parent("tr")
        if tr:
            row_text = tr.get_text(" ", strip=True)
        else:
            row_text = a.get_text(" ", strip=True)

        record = {
            "program": row_text,   # raw combined text for now
            "url": full_url
        }
        records.append(record)

        if len(records) >= limit:
            break

    return records


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