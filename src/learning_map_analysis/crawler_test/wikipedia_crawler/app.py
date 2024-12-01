import os
from scrapy.crawler import CrawlerProcess
from wikipedia_crawler.spiders.wikifirstparagraphbot_spider import WikiFirstParagraphSpiderBot
from graph_builder import Network
from tests.test_postgres import LEARNING_JOURNEY
import sys
import json
SUBECT_PREFIX = "en"
SUBJECT = "PostgreSQL"

FILENAME = "en_wikipedia_paragraph_PostgreSQL_adapter.json"
IGNORE_LIST = "ignore-list.json"

def create_process():
    return CrawlerProcess(settings={
        'LOG_LEVEL': 'INFO',
        'EXTENSIONS': {
            'wikipedia_crawler.extensions.stats_collector.StatsCollectorExtension': 500,
        },
        'MYEXT_ENABLED': True,
        'NETWORK_GROWTH_FILE': 'network_growth.json',
    })
    

def run_spider(max_depth, subject, max_links):
    process = create_process()

    try:
        with open(IGNORE_LIST) as f:
            ignore_list = json.load(f)
    except FileNotFoundError:
        ignore_list = []

    process.crawl(WikiFirstParagraphSpiderBot, max_depth=max_depth, ignore_list=ignore_list, filename=FILENAME, max_links=max_links, start_urls=[
        f"https://{SUBECT_PREFIX}.wikipedia.org/wiki/{subject}"
    ])
    process.start()
    
    np = Network(FILENAME, max_links, LEARNING_JOURNEY, already_learned=ignore_list, start_page=f"https://{SUBECT_PREFIX}.wikipedia.org/wiki/{subject}")
    ignore_list.append(np.top_node)

    with open(IGNORE_LIST, "w") as f:
        json.dump(ignore_list, f)
        

def _remove_file():
    try:
        os.remove(IGNORE_LIST)
    except FileNotFoundError:
        pass

if __name__ == "__main__":
    # No caching for now for the list therefore remove file is there
    # The previous logic kept a file that was used for adaptive purposes
    _remove_file()
    run_spider(max_depth=3, subject=sys.argv[1], max_links=20)
