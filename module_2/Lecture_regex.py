from urllib.request import urlopen
import json

url = "https://en.wikipedia.org/wiki/python_(programming_language)"

page = urlopen(url)

#extrac the HTML from the page
html_bytes = page.read()
html = html_bytes.decode("utf-8")

# You'll immediately relize that this is a lot of data
# suppose you're just looking for the title

title_index = html.find("<title>")
start_index = title_index + len("<title>")
end_index = html.find("</title>")
title = html[start_index : end_index]

print(title)

###################################################

import re
from urllib.request import urlopen

# 1 #
string = "Welcome to EN605.256: modern software concepts in Python!"
# I want to find the course number within the string above 
print (re.search("[A-Za-z]{2}[0-9]*\.[0-9]+", string))




# 2 #
url = "https://e-catalogue.jhu.edu/course-search/"
page = urlopen(url)

# Extract the HTML from the page
html_bytes = page.read()
html = html_bytes.decode("utf-8")

# Find all Engineering department numbers
search_query = "EN\.\d{3}"

# I want to find the departmnet number within the string above
course_numbers = re.findall(search_query, html)
print (course_numbers)

sample_html = """
<option value = "SA.901">SA.901 - Arabic</option>
<option value = "SA.902">SA.902 - Chinese</option>
<option value = "SA.903">SA.903 - English</option>
<option value = "SA.904">SA.904 - French</option>
<option value = "SA.905">SA.905 - Language</option>
<option value = "SA.906">SA.906 - Italian</option>
<option value = "SA.907">SA.907 - Japanese</option>
<option value = "SA.908">SA.908 - Portuguese</option>
<option value = "SA.909">SA.909 - Russian</option>
<option value = "SA.910">SA.910 - Language</option>
<option value = "SA.911">SA.911 - Indonesian</option>
<option value = "SA.912">SA.912 - Vietnamese</option>
<option value = "SA.913">SA.913 - Thai</option>
<option value = "SA.914">SA.914 - Hindi</option>
<option value = "SA.915">SA.915 - Korean</option>
<option value = "SA.916">SA.916 - Persian</option>
<option value = "SA.917">SA.917 - Burnese</option>
<option value = "SA.990">SA.990 - International Relations</option>
<option value = "SA.999">SA.999 - No Department</option>
"""

# use re to split string
cleaned = re.split('<option value = ".{6}"> \ </option> \ \n', sample_html)

# Filter the output
filtered = list(filter(None, cleaned))
print(filtered)

# 3 #
joe_review = """
A Performance Review: Joe Kovba has been a valuable member of our software development team for the past year, demonstrating strong technical skills, a positive attitude, and a willingness to take on new challenges. Joe's contributions have been instrumental in the success of several key projects.

Joe is proficient in Python and has a deep understanding of software development best practices. Joe's code is consistently well-structured, efficient, and maintainable.
"""

# Substitute Joe for Liv
messy_liv_review = re.sub("Joe Kovba", "Liv d'Aliberti", joe_review)
cleaner_review = re.sub("Joe", "Liv", messy_liv_review)
liv_review = re.sub("joe", "liv", cleaner_review)

print(liv_review)

# 4 #
inputs = [
    "John's phone number is 7033217654", 
    "(703)32317654 was the number Kelly gave me", 
    "(703) 321 7654 is Liam's mom's number",
    "703.321.7654 is waht was in the log for Millie",
    "(703)-321-7654 was Nikhil's number last year",
    "the number for Omar is 703-321-7654"
]

first_three = "(\\d{3} | \\(\\d{3}\\))"
second_three = "(\\d{3})"
four_digits = "(\\d{4})"
sep = '(:?\\s+|-|\\.)?'
grouped_pattern = re.compil(f"""
                            {first_three}
                            {sep}
                            {second_three}
                            {sep}
                            {four_digits}""", re.VERBOSE)

result = ["".join(grouped_pattern.findall(i)[0]) for i in inputs]
print(result)
