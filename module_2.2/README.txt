1. Name:
   Joohyun Lee, [YOUR JHED ID]

2. Module Info:
   Module 2 - Web Scraping, URL Management, and LLM Data Cleaning
   Due Date: [DUE DATE FROM SYLLABUS / ASSIGNMENT PAGE]

3. Approach:
   - Robots.txt compliance:
     I used urllib.robotparser to fetch and check robots.txt for thegradcafe.com before scraping any pages.
     I verified can_fetch() for the pages I scraped. Evidence is included as screenshot.jpg.

   - Scraping (urllib + BeautifulSoup/regex/string methods):
     I used urllib.request.urlopen to download GradCafe survey pages and (when needed) individual result pages.
     I used urllib.parse.urljoin/urlparse for URL management.
     I used BeautifulSoup and string/regex parsing to extract required fields such as:
       program (raw combined program+university text), date_added, url, status, term, degree,
       US/International, comments, and GRE/GPA fields when available.
     The raw scraped output is stored as JSON under applicant_data.json in this folder.

   - Cleaning (local LLM standardizer):
     I used the provided llm_hosting sub-package to run a small local language model to standardize program and university names.
     The tool adds two fields: llm-generated-program and llm-generated-university.
     I then mapped these standardized values into clean program_name and university fields for analysis.

   - Efficiency / parallelization:
     To reduce total cleaning time, I split the dataset into multiple JSON chunks and ran 4–5 parallel runs of the standardizer,
     then merged the outputs back into a single cleaned JSON.

4. Known Bugs:
   [If none, write: "None known at submission time."]1. Name:
   Joohyun Lee, [YOUR JHED ID]

2. Module Info:
   Module 2 - Web Scraping, URL Management, and LLM Data Cleaning
   Due Date: [DUE DATE FROM SYLLABUS / ASSIGNMENT PAGE]

3. Approach:
   - Robots.txt compliance:
     I used urllib.robotparser to fetch and check robots.txt for thegradcafe.com before scraping any pages.
     I verified can_fetch() for the pages I scraped. Evidence is included as screenshot.jpg.

   - Scraping (urllib + BeautifulSoup/regex/string methods):
     I used urllib.request.urlopen to download GradCafe survey pages and (when needed) individual result pages.
     I used urllib.parse.urljoin/urlparse for URL management.
     I used BeautifulSoup and string/regex parsing to extract required fields such as:
       program (raw combined program+university text), date_added, url, status, term, degree,
       US/International, comments, and GRE/GPA fields when available.
     The raw scraped output is stored as JSON under applicant_data.json in this folder.

   - Cleaning (local LLM standardizer):
     I used the provided llm_hosting sub-package to run a small local language model to standardize program and university names.
     The tool adds two fields: llm-generated-program and llm-generated-university.
     I then mapped these standardized values into clean program_name and university fields for analysis.

   - Efficiency / parallelization:
     To reduce total cleaning time, I split the dataset into multiple JSON chunks and ran 4–5 parallel runs of the standardizer,
     then merged the outputs back into a single cleaned JSON.

4. Known Bugs:
   [If none, write: "None known at submission time."]