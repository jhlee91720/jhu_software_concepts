from urllib.request import urlopen
import json

# Collect the National Weather Service's Data About the Weather in Washington D.C.
url = "https://api.weather.gov/gridpoints/LWX/96,70/forecast/hourly"

# Open the website
page = urlopen(url)

# Extract the html from the website
html_bytes = page.read()

# Load JSON object
washington_weather = json.loads(html_bytes)  # JSON object = python dicts ; JSON array = pythong lists

# Print the JSON object
print(f"current temperature in D.C. is { washington_weather['properties']['periods'][0]['temperature'] }.")





##############Handling URL Errors##################

from urllib import error, request
try:
    response = request.urlopen(url)
except error.HTTPError as err:
    if err.code == 400:
        print("Bad Request!")
    if err.code == 404:
        print("Page not Found!")
    else:
        print(f"An HTTP error has occured: {err}")
      
###################################################  




############Breaking down URLs#####################

from urllib import parse, request

parsed = parse.urlparse(url)
path = parsed.path

##################################################




##############Building Up URLs####################

location_paths = {
    "DC" : "LWX/96,70/forecast/hourly",
    "NYC" : "OKX/34,35/forecase/hourly",
    "LA" : "LOX/155,45/forecast/hourly"
}

url = "https://api.weather.gov/gridpoints/" "https://api.weather.gov/gridpoints/LWX/96,70/forecast/hourly"

for key in location_paths:
    location_url = parse.urljoin(url, location_paths[key])
    page = request.urlopen(location_url)
    html_bytes = page.read()
    weather = json.loads(html_bytes)
    degrees = weather['properties']['periods'][0]['temperature']

print(f"Current temperature in {key} is {degrees} degrees fahrenheit.")

##################################################




##########Parsing Crawler Access##################
from urllib import parse, robotparser
agent = "x"
url =  "https://www.thegradcafe.com/"

# Set up parser with website
parser = robotparser.RobotFileParser(url)
parser.set_url(parse.urljoin(url, "robots.txt"))
parser.read()

path = [
    "/",
    "/cgi-bin/",
    "/admin/",
    "survey/?program=Computer+Science"
]

for p in path:
    print(f"{parser.can_fetch(agent, p), p}")
    
##################################################