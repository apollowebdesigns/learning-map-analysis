import scrapy
import json
from bs4 import BeautifulSoup

class WikiFirstLinkSpider(scrapy.Spider):
    """Based of the paper for the first link analysis
    https://arxiv.org/abs/1605.00309
    
    While the first was not in Python code.
    """
    name = "wikifirstlink"
    allowed_domains = ["en.wikipedia.org"]
    start_urls = ["https://en.wikipedia.org/wiki/Climate_change"]

    def __init__(self, max_depth=20, *args, **kwargs):
        super(WikiFirstLinkSpider, self).__init__(*args, **kwargs)
        self.max_depth = int(max_depth)
        self.network = []
        self.visited = set()

    def parse(self, response, depth=0):
        if depth >= self.max_depth or response.url in self.visited:
            return

        self.visited.add(response.url)
        current_url = response.url
        first_link = self.get_first_link(response)

        self.network.append({
            "title": current_url,
            "links": [first_link]
        })

        # if first_link and first_link not in self.visited:
        #     yield scrapy.Request(first_link, callback=self.parse, cb_kwargs={"depth": depth + 1})
        yield scrapy.Request(first_link, callback=self.parse, cb_kwargs={"depth": depth + 1})

    def get_first_link(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        content = soup.find(id="bodyContent")
        
        for paragraph in content.find_all('p', recursive=True):
            for link in paragraph.find_all('a', recursive=True):
                href = link.get('href')
                if href and href.startswith('/wiki/') and ':' not in href:
                    return response.urljoin(href)
        
        return None

    def closed(self, reason):
        with open("wikipedia_first_link_network.json", "w") as f:
            json.dump(self.network, f, indent=2)