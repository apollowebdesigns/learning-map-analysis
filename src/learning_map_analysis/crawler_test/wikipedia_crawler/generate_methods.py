import logging
import json
from collections import Counter
import networkx as nx
from networkx.algorithms.community import louvain_communities, modularity
from networkx.algorithms.community.label_propagation import label_propagation_communities
from app import SUBECT_PREFIX
import pandas as pd
import numpy as np
from evaluation_methods import calculate_metrics
from networkx import pagerank
import concurrent.futures

# The upper value for this is 9 as Miller's Law is +- 2 from 7
MILLERS_LAW = 7 + 1 # The plus 1 allows for missing the first link when used

def _get_page_wiki(pagename):
    pagename = pagename.replace("/recommender/", "")
    return f"https://{SUBECT_PREFIX}.wikipedia.org/wiki/{pagename}"


class GenerateLearningJourneys():
    def __init__(self) -> None:
        pass
    
    def build_community_detection_journey(self, _dummy=None):
        graph = self.graph
        start_page = self.start_page
        method = self.method
        max_distance = self.max_distance
        communities = method(graph)
        communities_list = list(communities)
        postgresql_community = None
        for community in communities_list:
            if start_page in community:
                postgresql_community = community
                break
        
        if postgresql_community is None:
            raise ValueError(f"{start_page} page not found in any community")

        postgresql_community = set(postgresql_community)
        
        # Prepare the list for storing rows
        rows = []
        filtered_nodes = set()  # To store nodes within the max_distance
        
        # Add shortest path distance to each node in the community
        for page in postgresql_community:
            try:
                shortest_path_length = nx.shortest_path_length(graph, source=start_page, target=page)
            except nx.NetworkXNoPath:
                shortest_path_length = float('inf')
            if max_distance is None or shortest_path_length <= max_distance:
                rows.append({'Page': page, 'shortest_path': shortest_path_length})
                filtered_nodes.add(page)
            
        return filtered_nodes
    
    def build_community_detection_journeys(self, graph, start_page, method, max_distance=1, iterations=100, min_threshold=0.5):
        total_filtered_nodes = Counter()
        self.graph = graph
        self.start_page = start_page
        self.method = method
        self.max_distance = max_distance
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for filtered_nodes in executor.map(self.build_community_detection_journey, range(iterations)):
                filtered_nodes_counter = Counter(filtered_nodes)
                total_filtered_nodes +=  filtered_nodes_counter
        # Filter out on the percentage threshold value
        filtered_dict = {k: v for k, v in total_filtered_nodes.items() if v >= total_filtered_nodes.most_common(1)[0][1] * min_threshold}
        filtered_nodes_counter = Counter(filtered_dict)
        filtered_nodes = set(total_filtered_nodes)
        return filtered_nodes, graph.subgraph(filtered_nodes).copy()
    
    def build_centrality(self, graph, method, start_page):
        centrality = method(graph)
        filtered_nodes = [(node, cent) for node, cent in centrality.items()][:MILLERS_LAW]
        sorted_nodes = sorted(filtered_nodes, key=lambda x: x[1], reverse=True)
        recommended_nodes = sorted_nodes
        returned_nodes = {node[0] for node in recommended_nodes}
        returned_nodes.discard(_get_page_wiki(start_page))
        G = nx.DiGraph()
        G.add_nodes_from(returned_nodes)
        nodes = list(returned_nodes)
        for node, second in zip(nodes[1:], nodes[:-1]):
            G.add_edge(node, second)
        return returned_nodes, G
    
    def evaluate_modularity(self, graph, communities):
        try:
            mod = modularity(graph, communities)
        except Exception:
            # Assume that the random walk which is zero is good enough
            mod = 0
        
        return mod
