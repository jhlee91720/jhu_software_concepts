from urllib import request, error
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

#Part B: request data from GRADCAFE#############################################
if __name__ == "__main__":
    base_url = "https://www.thegradcafe.com/survey/"
    page_num = 1
    survey_url = f"{base_url}?page={page_num}"
    print("fetching:", survey_url)

    try:
        req = request.Request(survey_url, headers={"User-Agent": "joohyun"})
        page = request.urlopen(req)

        html_bytes = page.read()
        html = html_bytes.decode("utf-8", errors="replace")
        
        with open("module_2/survey.html", "w", encoding="utf-8") as f:
            f.write(html)


    except error.HTTPError as err:
        if err.code == 400:
            print("Bad Request!")
        elif err.code == 404:
            print("Page not Found!")
        else:
            print(f"An HTTP error has occured: {err}")


################################################################################
#Part C: Use beautifulSoup to find admissions data #############################

def parse_one_page(html): 
    soup = BeautifulSoup(html, "html.parser")

    # Find all applicant entries
    result_links = soup.find_all("a", href=True)

    # Put the data into a list
    entries = []
    for link in result_links:
        href = link["href"]
        if href.startswith("/result/"):
            entries.append(link)

    # Scale up to entries in a page
    all_entries = []
    for entry in entries: 
        # Working with first entry -- scale it up later
        # entry = entries[0]
        row = entry.find_parent("tr")                                   # Store table row containing key info
        if row is None:
            continue
        
        cells = row.find_all("td")                                      # Store data in columns in the table row
        if len(cells) <4:
            continue
        
        university = cells[0].get_text(" ", strip=True)
        program = cells[1].get_text(" ", strip=True)
        date_added = cells[2].get_text(" ", strip=True)
        status = cells[3].get_text(" ", strip=True)


        detail_text = ""                                                # Get more extra details from the table row -- grab the second "tr"
        detail_row = row.find_next_sibling("tr")
        if detail_row:
            detail_text = detail_row.get_text(" ", strip=True)

        entry_url = "https://www.thegradcafe.com" + entry["href"]

        us_international = None                                         # sort out info in detail_text (US-international)
        if "International" in detail_text:
            us_international = "International"
        elif "American" in detail_text:
            us_international = "American"


        term_year = None                                                # sort out info in detail_text (term year)
        m = re.search(r"(Fall|Spring|Summer)\s+\d{4}", detail_text)
        if m:
            term_year = m.group(0)
            
            
        gpa = None                                                      # sort out info in detail_text (GPA)
        m_gpa = re.search(r"GPA\s*([0-9]+(?:\.[0-9]+)?)", detail_text)
        if m_gpa:
            gpa = m_gpa.group(1)


        gre = None                                                      # sort out info in detail_text (GRE)
        m_gre = re.search(r"GRE\s*([0-9]+)", detail_text)
        if m_gre:
            gre = m_gre.group(1)
            

        # Create a dict for an entry
        dict_entry = {
            "university": university,
            "program": program,
            "date_added": date_added,
            "status": status,
            "entry_url": entry_url,
            "term": term_year,
            "applicant_type": us_international,
            "gpa": gpa,
            "gre": gre
        }
        all_entries.append(dict_entry)
    return all_entries