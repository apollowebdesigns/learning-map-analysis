import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import seaborn as sns
from app import SUBECT_PREFIX


def compare_graphs(graph_dict, learning_journey_title, original_graph=None, figsize=(12, 8), node_size=300, font_size=8, subject_prefix="en"):
    """
    Compare multiple NetworkX graphs by overlaying them on a single plot.
    If an original graph is provided, it will be displayed in black.
    Node names are modified to remove the Wikipedia URL prefix.
    
    Parameters:
    graph_dict (dict): A dictionary where keys are graph names and values are NetworkX graph objects.
    learning_journey_title (str): Title of the learning journey for the plot.
    original_graph (nx.Graph, optional): The original graph to be displayed in black. If None, no original graph is shown.
    figsize (tuple): Figure size (width, height) in inches.
    node_size (int): Size of nodes in the graph.
    font_size (int): Font size for node labels.
    subject_prefix (str): The language prefix for Wikipedia URLs (default is "en").
    
    Returns:
    fig, ax: The figure and axis objects for further customisation if needed.
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    def rename_node(node_name):
        return node_name.replace(f"https://{SUBECT_PREFIX}.wikipedia.org/wiki/", "")
    
    # Rename nodes in all graphs in graph_dict and original_graph if provided
    graph_dict = {name: nx.relabel_nodes(G, rename_node) for name, G in graph_dict.items()}
    if original_graph:
        original_graph = nx.relabel_nodes(original_graph, rename_node)
    
    # Create a union of all nodes from all graphs, including the original graph if provided
    all_nodes = set()
    for G in graph_dict.values():
        all_nodes.update(G.nodes())
    if original_graph:
        all_nodes.update(original_graph.nodes())
    
    # Create a union graph to compute a common layout
    union_graph = nx.Graph()
    union_graph.add_nodes_from(all_nodes)
    pos = nx.spring_layout(union_graph, k=1.5, iterations=50)
    
    # Draw the original graph in black if provided
    if original_graph:
        nx.draw_networkx_nodes(original_graph, pos, ax=ax, node_color='black', 
                               node_size=node_size, alpha=0.6, label='Original', node_shape='s')
        nx.draw_networkx_edges(original_graph, pos, ax=ax, edge_color='black', 
                               alpha=0.3, width=0.5)
    
    # Define a custom color palette
    colors = ['#FF1493', '#00BFFF', '#32CD32', '#FFD700', '#FF4500', '#9370DB']
    shapes = ['^', '>', 'v', '<', 'd', 'p']
    
    for (name, G), color, shape in zip(graph_dict.items(), colors, shapes):
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=color, 
                               node_size=node_size, alpha=0.6, label=name, node_shape=shape)
        
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color=color, 
                               alpha=0.3, width=1)
    
    # Draw labels once (to avoid overlapping labels)
    nx.draw_networkx_labels(union_graph, pos, ax=ax, font_size=font_size)
    
    ax.legend()
    ax.set_title(f"Comparison of Graph Structures for Learning Map: {learning_journey_title}")
    ax.axis('off')
    
    plt.tight_layout()
    if original_graph:
        build_confusion_matrix(original_graph, graph_dict, learning_journey_title)
    return fig, ax

def plot_single_graph(G, learning_journey_title, figsize=(12, 8), node_size=300, font_size=8, subject_prefix="en"):
    """
    Creates a single plot for a given graph.
    
    Parameters:
    G (nx.Graph): NetworkX graph object to be plotted.
    learning_journey_title (str): Title of the learning journey for the plot.
    figsize (tuple): Figure size (width, height) in inches.
    node_size (int): Size of nodes in the graph.
    font_size (int): Font size for node labels.
    subject_prefix (str): The language prefix for Wikipedia URLs (default is "en").
    
    Returns:
    fig, ax: The figure and axis objects for further customisation if needed.
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    def rename_node(node_name):
        return node_name.replace(f"https://{subject_prefix}.wikipedia.org/wiki/", "")
    
    # Rename nodes in the graph
    G = nx.relabel_nodes(G, rename_node)
    
    # Use a spring layout for node positioning
    pos = nx.spring_layout(G, k=1.5, iterations=50)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_size, alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.4, width=1)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=font_size)
    
    ax.set_title(f"Learning Map: {learning_journey_title}")
    ax.axis('off')
    
    plt.tight_layout()
    
    return fig, ax

