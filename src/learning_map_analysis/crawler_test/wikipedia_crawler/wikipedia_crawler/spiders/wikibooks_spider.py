import scrapy
import json


class WikiBooksSpider(scrapy.Spider):
    name = "wikibooks"
    allowed_domains = ["en.wikibooks.org"]
    start_urls = ["https://en.wikibooks.org/wiki/Climate_Change"]

    def __init__(self, max_depth=2, *args, **kwargs):
        super(WikiBooksSpider, self).__init__(*args, **kwargs)
        self.max_depth = int(max_depth)
        self.network = []

    def parse(self, response, depth=0):
        if depth >= self.max_depth:
            return

        current_url = response.url
        links = response.css("a[href^='/wiki/']:not([href*=':'])::attr(href)").getall()
        wiki_links = [response.urljoin(link) for link in links]

        self.network.append({
            "title": current_url,
            "links": wiki_links
        })

        for link in wiki_links:
            yield scrapy.Request(link, callback=self.parse, cb_kwargs={"depth": depth + 1})

    def closed(self, reason):
        with open("wikibook_network.json", "w") as f:
            json.dump(self.network, f, indent=2)
