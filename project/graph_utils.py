import cfpq_data as cfpq
from networkx.drawing.nx_pydot import to_pydot
from dataclasses import dataclass

@dataclass
class GraphInfo:
    nodes_number: int
    edges_number: int
    labels: list

def get_graph_info(name):
    graph_path = cfpq.download(name)
    graph = cfpq.graph_from_csv(graph_path)
    n_nodes = graph.number_of_nodes()
    n_edges = graph.number_of_edges()
    labels = cfpq.get_sorted_labels(graph)
    return GraphInfo(n_nodes, n_edges, labels)

def save_two_cycles_graph(fst_cycle_node_number, snd_cycle_node_number, nodes, path):
    graph = cfpq.labeled_two_cycles_graph(m = fst_cycle_node_number,n = snd_cycle_node_number,labels = nodes)
    dot_graph = to_pydot(graph)
    dot_graph.write_raw(path)
