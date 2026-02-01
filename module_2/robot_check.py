from urllib import robotparser, parse
from urllib.request import urlopen

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
    "/survey/?program=Computer+Science"
]

for p in path:
    print(f"{parser.can_fetch(agent, p), p}")
    
################################################################################