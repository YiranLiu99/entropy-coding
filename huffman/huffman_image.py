import pickle
from PIL import Image
import networkx
from huffman import huffman_coding
from helper.image_helper import read_image, add_padding, remove_padding
from helper import visualizer


def to_decompressed_image(compressed_image_path):
    with open(compressed_image_path, 'rb') as file:
        compressed_data = pickle.load(file)
        try:
            compress_version = compressed_data['compress_version']
        except KeyError:
            raise Exception('Invalid compressed image huffman data.')
        if compress_version != 'huf_img':
            raise Exception('Invalid compressed image huffman data.')
        huffman_tree = compressed_data['huffman_tree_structure']
        huffman_tree_root = compressed_data['huffman_tree_root']
        image_width = compressed_data['image_width']
        image_height = compressed_data['image_height']
        image_name = compressed_data['image_name']
        image_extension = compressed_data['image_extension']
        encoded_data = remove_padding(compressed_data['data'])

        huffman_tree_graph = networkx.node_link_graph(huffman_tree)
        decoded_symbols = huffman_coding.decompress(encoded_data, huffman_tree_graph, huffman_tree_root)

        img = Image.new('L', (image_width, image_height))
        img.putdata(decoded_symbols)
        return img, image_name + image_extension


def save_decompressed_image(compressed_image_path, output_image_folder_path):
    img, img_name = to_decompressed_image(compressed_image_path)
    img.save(output_image_folder_path + 'huffman_decompressed_' + img_name)


class HuffmanImage:
    def __init__(self, file):
        self.huffman_tree_graph = None
        self.huffman_codes_dict = None
        self.huffman_tree_root_node = None
        self.frequencies = None
        self.encoded_data = None
        self.huffman_dict_graph = None
        self.root_node_id = None
        self.img, self.pixel_data, self.file_name, self.file_extension = read_image(file)

    def to_compressed_image(self):
        # first 8 bits in padded_data represents padding info, how many bits have been added.
        padded_data = add_padding(self.encoded_data)
        # Convert bitarray to bytes
        compressed_bytes = padded_data.tobytes()
        image_width = self.img.width
        image_height = self.img.height
        huffman_tree = networkx.readwrite.json_graph.node_link_data(self.huffman_dict_graph)
        compressed_data = {
            'huffman_tree_structure': huffman_tree,  # Include the serialized Huffman tree(dict type)
            'huffman_tree_root': self.root_node_id,  # Include the root node of the Huffman tree(int type)
            'image_width': image_width,  # (int type)
            'image_height': image_height,  # (int type)
            'compress_version': 'huf_img',  # (str type)
            'image_name': self.file_name,  # (str type)
            'image_extension': self.file_extension,  # (str type)
            'data': compressed_bytes  # Include the converted bytes. Including padding and padding info.(bytes type)
        }
        # self.show_compressed_info(compressed_data)
        compressed_data_bytes = pickle.dumps(compressed_data)
        return compressed_data_bytes

    # set the huffman tree graph, huffman codes dict, huffman tree root node, frequencies, encoded data
    def process_image(self):
        (self.frequencies,
         self.huffman_tree_root_node,
         self.huffman_codes_dict,
         self.huffman_tree_graph,
         self.encoded_data,
         self.huffman_dict_graph,
         self.root_node_id) = huffman_coding.compress_data(self.pixel_data)

    # convert networkx graph to plotly figure
    def visual_huffman_tree_image(self):
        dict_graph, root = huffman_coding.generate_dict_graph(self.huffman_tree_root_node)
        return visualizer.visualize_tree(dict_graph)

    def show_compressed_info(self, compressed_data):
        print("Compress Version:", compressed_data['compress_version'])
        print("Image name:", compressed_data['image_name'] + compressed_data['image_extension'])
        print("Image width:", compressed_data['image_width'])
        print("Image height:", compressed_data['image_height'])
        print("Huffman tree:", compressed_data['huffman_tree_structure'])
        print("Huffman tree root:", compressed_data['huffman_tree_root'])
        print("Frequency dict:", self.frequencies)
        print("Huffman codes dict:", self.huffman_codes_dict)
