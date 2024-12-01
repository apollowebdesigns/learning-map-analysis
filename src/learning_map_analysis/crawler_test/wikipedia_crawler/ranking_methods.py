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
from functools import reduce

logger = logging.getLogger(__name__)

# The upper value for this is 9 as Miller's Law is +- 2 from 7
MILLERS_LAW = 7 + 1 # The plus 1 allows for missing the first link when used


def _get_page_wiki(pagename):
    pagename = pagename.replace("/recommender/", "")
    return f"https://{SUBECT_PREFIX}.wikipedia.org/wiki/{pagename}"

class CommunityDetectionComparison:
    def  __init__(self, graph, start_page, truth_learning_links):
        self.truth_learning_links = truth_learning_links
        self.start_page = start_page
        self.learning_journey_length = len(truth_learning_links)
        methods = [
            louvain_communities,
            label_propagation_communities,
            pagerank,
        ]
        arguments = [
            {"graph": graph, "start_page": start_page, "method": louvain_communities},
            {"graph": graph, "start_page": start_page, "method": label_propagation_communities},
            {"graph": graph, "start_page": start_page, "method": pagerank, "centrality_method": True},
        ]
        self.graph_args = {
            "louvain_communities": [graph],
            "label_propagation_communities": [graph.to_undirected()],  # Minimum  number of nodes in a clique
            "pagerank": [graph]
        }
        self.metrics = {}
        self.subgraphs = {}
        self.modularity_evaluations = {}
        self.jaccard_scores = {}
        self.metrics_error = {}
        self.modularity_evaluations_error = {}
        self.jaccard_scores_error = {}

        num_iterations = 10

        for method, args in zip(methods, arguments):
            method_metrics = []
            method_modularities = []
            method_jaccards = []
            
            for _ in range(num_iterations):
                built = self.build_postgresql_community_subgraph(**args)
                method_metrics.append(set(built[0]))
                method_modularities.append(built[2])
                
                # Calculate Jaccard coefficient
                detected_community = set(built[0])
                truth_community = set(self.truth_learning_links)
                jaccard_score = self.calculate_jaccard_coefficient(detected_community, truth_community)
                method_jaccards.append(jaccard_score)
            
            # Calculate averages
            self.metrics[method.__name__] = list(set.intersection(*method_metrics))
            self.subgraphs[method.__name__] = graph.subgraph((set.intersection(*method_metrics))).copy()
            self.modularity_evaluations[method.__name__] = np.mean(method_modularities)
            self.jaccard_scores[method.__name__] = np.mean(method_jaccards)
            # Calculate error
            self.metrics_error[method.__name__] = list({j for i in method_metrics for j in i})
            self.modularity_evaluations_error[method.__name__] = np.max(method_modularities) - np.min(method_modularities)
            self.jaccard_scores_error[method.__name__] = np.max(method_jaccards) - np.min(method_modularities)
            
        self.algorithm_ranking = sorted(self.jaccard_scores.items(), key=lambda x: x[1], reverse=True)
        with open("community_detection_learning_journeys.json", "w") as f:
            json.dump(self.metrics, f)
            
    def get_algorithm_ranking(self):
        return self.algorithm_ranking

    def evaluate_modularity(self, graph, communities):
        try:
            mod = modularity(graph, communities)
        except Exception:
            # Assume that the random walk which is zero is good enough
            mod = 0
        
        return mod
    
    
    def build_community_detection_journey(self, _dummy=None):
        graph = self.graph
        start_page = self.start_page
        method = self.method
        max_distance = self.max_distance
        communities = method(*self.graph_args[method.__name__])
        communities_list = list(communities)
        
        mod = self.evaluate_modularity(graph, communities)
        
        # Find the community that contains the start page (PostgreSQL)
        postgresql_community = None
        for community in communities_list:
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
                
        return filtered_nodes, mod
        

    def build_postgresql_community_subgraph(self, graph, start_page, method, max_distance=1, centrality_method=False, iterations=100, min_threshold=0.5):
        # print("Debugging")
        # print(start_page)
        start_page = _get_page_wiki(start_page)  # Assuming _get_page_wiki converts the page to the proper wiki format
        self.graph = graph
        self.start_page = start_page
        self.method = method
        self.max_distance = max_distance
        # Detect communities using the greedy modularity communities algorithm
        # print(f"Debugging, method used is: {method.__name__}")
        if centrality_method:
            filtered_nodes = self.build_pageranking_selection(graph, start_page, method)
            mod = np.nan
        else:
            # Methods are a measure of community detection below
            total_filtered_nodes = Counter()
            modularities = []
            with concurrent.futures.ProcessPoolExecutor() as executor:
                for filtered_nodes, mod in executor.map(self.build_community_detection_journey, range(iterations)):
                    filtered_nodes_counter = Counter(filtered_nodes)
                    total_filtered_nodes +=  filtered_nodes_counter
                    modularities.append(mod)
            filtered_dict = {k: v for k, v in total_filtered_nodes.items() if v >= total_filtered_nodes.most_common(1)[0][1] * min_threshold}
            filtered_nodes_counter = Counter(filtered_dict)
            filtered_nodes = set(total_filtered_nodes)
            mod = np.average(modularities)
            
        filtered_nodes.discard(_get_page_wiki(self.start_page))
        # Create a subgraph containing only the filtered nodes
        subgraph = graph.subgraph(filtered_nodes).copy()
        
        if not filtered_nodes:
            logger.warning("No nodes  found within the specified distance.")
        
        return list(subgraph.nodes), subgraph, mod
    
    def get_evaluations(self):
        data = {name: calculate_metrics(metric, self.truth_learning_links) for name, metric in self.metrics.items()}
        for var_name, _metric in data.items():
            data[var_name]['scraper_percentage_covered'] = 100 - (100 * (len(set(self.truth_learning_links) - set(self.graph))/len(self.truth_learning_links)))
        for name, score in self.jaccard_scores.items():
            data[name]['Jaccard Coefficient'] = score
        records = {key: list(value.values()) for key, value in data.items()}
        columns = data[list(data.keys())[0]].keys()
        return pd.DataFrame.from_dict(records, orient='index', columns=columns)
    
    def get_errors(self):
        data = {name: calculate_metrics(metric, self.truth_learning_links) for name, metric in self.metrics_error.items() if name not in self.metrics.keys()}
        # for name, score in self.jaccard_scores_error.items():
        #     data[name]['Jaccard Coefficient'] = score
        if data:
            records = {key: list(value.values()) for key, value in data.items()}
            columns = data[list(data.keys())[0]].keys()
            return pd.DataFrame.from_dict(records, orient='index', columns=columns)
        else:
            return None
    
    def calculate_jaccard_coefficient(self, community1, community2):
        set1 = set(community1)
        set2 = set(community2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union != 0 else 0
    
    def build_pageranking_selection(self, graph, starting_page, method, percentile=90):
        centrality = method(graph)
        filtered_nodes = [(node, cent) for node, cent in centrality.items()][:MILLERS_LAW]
        sorted_nodes = sorted(filtered_nodes, key=lambda x: x[1], reverse=True)
        recommended_nodes = sorted_nodes
        returned_nodes = {node[0] for node in recommended_nodes}
        returned_nodes.discard(_get_page_wiki(self.start_page))
        return returned_nodes

def build_pageranking_selection(graph, start_page, max_distance=1):
    pagerank = nx.pagerank(graph)
    
    recommended_nodes = pagerank.items()

    sorted_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
    # Currently, nodes appear to be missing a few things
    try:
        recommended_nodes = [(node, rank) for node, rank in sorted_nodes if rank/pagerank[f"https://en.wikipedia.org/wiki/{starting_page}"] < 2][:7]
    except Exception:
        print("Warning: Nodes failed to normalise")
        ranks = [rank for _node, rank in sorted_nodes]
        normalised_ranks = ranks/np.linalg.norm(ranks)
        [node for node, _rank in sorted_nodes]
        mark_outliers(normalised_ranks)
        # recommended_nodes = [(node, rank) for node, rank, mark in zip(nodes, normalised_ranks, marked_nodes) if mark][:7]
        recommended_nodes = sorted_nodes[:MILLERS_LAW]
    return recommended_nodes

def mark_outliers(data, m=2):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    # Return a mask rather than list
    return s < m

