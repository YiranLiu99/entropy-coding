import random
import sys
from collections import deque
import networkx as nx
from bitarray import bitarray


# recursively building the Shannon-Fano tree
def build_sf_tree(freq_list):
    # If len(freq_list) == 1, return the only element in freq_list,
    # indicating that a leaf node in the tree has been reached.
    if len(freq_list) == 1:
        return freq_list[0][0]

    total_freq = sum([item[1] for item in freq_list])
    cumulative_freq = 0
    split_index = 0

    # Accumulate frequencies(cumulative_freq) from the beginning
    # until the accumulated value surpasses half of the total sum(total_freq).
    # This determines the split point(split_index),
    # ensuring that the sum of frequencies in the two resulting sub-lists is as close as possible.
    for i, (symbol, freq) in enumerate(freq_list):
        cumulative_freq += freq
        if cumulative_freq >= total_freq / 2:
            split_index = i
            break

    left_branch = build_sf_tree(freq_list[:split_index + 1])
    right_branch = build_sf_tree(freq_list[split_index + 1:])

    return left_branch, right_branch


# build networkx graph and get code dict using Shannon-Fano tree root
def build_sf_graph(root, frequency_dict):
    global_node_id = 1
    graph = nx.DiGraph()
    code_dict = {}
    queue = deque([(None, root, "", global_node_id)])  # (parent_node, current_node, parent_code, current_node_id)
    graph.add_node(global_node_id, frequency=0, symbol=None)
    while queue:
        parent_node, current_node, parent_code, current_node_id = queue.popleft()
        if isinstance(current_node, tuple):
            left, right = current_node
            global_node_id += 1
            left_node_id = global_node_id
            global_node_id += 1
            right_node_id = global_node_id
            graph.add_node(left_node_id, frequency=0, symbol=None)
            graph.add_node(right_node_id, frequency=0, symbol=None)
            graph.add_edge(current_node_id, left_node_id, label="0")
            graph.add_edge(current_node_id, right_node_id, label="1")
            queue.append((current_node, left, parent_code + "0", left_node_id))
            queue.append((current_node, right, parent_code + "1", right_node_id))
        else:
            code_dict[current_node] = parent_code
            graph.nodes[current_node_id]['frequency'] = frequency_dict[current_node]
            graph.nodes[current_node_id]['symbol'] = current_node

    update_frequency_recursive(graph, 1)
    set_label_recursive(graph, 1)
    return graph, code_dict


# Update frequency of each node in the graph recursively
# The frequency of a node is the sum of the frequencies of its two children.
def update_frequency_recursive(G, node):
    if G.out_degree(node) == 0:
        return G.nodes[node]['frequency']
    children = list(G.successors(node))
    frequency_sum = sum(update_frequency_recursive(G, child) for child in children)
    G.nodes[node]['frequency'] = frequency_sum
    return frequency_sum


# Set label of each node in the graph recursively. The label of a node is [symbol, frequency].
def set_label_recursive(G, node):
    frequency = G.nodes[node]['frequency']
    symbol = G.nodes[node]['symbol']
    G.nodes[node]['label'] = f"[{symbol},{frequency}]"
    for child in G.successors(node):
        set_label_recursive(G, child)


def build_sorted_frequency_dict(data):
    frequency_dict = {item: data.count(item) for item in set(data)}
    sorted_freq = sorted(frequency_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_freq, frequency_dict


def encode_data(data, code_dict):
    encoded_data = bitarray()
    for symbol in data:
        encoded_data += bitarray(code_dict[symbol])
    return encoded_data

# return frequency_dict, sf_tree_root, sf_tree_root_id, sf_graph, sf_code_dict, encoded_data
def sf_compress_data(data):
    sorted_freq_list, frequency_dict = build_sorted_frequency_dict(data)
    sf_tree_root = build_sf_tree(sorted_freq_list)
    sf_graph, sf_code_dict = build_sf_graph(sf_tree_root, frequency_dict)
    encoded_data = encode_data(data, sf_code_dict)
    sf_tree_root_id = 1
    return frequency_dict, sf_tree_root, sf_tree_root_id, sf_graph, sf_code_dict, encoded_data


def decompress(encoded_data, sf_tree_graph, sf_tree_root_id):
    decoded_symbols = []
    current_node_id = sf_tree_root_id
    current_bits = bitarray()

    for bit in encoded_data:
        current_bits.append(bit)
        children = list(sf_tree_graph.successors(current_node_id))
        if bit == 1:
            label_to_find = "1"
        else:  # bit == 0
            label_to_find = "0"
        for child in children:
            edge_label = sf_tree_graph.get_edge_data(current_node_id, child).get('label')
            if edge_label == label_to_find:
                current_node_id = child
                break
        if sf_tree_graph.nodes[current_node_id]['symbol'] is not None:
            decoded_symbols.append(sf_tree_graph.nodes[current_node_id]['symbol'])
            current_node_id = sf_tree_root_id
            current_bits = bitarray()

    return decoded_symbols


if __name__ == '__main__':
    length = 10000
    original_data = [random.randint(0, 255) for _ in range(length)]

    frequency_dict, sf_tree_root, sf_tree_root_id, sf_graph, sf_code_dict, encoded_data = sf_compress_data(original_data)

    # print(original_data)
    # print(encoded_data)

    print(frequency_dict)
    print(sf_tree_root)
    print(nx.node_link_data(sf_graph))
    print(sf_code_dict)

    print(sys.getsizeof(original_data))
    print(sys.getsizeof(encoded_data))
