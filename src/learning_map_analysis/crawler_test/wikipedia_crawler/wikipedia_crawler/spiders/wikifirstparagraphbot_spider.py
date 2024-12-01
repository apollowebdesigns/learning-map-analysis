import scrapy
import json
from bs4 import BeautifulSoup
from datetime import datetime

# This decides the top number of links to use
TOP_NUMBER = 20
SUBECT_PREFIX = "en"
SUBJECT = "PostgreSQL"


class WikiFirstParagraphSpiderBot(scrapy.Spider):
    """Based of the paper for the first link analysis
    https://arxiv.org/abs/1605.00309
    
    While the first was not in Python code.
    """
    name = "wikifirstparagraphbot"
    allowed_domains = [f"{SUBECT_PREFIX}.wikipedia.org"]
    # start_urls = [f"https://{SUBECT_PREFIX}.wikipedia.org/wiki/{SUBJECT}"]
    # start_urls = [
    #     f"https://{SUBECT_PREFIX}.wikipedia.org/wiki/{SUBJECT}"
    # ]
      # Example start URL

    def __init__(self, max_depth=20, ignore_list=[], filename="test.json", starter=None, max_links=20, *args, **kwargs):
        super(WikiFirstParagraphSpiderBot, self).__init__(*args, **kwargs)
        self.max_depth = int(max_depth)
        self.max_links = int(max_links)
        self.network = []
        self.visited = set()
        self.ignore_list = ignore_list
        self.filename = filename
        self.links_to_count_list = []
        self.links_to_count = set()
        self.link_counter = {}
        self.link_counter_list = {}
        self.end_times = {}
        self.start_time = datetime.now()
        for url in ignore_list:
            self.start_urls.append(url)

    def parse(self, response, depth=0):
        if depth >= self.max_depth or response.url in self.visited:
            return
        
        if response.url in self.ignore_list:
            return

        self.visited.add(response.url)
        current_url = response.url
        first_link_paragraph = self.get_first_paragraph(response)
        
        for link_returned in first_link_paragraph:
            self.links_to_count.add(link_returned)
            self.links_to_count_list.append(link_returned)
        self.link_counter[depth] = len(self.links_to_count)
        self.link_counter_list[depth] = len(self.links_to_count_list)
        self.end_times[depth] = (datetime.now() - self.start_time).total_seconds() / 60  # Duration in minutes

        self.network.append({
            "title": current_url,
            "links": first_link_paragraph
        })

        # if first_link and first_link not in self.visited:
        #     yield scrapy.Request(first_link, callback=self.parse, cb_kwargs={"depth": depth + 1})
        for link in first_link_paragraph:
            if link not in self.visited:
                yield scrapy.Request(link, callback=self.parse, cb_kwargs={"depth": depth + 1})

    def get_first_paragraph(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        content = soup.find(id="bodyContent")
        links = []
        for paragraph in content.find_all('p', recursive=True):
            for link in paragraph.find_all('a', recursive=True):
                href = link.get('href')
                if href and href.startswith('/wiki/') and ':' not in href:
                    links.append(response.urljoin(href))
            # break

        return links[:self.max_links]

    def closed(self, reason):
        for link in self.ignore_list:
            # This allows the completed node to be added to the network
            self.network.append({
                "title": link,
                "links": []
            })
        # with open(f"{SUBECT_PREFIX}_wikipedia_paragraph_{SUBJECT}_top_number_{TOP_NUMBER}_max_depth_{self.max_depth}.json", "w") as f:
        with open(self.filename, "w") as f:
            json.dump(self.network, f, indent=2)