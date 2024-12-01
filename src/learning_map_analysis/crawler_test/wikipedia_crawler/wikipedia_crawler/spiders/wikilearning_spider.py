import scrapy
import networkx as nx
import json


class WikiLearningSpider(scrapy.Spider):
    name = "wikilearning"
    allowed_domains = ["en.wikipedia.org"]
    start_urls = ["https://en.wikipedia.org/wiki/Climate_change"]

    def __init__(self, max_depth=3, *args, **kwargs):
        super(WikiLearningSpider, self).__init__(*args, **kwargs)
        self.max_depth = int(max_depth)
        self.graph = nx.DiGraph()
        self.visited = set()
        self.network = []

    def parse(self, response, depth=0):
        if depth >= self.max_depth:
            return

        current_url = response.url
        self.visited.add(current_url)

        # Extract all Wikipedia links
        links = response.css("a[href^='/wiki/']:not([href*=':'])::attr(href)").getall()
        wiki_links = [response.urljoin(link) for link in links if response.urljoin(link) not in self.visited]

        # Add nodes and edges to the graph
        self.graph.add_node(current_url)
        for link in wiki_links:
            self.graph.add_edge(current_url, link)

        # Calculate PageRank
        pagerank = nx.pagerank(self.graph)

        # Sort links by PageRank and get top 5
        sorted_links = sorted([(link, pagerank.get(link, 0)) for link in wiki_links], 
                              key=lambda x: x[1], reverse=True)
        top_5_links = [link for link, rank in sorted_links[:5] if link not in self.visited]
        
        self.network.append({
            "title": current_url,
            "links": top_5_links
        })
        
        # Yield the current page data
        yield {
            "title": current_url,
            "links": top_5_links
        }

        # Recursively follow top 5 links
        for link in top_5_links:
            yield scrapy.Request(link, callback=self.parse, cb_kwargs={"depth": depth + 1})

    def closed(self, reason):
        with open("wikipedia_network.json", "w") as f:
            json.dump(self.network, f, indent=2)
