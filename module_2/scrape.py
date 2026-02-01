from urllib import parse
from urllib.request import urlopen, Request


def scrape_data():
    base_url = "https://www.thegradcafe.com/"
    survey_url = parse.urljoin(base_url, "survey/")

    # Optional but helpful: a basic User-Agent header
    req = Request(
        survey_url,
        headers={"User-Agent": "Joo Hyun"}
    )

    page = urlopen(req)
    html = page.read().decode("utf-8", errors="replace")

    print("Fetched URL:", survey_url)
    print("HTML length:", len(html))

    return html


def save_data(html, filename="raw_survey_page.html"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print("Saved HTML to:", filename)


def load_data(filename="raw_survey_page.html"):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def main():
    html = scrape_data()
    save_data(html)


if __name__ == "__main__":
    main()