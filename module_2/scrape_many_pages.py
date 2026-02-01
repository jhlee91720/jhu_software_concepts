from urllib import request, error
import json

from scrape_one_page import parse_one_page


def fetch_html(url):
    headers = {"User-Agent": "joohyun"}
    req = request.Request(url, headers=headers)

    page = request.urlopen(req, timeout = 10)
    
    html_bytes = page.read()
    html = html_bytes.decode("utf-8", errors="replace")
    return html


def main():
    base_url = "https://www.thegradcafe.com/survey/"
    page_num = 1
    master_entries = []

    while len(master_entries) < 30000:
        survey_url = f"{base_url}?page={page_num}"
        print("fetching:", survey_url)

        html = fetch_html(survey_url)
        
        page_entries = parse_one_page(html)
        master_entries.extend(page_entries)
        page_num += 1
        
    print("final total collected:", len(master_entries))
    print("sample entry:", master_entries[0])


if __name__ == "__main__":
    main()
