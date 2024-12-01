import scrapy
import json
from urllib.parse import quote

SUBECT_PREFIX = "en"

class WikispiderSpider(scrapy.Spider):
    name = "wikispider"
    allowed_domains = [f"{SUBECT_PREFIX}.wikipedia.org"]
    api_url = f"https://{SUBECT_PREFIX}.wikipedia.org/w/api.php"

    def __init__(self, start_page="PostgreSQL", max_depth=2, *args, **kwargs):
        super(WikispiderSpider, self).__init__(*args, **kwargs)
        self.start_page = start_page
        self.max_depth = int(max_depth)
        self.network = []
        self.visited_urls = set()

    def start_requests(self):
        yield self.build_request(self.start_page, 0)

    def build_request(self, title, depth):
        params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "links",
            "pllimit": "max"
        }
        url = f"{self.api_url}?{self.urlencode(params)}"
        return scrapy.Request(url, callback=self.parse_api_response, cb_kwargs={"depth": depth, "title": title})

    def parse_api_response(self, response, depth, title):
        if depth >= self.max_depth:
            return

        data = json.loads(response.text)
        page_id = list(data['query']['pages'].keys())[0]
        current_url = f"https://{SUBECT_PREFIX}.wikipedia.org/wiki/{quote(title)}"

        if current_url in self.visited_urls:
            return
        self.visited_urls.add(current_url)

        links = []
        if 'links' in data['query']['pages'][page_id]:
            links = [link['title'] for link in data['query']['pages'][page_id]['links']]

        # Filter out unwanted links
        filtered_links = [link for link in links if not self.should_filter(link)]

        # Build full URLs for the filtered links
        wiki_links = [f"https://{SUBECT_PREFIX}.wikipedia.org/wiki/{quote(link)}" for link in filtered_links]

        # Append the current URL and its links to the network
        self.network.append({
            "title": current_url,
            "links": wiki_links
        })

        # Yield requests for each filtered link
        for link in filtered_links:
            full_link = f"https://{SUBECT_PREFIX}.wikipedia.org/wiki/{quote(link)}"
            if full_link not in self.visited_urls:
                yield self.build_request(link, depth + 1)

    def should_filter(self, title):
        # Define keywords to filter out
        redirect_keywords = [
            "Wikipedia:",
            "Category:",
            "File:",
            "Template:",
            "Help:",
            "ISSN (identifier)",
        ]
        # Check if the title contains any of the redirect keywords
        return any(keyword in title for keyword in redirect_keywords)

    def closed(self, reason):
        with open(f"{SUBECT_PREFIX}_wikipedia_network_{self.start_page}.json", "w") as f:
            json.dump(self.network, f, indent=2)

    @staticmethod
    def urlencode(params):
        return "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
