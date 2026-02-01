from urllib import parse, robotparser
agent = "joohyun"
url =  "https://www.thegradcafe.com/"

# Set up parser with website
parser = robotparser.RobotFileParser(url)
parser.set_url(parse.urljoin(url, "robots.txt"))
parser.read()

path = [
    "/",
    "/cgi-bin/",
    "/admin/",
    "/survey",
]

for p in path:
    print(f"{parser.can_fetch(agent, p), p}")
