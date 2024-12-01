import json
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
import matplotlib.pyplot as plt
from urllib.parse import unquote
import pandas as pd

class Network:
    def __init__(self, filename, n_nodes_to_keep, expected_learning_journey, already_learned=[], ignore_list=[], start_page=None) -> None:
        self.filename = filename
        self.n_nodes_to_keep = n_nodes_to_keep
        self._load_network()
        self.graph = nx.DiGraph()
        self.expected_learning_journey = expected_learning_journey
        self.already_learned = already_learned
        self.ignore_list = ignore_list
        self.start_page = start_page

        for page in self.network_data:
            self.graph.add_node(unquote(page["title"]))
            for link in page["links"]:
                if link not in already_learned:
                    self.graph.add_edge(unquote(page["title"]), unquote(link))
        
        data = nx.node_link_data(self.graph)
        
        print("Writing data to JSON file...")
        sp = start_page.replace("https://en.wikipedia.org/wiki/", "")
        with open(f'{sp}_visualisation_data_graph.json', 'w') as f:
            print("Written successfully")
            json.dump(data, f)
            
        try:
            with open(f'static/{sp}_visualisation_data_graph.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print("Failed to save to static website folder")
            print(f"Error: {e}")
            
        print("Data written to JSON file.")
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 10))
        
        self.evaluation_data = {'algorithm': [], 'evaluation': []}
        
        self.create_learning_journey(nx.pagerank, axes[0, 0])
        # self.create_learning_journey(nx.eigenvector_centrality, axes[0, 1])
        # self.create_learning_journey(nx.closeness_centrality, axes[1, 0])
        
        plt.tight_layout()
        plt.savefig('foo.png', bbox_inches='tight')
        # plt.show()
        
        print(pd.DataFrame(self.evaluation_data))
        
    def create_learning_journey(self, algorithm, ax):
        ranked = algorithm(self.graph)
        
        self.top_n_nodes = sorted(ranked, key=ranked.get, reverse=True)[:self.n_nodes_to_keep]
        print(f"Top nodes by {algorithm}:")
        for node in self.top_n_nodes:
            print(f"Node: {node}, {algorithm}: {ranked[node]}")

        frame_n_nodes = pd.DataFrame({
            "nodes": self.top_n_nodes,
            "rank": [ranked[node] for node in self.top_n_nodes]
        })

        # Create a subgraph with the top n nodes
        top_n_subgraph = self.graph.subgraph(self.top_n_nodes)

        f, nax = plt.subplots(figsize=(15, 15))
        
        # Draw the subgraph on the specified axis
        pos = nx.spring_layout(top_n_subgraph)
        nx.draw(top_n_subgraph, pos, ax=nax, with_labels=True, node_size=500, node_color="lightblue", 
                font_size=10, font_weight="bold", arrows=True)

        edge_labels = nx.get_edge_attributes(top_n_subgraph, "weight")
        nx.draw_networkx_edge_labels(top_n_subgraph, pos, edge_labels=edge_labels, ax=nax)

        nax.set_title(f"Top {self.n_nodes_to_keep} {algorithm.__name__} Nodes in Wikipedia Network")
        nax.axis("off")
        
        learning_journey = set([i.replace(" ", "_") for i in self.top_n_nodes])
        print("Learning Journey:", learning_journey)
        
        self.evaluation_data["algorithm"].append(f"{algorithm}")
        self.evaluation_data["evaluation"].append(self.evaluate_learning_journey(learning_journey))
        
        self.plot_rankings(frame_n_nodes, algorithm.__name__, ax)
        
        self.top_node = None
        
        for step in learning_journey:
            # print("Debugging:")
            # print(learning_journey)
            # print(self.expected_learning_journey)
            if step in self.expected_learning_journey and step not in self.already_learned:
                self.top_node = step
                break

    def _load_network(self):
        with open(self.filename, "r") as f:
            self.network_data = json.load(f)

    def plot_rankings(self, frame_n_nodes, algorithm, a):        
        frame_n_nodes['nodes'] = frame_n_nodes['nodes'].str.replace('https://en.wikipedia.org/wiki/', '')
        a.bar(frame_n_nodes['nodes'], frame_n_nodes['rank'])
        a.set_xticks(frame_n_nodes['nodes'])
        a.set_xticklabels(frame_n_nodes['nodes'], rotation=90)

        # Add labels and title to the subplot
        a.set_xlabel('nodes')
        a.set_ylabel('rank')
        a.set_title(f'Bar Chart of nodes vs. {algorithm}')
        
    def evaluate_learning_journey(self, actual):
        # This allows for the number of nodes to cover what is learned, therefore always increasing in size
        total_learned_nodes = actual.union(set(self.already_learned))
        return len([i for i in self.expected_learning_journey if i in total_learned_nodes]) / len(self.expected_learning_journey)


    def build_postgresql_community_subgraph(self, graph):
        start_page = self.start_page
        
        # Detect communities using the greedy modularity communities algorithm
        communities = list(greedy_modularity_communities(graph))

        selected_community = None
        for community in communities:
            if start_page in community:
                selected_community = community
                break
        
        if selected_community is None:
            raise ValueError(f"{selected_community} page not found in any community")

        # Filter nodes to keep only those in the community
        selected_community = set(selected_community)
        
        # Prepare the list for storing rows
        rows = []
        
        # Add shortest path distance to each node in the PostgreSQL community
        for page in selected_community:
            try:
                # Calculate the shortest path length from the start page
                shortest_path_length = nx.shortest_path_length(graph, source=start_page, target=page)
            except nx.NetworkXNoPath:
                # Handle cases where there is no path between nodes
                shortest_path_length = float('inf')
            
            # Add each page and its shortest path length to the rows list
            rows.append({'Page': page, 'shortest_path': shortest_path_length})
        
        # Convert the list of rows to a DataFrame
        pd.DataFrame(rows)
        
        # Create a subgraph containing only the nodes in the community
        subgraph = graph.subgraph(selected_community).copy()
        
        return subgraph
