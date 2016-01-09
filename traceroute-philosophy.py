import sys
import re
import requests
from bs4 import BeautifulSoup

class PageNotFoundException(Exception):
    pass

class LoopException(Exception):
    pass

class NoLinkException(Exception):
    pass


def gen_url(entry):
    wordlist = entry.split(' ')
    return "https://en.wikipedia.org/wiki/" + '_'.join(wordlist)


class Crawl():
    def __init__(self, init_url):
        self.url = init_url
        self.finished = False
        self.count = -1
        self.history = set()

    def next(self):
        r = requests.get(self.url)
        if (r.status_code != 200):
            raise PageNotFoundException
        self.soup = BeautifulSoup(r.text, "html.parser")
        self.url = self.soup.find("link", {"rel": "canonical"})["href"]
        if self.url in self.history:
            raise LoopException
        self.history.add(self.url)
        self.title = self.soup.find("h1", {"id": "firstHeading"}).text
        self.count += 1
        if (self.title == "Philosophy"):
            self.finished = True
        self.get_next_url()

    def get_next_url(self):
        body = self.soup.find("div", {"id": "mw-content-text"})
        for tag in body.find_all(["table", "sup", "i", "span", "div", "small", "cite"]):
            tag.extract()
        for ext in body.find_all("a", {"class": "external text"}):
            ext.extract()
        for internal in body.find_all("a", {"class": "internal"}):
            internal.extract()
        for red in body.find_all("a", {"class": "new"}):
            red.extract()
        for red in body.find_all("a", {"class": "extiw"}):
            red.extract()

        # Should use a pure RE solution
        for a in body.find_all("a"):
            a["href"] = a["href"].replace('(','[')
            a["href"] = a["href"].replace(')',']')
        text = re.sub(r'\([^)]*\)', '', str(body))
        new_soup = BeautifulSoup(text, "html.parser")
        for a in new_soup.find_all("a"):
            a["href"] = a["href"].replace('[','(')
            a["href"] = a["href"].replace(']',')')

        try:
            a = new_soup.find("a")
            self.url = gen_url((a["href"].split('#')[0]).split('/')[-1])
        except:
            raise NoLinkException



if len(sys.argv) == 0:
    print("Please input an argument.")
    exit(0)
url = gen_url(' '.join(sys.argv[1:]))
crawl = Crawl(url)
try:
    while not crawl.finished:
        crawl.next()
        print(str(crawl.count) + ' ' + crawl.title)
    print("Distance to 'philosophy': %d" % crawl.count)
except PageNotFoundException:
    print("Page not found. No route to 'philosophy'.")
except LoopException:
    print("Loop detected. No route to 'philosophy'.")
except NoLinkException:
    print("Cannot find valid link. No route to 'philosophy'.")
except requests.exceptions.ConnectionError:
    print("Cannot reach Wikipedia server. Please check your connection.")
except KeyboardInterrupt:
    pass
