1) Name
--------------------------------
Name: Joo Hyun Lee
JHED ID: jlee887


2) Module Info
--------------------------------
Module: Module 2
Assignment: GradCafe Web Scraper + Data Cleaning with LLM


3) Approach
--------------------------------
Part A: robots.txt Check
- I checked GradCafe robots.txt before scraping to confirm scraping was permitted.
- robots.txt URL checked:
  https://www.thegradcafe.com/robots.txt
- Script used:
  module_2/robot_check.py
- Screenshot evidence:
  module_2/robot_check.png

Part B/C: Web Scraping + Parsing (GradCafe Survey Pages)
- I used urllib (urllib.request) to request HTML pages from GradCafe.
- I scraped multiple pages by looping through the survey pages (?page=1, ?page=2, ...).
- I parsed each page using BeautifulSoup and string processing to extract applicant data.
- The data is stored in a Python list of dictionaries and saved as JSON.
- Output file:
  module_2/applicant_data.json
- The file contains at least 30,000 applicant entries.

Part E: Structured JSON Output
- The dataset is saved as a JSON list of dictionaries (clean formatted JSON).
- Each dictionary contains keys such as program/university/status/date_added/url/term and other available fields.
- Missing values are represented consistently (None).

Part D: LLM Cleaning / Standardization
- I used the provided local LLM standardizer under:
  module_2/llm_hosting/app.py
- This script adds two standardized fields:
  llm-generated-program
  llm-generated-university
- Running the local model over all 30,000 entries takes a long time on my computer.
  To demonstrate correct LLM cleaning, I ran the standardizer on a representative sample of 300 entries.
- Files:
  Sample input: module_2/cleaned_applicant_data.json  (300 entries)
  Cleaned output: module_2/llm_extend_applicant_data.json  (300 entries with LLM-generated fields)


4) Known Bugs / Limitations
--------------------------------
- LLM cleaning was run on a 300-entry sample due to long runtime when standardizing the full 30,000-entry dataset locally.
- Some GradCafe pages may contain duplicate or inconsistent entries; duplicates can appear in the dataset.