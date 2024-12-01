import json
import networkx as nx
import traceback
from ranking_methods import GenerateLearningJourneys


from app import SUBECT_PREFIX
import subprocess
import platform
import os
import seaborn as sns

system = platform.system()


def run_scraper(start_link):
    venv_location = '../../../../.venv/bin/python'
    if system == "Windows":
        print("Warning: running on Windows")
        venv_location = '../../../../.venv/Scripts/python'
    script_path = os.path.abspath("app.py")
    print("subprocess started")
    subprocess.call([venv_location, script_path, start_link])
    print("subprocess finished")
    

links = [
    "https://en.wikipedia.org/wiki/Battle_of_Glasgow,_Missouri",
    "https://en.wikipedia.org/wiki/PostgreSQL",
    "https://en.wikipedia.org/wiki/Confederate_States_of_America",
    "https://en.wikipedia.org/wiki/Aedes_albopictus",
    "https://en.wikipedia.org/wiki/Aedes_aegypti",
    "https://en.wikipedia.org/wiki/Quantum_mechanics",
    "https://en.wikipedia.org/wiki/Quantum_computing",
    "https://en.wikipedia.org/wiki/Limestone",
]

count = []


for counter, link in enumerate(links):
    start_link = link.replace(f"https://{SUBECT_PREFIX}.wikipedia.org/wiki/", "")
    run_scraper(start_link)
    with open('visualisation_data_graph.json', 'r') as f:
        network_data = json.load(f)
    graph = nx.node_link_graph(network_data)
    try:
        gen_learning_journeys = GenerateLearningJourneys()
        journeys = list(gen_learning_journeys.build_community_detection_journeys(graph, link))
        count.append(len(journeys))
    except Exception:
        print("Unable to parse specific learning journey, reason is:")
        print(traceback.format_exc())
        
    
    
sns.boxplot(count)
