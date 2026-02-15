from bs4 import BeautifulSoup
from urllib.request import urlopen

url = "https://e-catalogue.jhu.edu/course-search/"
page = urlopen(url)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")

text = soup.get_text()
spaceless_text = text.replace("\n\n", "")
# print(spaceless_text)

# Get the Page Title
# print(soup.title.string)

# Find all Departments
department_html = soup.find_all("option")
department = [i.get_text() for i in department_html]
print(department)