def build_confusion_matrix(original_graph, graph_dict, learning_journey_title):
    # Get all unique nodes from all graphs
    all_nodes = set(original_graph.nodes())
    for graph in graph_dict.values():
        all_nodes.update(graph.nodes())
    all_nodes = sorted(list(all_nodes))

    # Create a matrix to store node presence
    graphs = [original_graph] + list(graph_dict.values())
    graph_names = ['Original'] + list(graph_dict.keys())
    node_presence = np.zeros((len(graphs), len(all_nodes)), dtype=int)

    # Fill the node presence matrix
    for i, graph in enumerate(graphs):
        for j, node in enumerate(all_nodes):
            if node in graph.nodes():
                node_presence[i, j] = 1

    # Plot the node presence matrix
    plt.figure(figsize=(12, 8))
    sns.heatmap(node_presence, annot=True, fmt='d', cmap='Blues',
                xticklabels=[i.replace("_", " ").capitalize().replace(" communities", "") for i in all_nodes],
                yticklabels=[j.replace("_", " ").capitalize().replace(" communities", "") for j in graph_names])
    plt.title(f"Node Presence Matrix for Learning Map: {learning_journey_title}")
    plt.xlabel('Nodes')
    plt.ylabel('Graphs')
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()

    # Calculate and display coverage statistics
    coverage = node_presence.sum(axis=1) / len(all_nodes) * 100
    print("\nNode Coverage Statistics:")
    for name, cov in zip(graph_names, coverage):
        print(f"{name}: {cov:.2f}% of nodes covered")

    # Calculate and display similarity matrix
    similarity_matrix = np.zeros((len(graphs), len(graphs)))
    for i in range(len(graphs)):
        for j in range(len(graphs)):
            similarity = np.sum(node_presence[i] == node_presence[j]) / len(all_nodes) * 100
            similarity_matrix[i, j] = similarity

    plt.figure(figsize=(7, 6))
    sns.heatmap(similarity_matrix, annot=True, fmt='.2f', cmap='YlGnBu',
                xticklabels=[i.replace("_", " ").capitalize().replace(" communities", "") for i in graph_names], 
                yticklabels=[j.replace("_", " ").capitalize().replace(" communities", "") for j in graph_names])
    plt.title(f"Graph Similarity Matrix (%) for Learning Map: {learning_journey_title}")
    plt.tight_layout()
    plt.show()


def direct_compare_graphs(names, graphs, figsize=(12, 8), node_size=300, font_size=8):
    """
    Compare multiple NetworkX graphs by overlaying them on a single plot.
    
    Parameters:
    graph_dict (dict): A dictionary where keys are graph names and values are NetworkX graph objects.
    figsize (tuple): Figure size (width, height) in inches.
    node_size (int): Size of nodes in the graph.
    font_size (int): Font size for node labels.
    
    Returns:
    fig, ax: The figure and axis objects for further customisation if needed.
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create a union of all nodes from all graphs
    all_nodes = set()
    
    # Create a union graph to compute a common layout
    union_graph = nx.Graph()
    union_graph.add_nodes_from(all_nodes)
    pos = nx.spring_layout(union_graph)
    
    # Define a custom color palette
    colors = ['#FF1493', '#00BFFF', '#32CD32', '#FFD700', '#FF4500', '#9370DB']
    shapes = ['^', '>', 'v', '<', 'd', 'p']
    
    for name, G, color, shape in zip(names, graphs, colors, shapes):
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=color, 
                               node_size=node_size, alpha=0.6, label=name, node_shape=shape)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color=color, 
                               alpha=0.3, width=1)
    
    # Draw labels once (to avoid overlapping labels)
    nx.draw_networkx_labels(union_graph, pos, ax=ax, font_size=font_size)
    
    ax.legend()
    ax.set_title("Comparison of Graph Structures")
    ax.axis('off')
    
    plt.tight_layout()
    return fig, ax

class GraphBuilder:
    def __init__(self, number_of_plots):
        self.fig, axes = plt.subplots(number_of_plots, 1, figsize=(12, 7 * number_of_plots))
        self.axes = axes if number_of_plots > 1 else [axes]
        self.current_plot = 0

    def plot_graph(self, df, title=None):
        if self.current_plot >= len(self.axes):
            raise ValueError("All available plots have been used.")

        ax = self.axes[self.current_plot]
        
        # Drop unnecessary rows
        plot_df = df.drop(['macro avg', 'weighted avg'], errors='ignore')

        # Plotting
        plot_df[['precision', 'recall', 'accuracy', 'f1_score']].plot(kind='bar', ax=ax)

        ax.set_title(title or 'Classification Report Metrics by Class')
        ax.set_ylabel('Score')
        ax.set_xlabel('Class')
        ax.set_xticklabels([label.get_text().replace("_", " ").capitalize() for label in ax.get_xticklabels()], rotation=45, ha='right')
        ax.grid(axis='y')
        ax.legend(loc='upper right')

        self.current_plot += 1

    def show_plots(self):
        plt.tight_layout()
        plt.show()