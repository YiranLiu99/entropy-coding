from collections import defaultdict
import heapq
from bitarray import bitarray
from huffman.huffman_node import HuffmanNode as HuffmanNode
import networkx as nx
from collections import deque


# count the frequency of each symbol in the data
def calculate_frequencies(data):
    frequencies = defaultdict(int)
    for symbol in data:
        frequencies[symbol] += 1
    return frequencies


def build_huffman_tree(frequencies):
    cnt_node = 1
    node_heap = []
    for symbol, frequency in frequencies.items():
        node = HuffmanNode(node_id=cnt_node, symbol=symbol, frequency=frequency)
        heapq.heappush(node_heap, node)
        cnt_node += 1

    while len(node_heap) > 1:
        # pop two minimum frequency nodes
        left_node = heapq.heappop(node_heap)
        right_node = heapq.heappop(node_heap)
        # Create a new node merged from left_node and right_node
        new_node = HuffmanNode(node_id=cnt_node, symbol=None, frequency=left_node.frequency + right_node.frequency,
                               left=left_node, right=right_node)
        heapq.heappush(node_heap, new_node)
        cnt_node += 1
    return node_heap[0]


def generate_huffman_codes_dict(node, current_code="", code_dict=None):
    if code_dict is None:
        code_dict = {}
    # if this node is leaf(has symbol)
    if node.symbol is not None:
        code_dict[node.symbol] = current_code
    if node.left is not None:
        generate_huffman_codes_dict(node.left, current_code + "0", code_dict)
    if node.right is not None:
        generate_huffman_codes_dict(node.right, current_code + "1", code_dict)
    return code_dict


# generate a graph of the huffman tree, return a networkx graph. Each node is a HuffmanNode object.
def generate_huffman_tree_graph(root):
    G = nx.DiGraph()
    queue = deque([(root, None, 0)])  # (node, parent, level)
    while queue:
        current_node, parent, level = queue.popleft()
        G.add_node(current_node)
        if parent is not None:
            G.add_edge(parent, current_node)
        if current_node.left:
            queue.append((current_node.left, current_node, level + 1))
        if current_node.right:
            queue.append((current_node.right, current_node, level + 1))
    return G

# generate a graph of the huffman tree, return a networkx graph.
# Each node is a node with node_id,frequency, label, symbol, left_child_node_id, right_child_node_id.
def generate_dict_graph(root):
    G = nx.DiGraph()
    queue = deque([(root, None, 0)])  # (node, parent, level)
    root_node_id = root.node_id
    while queue:
        current_node, parent, level = queue.popleft()
        G.add_node(current_node.node_id, node_id=current_node.node_id,
                   frequency=current_node.frequency, label=current_node.label,
                   symbol=current_node.symbol, left_child_node_id=current_node.left_child_node_id,
                   right_child_node_id=current_node.right_child_node_id)
        if parent is not None:
            G.add_edge(parent.node_id, current_node.node_id)
        if current_node.left:
            queue.append((current_node.left, current_node, level + 1))
        if current_node.right:
            queue.append((current_node.right, current_node, level + 1))
    return G, root_node_id


def encode_data(data, code_dict):
    encoded_data = bitarray()
    for symbol in data:
        encoded_data += bitarray(code_dict[symbol])
    return encoded_data


def compress_data(data):
    frequencies = calculate_frequencies(data)
    huffman_tree_root_node = build_huffman_tree(frequencies)
    huffman_codes_dict = generate_huffman_codes_dict(huffman_tree_root_node)
    huffman_tree_graph = generate_huffman_tree_graph(huffman_tree_root_node)
    huffman_dict_graph, root_node_id = generate_dict_graph(huffman_tree_root_node)
    encoded_data = encode_data(data, huffman_codes_dict)
    return frequencies, huffman_tree_root_node, huffman_codes_dict, huffman_tree_graph, encoded_data, huffman_dict_graph, root_node_id


# The codes are uniquely decodable, meaning that no code is a prefix of another code.
def decompress(encoded_data, huffman_dict_tree_graph, huffman_tree_root_id):
    decoded_symbols = []
    current_node_id = huffman_tree_root_id
    current_bits = bitarray()

    for bit in encoded_data:
        current_bits.append(bit)
        if bit == 1:
            child_node_id = huffman_dict_tree_graph.nodes[current_node_id]['right_child_node_id']
        else:  # bit == 0
            child_node_id = huffman_dict_tree_graph.nodes[current_node_id]['left_child_node_id']
        current_node_id = child_node_id
        child_node = huffman_dict_tree_graph.nodes[child_node_id]
        if child_node['symbol'] is not None:
            decoded_symbols.append(child_node['symbol'])
            current_node_id = huffman_tree_root_id
            current_bits = bitarray()

    return decoded_symbols
