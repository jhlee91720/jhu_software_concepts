1. Name:
    Joo Hyun Lee (jlee887)
  
2. Module Info:
    Module 2: Web Scraping, URL Management, and LLM Data Cleaning

3. Approach:
    A. Robots.txt compliance
        - sed urllib.robotparser.RobotFileParser to fetch and parse https://www.thegradcafe.com/robots.txt.
        - Verified can_fetch() before scraping survey/result pages.
        - Evidence screenshot included: screenshot.png (or your exact filename).
    B. Scraping (urllib + BeautifulSoup/regext/string methodds)
        - Used urllib.request.Request / urllib.request.urlopen to download GradCafe survey pages with a User-Agent header.
        - Used urllib.parse.urljoin for URL construction.
        - Parsed survey pages with BeautifulSoup and string/regex parsing to extract fields.
        - Stored raw scraped output as JSON: module_2.2/applicant_data.json (≥ 30,000 records; mine: 30020).
    C. Cleaning/Standardization (local LLM)
        - Used the provided llm_hosting/app.py local model standardizer to normalize program and university names.
        - The LLM adds:
          * llm-generated-program
          * llm-generated-university
        - LLM intermediate outputs:
          * module_2.2/out_00.jsonl … out_04.jsonl
          * merged: module_2.2/out_all.jsonl
    D. Final cleaned dataset 
        - Converted the merged JSONL output into a final JSON dataset.
        - Final cleaned output file: module_2.2/final_applicant_data.json
        - This file uses the standardized program/university from the LLM fields where available.
    E. Efficiency / parallelization
        - Converted the merged JSONL output into a final JSON dataset.
        - Final cleaned output file: module_2.2/final_applicant_data.json
        - This file uses the standardized program/university from the LLM fields where available.