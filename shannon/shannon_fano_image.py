import pickle
from PIL import Image
import networkx
from shannon import shannon_fano_coding
from helper.image_helper import read_image, add_padding, remove_padding
from helper import visualizer


def to_decompressed_image(compressed_image_path):
    with open(compressed_image_path, 'rb') as file:
        compressed_data = pickle.load(file)
        try:
            compress_version = compressed_data['compress_version']
        except KeyError:
            raise Exception('Invalid compressed image shannon fano data.')
        if compress_version != 'sf_img':
            raise Exception('Invalid compressed image shannon fano data.')
        sf_tree = compressed_data['sf_tree_structure']
        sf_tree_root = compressed_data['sf_tree_root']
        image_width = compressed_data['image_width']
        image_height = compressed_data['image_height']
        image_name = compressed_data['image_name']
        image_extension = compressed_data['image_extension']
        encoded_data = remove_padding(compressed_data['data'])

        sf_tree_graph = networkx.node_link_graph(sf_tree)
        decoded_symbols = shannon_fano_coding.decompress(encoded_data, sf_tree_graph, sf_tree_root)

        img = Image.new('L', (image_width, image_height))
        img.putdata(decoded_symbols)
        return img, image_name + image_extension


def save_decompressed_image(compressed_image_path, output_image_folder_path):
    img, img_name = to_decompressed_image(compressed_image_path)
    img.save(output_image_folder_path + 'sf_decompressed_' + img_name)


class ShannonFanoImage:
    def __init__(self, file):
        self.sf_tree_graph = None
        self.sf_code_dict = None
        self.sf_tree_root = None
        self.frequencies = None
        self.encoded_data = None
        self.root_node_id = None
        self.img, self.pixel_data, self.file_name, self.file_extension = read_image(file)

    def process_image(self):
        (self.frequencies,
         self.sf_tree_root,
         self.root_node_id,
         self.sf_tree_graph,
         self.sf_code_dict,
         self.encoded_data) = shannon_fano_coding.sf_compress_data(self.pixel_data)

    def to_compressed_image(self):
        # first 8 bits in padded_data represents padding info, how many bits have been added.
        padded_data = add_padding(self.encoded_data)
        # Convert bitarray to bytes
        compressed_bytes = padded_data.tobytes()
        image_width = self.img.width
        image_height = self.img.height
        sf_tree = networkx.readwrite.json_graph.node_link_data(self.sf_tree_graph)
        compressed_data = {
            'sf_tree_structure': sf_tree,  # Include the serialized Huffman tree(dict type)
            'sf_tree_root': self.root_node_id,  # Include the root node of the Huffman tree(int type)
            'image_width': image_width,  # (int type)
            'image_height': image_height,  # (int type)
            'compress_version': 'sf_img',  # (str type)
            'image_name': self.file_name,  # (str type)
            'image_extension': self.file_extension,  # (str type)
            'data': compressed_bytes  # Include the converted bytes. Including padding and padding info.(bytes type)
        }
        # self.show_compressed_info(compressed_data)
        compressed_data_bytes = pickle.dumps(compressed_data)
        return compressed_data_bytes

    def show_compressed_info(self, compressed_data):
        print("Compress Version:", compressed_data['compress_version'])
        print("Image name:", compressed_data['image_name'] + compressed_data['image_extension'])
        print("Image width:", compressed_data['image_width'])
        print("Image height:", compressed_data['image_height'])
        print("Shannon Fano tree:", compressed_data['sf_tree_structure'])
        print("Shannon Fano tree root:", compressed_data['sf_tree_root'])
        print("Frequency dict:", self.frequencies)
        print("Shannon Fano codes dict:", self.sf_code_dict)


if __name__ == '__main__':
    image_path = "../image_sample/gray_test.bmp"

    print('Compressing the image...')
    sf_image = ShannonFanoImage(image_path)
    sf_image.process_image()

    print(networkx.readwrite.json_graph.node_link_data(sf_image.sf_tree_graph))

    # sf_tree_fig = visualizer.visualize_tree(sf_image.sf_tree_graph)

    compressed_data_bytes = sf_image.to_compressed_image()
    decoded_symbols = shannon_fano_coding.decompress(sf_image.encoded_data, sf_image.sf_tree_graph,
                                                     sf_image.root_node_id)
    img = Image.new('L', (sf_image.img.width, sf_image.img.height))
    img.putdata(decoded_symbols)
    img.save("test.bmp")

    # Convert Figure object to JSON using plotly.io.to_json
    # huffman_tree_fig_json = pio.to_json(huffman_tree_fig)
    # compressed_data_bytes = huff_image.to_compressed_image()
    # frequency_dict = huff_image.frequencies
    # huffman_codes_dict = huff_image.huffman_codes_dict
    # frequency_dict_json = json.dumps(frequency_dict)
    # huffman_codes_dict_json = json.dumps(huffman_codes_dict)
