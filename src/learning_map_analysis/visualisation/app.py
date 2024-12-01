from flask import Flask, render_template, request
import json
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
import requests 
import subprocess
import os
import platform
import numpy as np

system = platform.system()

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/recommender/<username>")
def wikipedia_recommender(username):
    items = _find_recommendations(username)
    returned_links = []
    for link, rank in items:
        returned_links.append({'name': _remove_wiki(link), 'link': f'/recommender/{_remove_wiki(link)}'})
    return render_template('recommender.html',  username=username, items=returned_links)

@app.route("/get_community/<starting_page>")
def get_community(starting_page):
    graph = nx.DiGraph()
    network_data = _get_cache()
    graph = nx.node_link_graph(network_data)
    
    graph = build_postgresql_community_subgraph(graph, starting_page)
    print("Debugging")
    print(nx.node_link_data(graph))
    return json.dumps(nx.node_link_data(graph))

@app.route('/home')
def home():
    return render_template('search.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    items = _find_recommendations(query, first_load=True)
    returned_links = []
    for link, rank in items:
        returned_links.append({'name': _remove_wiki(link), 'link': f'/recommender/{_remove_wiki(link)}'})
    return render_template('recommender.html',  username=query, items=returned_links)

def _remove_wiki(wiki_url):
    return wiki_url.replace("https://en.wikipedia.org/wiki/", "")

def _find_recommendations(starting_page, first_load=False):
    graph = nx.DiGraph()
    network_data = _load_recommendations(starting_page)
    # Uncomment the below section if you want to use cached data and comment out line above
    # if first_load:
    #     network_data = _load_recommendations(starting_page)
    # else:
    #     network_data = _get_cache(starting_page)
    graph = nx.node_link_graph(network_data)
    
    graph = build_postgresql_community_subgraph(graph, starting_page)
    
    pagerank = nx.pagerank(graph)
    
    recommended_nodes = pagerank.items()

    # sorted_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
    # # Currently, nodes appear to be missing a few things
    # try:
    #     recommended_nodes = [(node, rank) for node, rank in sorted_nodes if rank/pagerank[f"https://en.wikipedia.org/wiki/{starting_page}"] < 2][:7]
    # except Exception:
    #     print("Warning: Nodes failed to normalise")
    #     ranks = [rank for _node, rank in sorted_nodes]
    #     normalised_ranks = ranks/np.linalg.norm(ranks)
    #     nodes = [node for node, _rank in sorted_nodes]
    #     marked_nodes = mark_outliers(normalised_ranks)
    #     # recommended_nodes = [(node, rank) for node, rank, mark in zip(nodes, normalised_ranks, marked_nodes) if mark][:7]
    #     recommended_nodes = sorted_nodes[:14]
    return recommended_nodes

def mark_outliers(data, m=2):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    # Return a mask rather than list
    return s < m

def _load_recommendations(page):
    """Builds the first network with api call
    Assumption is that the network is created from one call and that all learning journeys
    are made from this single call.
    
    This could be refactored in future to get better api calls
    """
    # call the crawler, generate recommendations
    # data = get_json_data(f"http://localhost:8000/{page}")
    script_path = os.path.abspath("../crawler_test/wikipedia_crawler/app.py")

    venv_location = '../../../.venv/bin/python'
    if system == "Windows":
        print("Warning: running on Windows")
        venv_location = '../../../.venv/Scripts/python'
    subprocess.call([venv_location, script_path, page])

    with open(f"{_remove_wiki(page)}_visualisation_data_graph.json", "r") as f:
        return json.load(f)
    # with open("static/graph.json", "w") as f:
    #     json.dump(data, f)
    # return data

def _get_cache(link):
    with open(f"{_remove_wiki(link)}_visualisation_data_graph.json", "r") as f:
        network_data = json.load(f)
    return network_data

def _get_page_wiki(pagename, link_prefix="/recommender/"):
    pagename = pagename.replace(link_prefix, "")
    return f"https://en.wikipedia.org/wiki/{pagename}"


def get_json_data(url):
    try:
        # Make the GET request
        response = requests.get(url)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the JSON data
        json_data = response.json()
        
        return json_data
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
def build_postgresql_community_subgraph(graph, start_page, max_distance=1):
    print("Debugging")
    print(start_page)
    start_page = _get_page_wiki(start_page)  # Assuming _get_page_wiki converts the page to the proper wiki format
    
    # Detect communities using the greedy modularity communities algorithm
    communities = list(greedy_modularity_communities(graph))
    
    # Find the community that contains the start page (PostgreSQL)
    postgresql_community = None
    for community in communities:
        if start_page in community:
            postgresql_community = community
            break
    
    if postgresql_community is None:
        raise ValueError(f"{start_page} page not found in any community")

    # Filter nodes to keep only those in the PostgreSQL community
    postgresql_community = set(postgresql_community)
    
    # Prepare the list for storing rows
    rows = []
    filtered_nodes = set()  # To store nodes within the max_distance
    
    # Add shortest path distance to each node in the PostgreSQL community
    for page in postgresql_community:
        try:
            # Calculate the shortest path length from the start page
            shortest_path_length = nx.shortest_path_length(graph, source=start_page, target=page)
        except nx.NetworkXNoPath:
            # Handle cases where there is no path between nodes
            shortest_path_length = float('inf')
        
        # Add each page and its shortest path length to the rows list
        if max_distance is None or shortest_path_length <= max_distance:
            rows.append({'Page': page, 'shortest_path': shortest_path_length})
            filtered_nodes.add(page)
    
    # Create a subgraph containing only the filtered nodes
    subgraph = graph.subgraph(filtered_nodes).copy()
    
    return subgraph