import re

from builtins import str  #  pip install future
from urllib.parse import urlparse
from html.parser import HTMLParser


class LinkerFinder(HTMLParser):
    def __init__(self, keyword, url, domain):
        self.url = url
        self.parsed_url = urlparse(url)
        self.cache = []
        self.existed = False
        self.domain = domain
        self.keyword = keyword
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        regx = re.compile(self.keyword)

        for (attribute, value) in attrs:
            if attribute == "href" and tag == "a":
                format_value = self.format_url(value)
                if format_value is not None:
                    self.cache.append(format_value)

            if value is not None and bool(re.search(regx, value)):
                self.existed = True


    def format_url(self, url):
        if bool(re.search(r"^\/\/", url)):
            url =  f"{self.parsed_url.scheme}:{url}"

        if bool(re.search(r"^/[a-zA-Z]", url)):
            url =  f"{self.parsed_url.scheme}://{self.parsed_url.netloc}{url}"

        if self.domain is not None:
            re_domain = re.compile(self.domain)
            if not bool(re.search(re_domain, url)):
                return None

        return url

    def handle_data(self, data):
        regx = re.compile(self.keyword)

        if data is not None and bool(re.search(regx, data)):
            self.existed = True

