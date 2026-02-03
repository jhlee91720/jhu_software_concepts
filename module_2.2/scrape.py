import urllib.request
import urllib.parse
import urllib.error
import urllib.robotparser


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


if __name__ == "__main__":
    scrape_one_page()