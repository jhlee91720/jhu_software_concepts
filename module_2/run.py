from urllib import robotparser, request, parse, error
from urllib.request import urlopen
import json
from bs4 import BeautifulSoup
import re

#Part A: Check robots.txt#######################################################

agent = "x"
url =  "https://www.thegradcafe.com/"

parser = robotparser.RobotFileParser(url)
parser.set_url(parse.urljoin(url, "robots.txt"))
parser.read()

path = [
    "/",
    "/cgi-bin/",
    "/admin/",
    "/survey/", # added path to survey page
    "survey/?program=Computer+Science"
]

# for p in path:
#     print(f"{parser.can_fetch(agent, p), p}")
    
################################################################################
#Part B: request data from GRADCAFE#############################################

survey_url = "https://www.thegradcafe.com/survey/"

try:
    req = request.Request(survey_url, headers={"User-Agent": "joohyun"})
    page = request.urlopen(req)

    html_bytes = page.read()
    html = html_bytes.decode("utf-8", errors="replace")


except error.HTTPError as err:
    if err.code == 400:
        print("Bad Request!")
    elif err.code == 404:
        print("Page not Found!")
    else:
        print(f"An HTTP error has occured: {err}")


with open("survey.html", "w", encoding="utf-8") as f:
    f.write(html)
################################################################################
#Part C: Use beautifulSoup to find admissions data #############################

soup = BeautifulSoup(html, "html.parser")

# Find all applicant entries
result_links = soup.find_all("a", href=True)

# Put the data into a list
entries = []
for link in result_links:
    href = link["href"]
    if href.startswith("/result/"):
        entries.append(link)


# Working with first entry -- scale it up later
first_entry = entries[0]
    
row = first_entry.find_parent("tr")                             # Store table row containing key info


cells = row.find_all("td")                                      # Store data in columns in the table row
university = cells[0].get_text(" ", strip=True)
print(university)
program = cells[1].get_text(" ", strip=True)
print(program)
date_added = cells[2].get_text(" ", strip=True)
print(date_added)
status = cells[3].get_text(" ", strip=True)
print(status)


detail_row = row.find_next_sibling("tr")                        # Get more extra details from the table row -- grab the second "tr"
if detail_row:
    detail_text = detail_row.get_text(" ", strip=True)
    print("detail_text:", detail_text)
else:
    print("No detail row found")


entry_url = "https://www.thegradcafe.com" + first_entry["href"] # Build the full entry URL
print(entry_url)


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
entry = {
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

print(entry)