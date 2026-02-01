Module 2: GradCafe Web Scraper


--------------------------------
Robots.txt Check (Part A)
--------------------------------

Before scraping any admissions data, I checked GradCafe's robots.txt to confirm scraping permission.

- robots.txt URL checked:
    https://www.thegradcafe.com/robots.txt

- Script used:
    module_2/robot_check.py

- Evidence:
    (True, '/')
    (True, '/cgi-bin/')
    (True, '/admin/')
    (True, '/survey/')
    (True, 'survey/?program=Computer+Science')
