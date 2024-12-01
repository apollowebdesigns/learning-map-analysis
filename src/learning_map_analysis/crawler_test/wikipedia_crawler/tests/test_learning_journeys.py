import os
import requests
from bs4 import BeautifulSoup
import json
EXCLUDED_LINKS = [
    "https://en.wikipedia.org/wiki/Main_Page",
    "https://en.wikipedia.org/#",
    "https://en.wikipedia.org",
    "https://en.wikipedia.org//wikimediafoundation.org/",
    'https://en.wikipedia.org#bodyContent',
    'https://en.wikipedia.org#',
]


class DataStore():
    def __init__(self):
        self.links = [
            "https://en.wikipedia.org/wiki/User:David_Eppstein/Graph_Algorithms",
            "https://en.wikipedia.org/wiki/User:David_Eppstein/Graph_Drawing",
            "https://en.wikipedia.org/wiki/User:David_Eppstein/Fundamental_Data_Structures",
            "https://en.wikipedia.org/wiki/User:David_Eppstein/Matroid_Theory",
            "https://en.wikipedia.org/wiki/User:David_Eppstein/Perfect_Graphs",
        ]
        
        self.link_map = {link: self.get_wikipedia_links(link) for link in self.links}

    def get_wikipedia_links(self, url):
        # Send a GET request to the webpage
        response = requests.get(url)
        
        # Create a BeautifulSoup object to parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        wikipedia_links = []

        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        for link in soup.find_all("a"):
            url = link.get("href", "")
            if ":" not in url.replace('https://en.wikipedia.org', ''):
                if "https://en.wikipedia.org/wiki/Main_Page" not in url.replace('https://en.wikipedia.org', ''):
                    full_link = 'https://en.wikipedia.org' + url
                    if full_link not in EXCLUDED_LINKS:
                        wikipedia_links.append(full_link)
        return wikipedia_links
    
    def get_chapters(self):
        """Gets the chapter links and breaks down the above
        """
        
        # Initialize the dictionary to store chapter links
        chapter_links = {}
        
        for url in self.links:
            # url = "https://en.wikipedia.org/wiki/User:David_Eppstein/Graph_Algorithms"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the main content area
            content = soup.find('div', {'id': 'mw-content-text'})

            # Find all h2 headers (chapters) and extract links
            for header in content.find_all('dl'):
                headline_span = header.find('dt')
                if headline_span and headline_span.text:
                    chapter_title = headline_span.text
                    chapter_links[chapter_title] = []
                    # Find the next sibling ul element (list of links)
                    next_element = header.find_next_sibling()
                    if next_element and next_element.name == 'dl':
                        for li in next_element.find_all('dd'):
                            link = li.find('a')
                            if link and link.has_attr('href'):
                                chapter_links[chapter_title].append({
                                    'text': link.text,
                                    'href': 'https://en.wikipedia.org' + link['href'],
                                    'book': url
                                })
            # Print the resulting dictionary
            # for chapter, links in chapter_links.items():
            #     print(f"\n{chapter}:")
            #     for link in links:
            #         print(f"  - {link['text']}: {link['href']}")
        return chapter_links
    
    def get_chapters_static(self):
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the path to the 'chapters' directory
        CHAPTERS = os.path.join(script_dir, "chapters")
        
        res = {}

        # Check if the directory exists
        if not os.path.exists(CHAPTERS):
            print(f"Warning: Directory {CHAPTERS} does not exist.")
            return res

        files = os.listdir(CHAPTERS)

        for file in files:
            file_path = os.path.join(CHAPTERS, file)
            if os.path.isfile(file_path) and file.endswith(".json"):
                try:
                    with open(file_path, "r", encoding='utf-8') as f:
                        data = json.load(f)
                        res.update(data)
                except json.JSONDecodeError:
                    print(f"Warning: {file} is not a valid JSON file.")
                except IOError:
                    print(f"Error: Could not read file {file}.")

        return res