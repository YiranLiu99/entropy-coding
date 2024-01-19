import os
import pickle
import time
from tkinter import filedialog

import networkx
from bitarray import bitarray
from shannon import shannon_fano_coding


def read_file_to_bytearray(file_path):
    data_in_bytearray = bytearray()
    with open(file_path, 'rb') as file:
        while True:
            byte_data = file.read(1)
            if not byte_data:
                break  # end of file
            data_in_bytearray.append(byte_data[0])

    file_name, file_extension = os.path.splitext(os.path.basename(file_path))
    return data_in_bytearray, file_name, file_extension


def write_compressed_data(compressed_data, save_dir_path, file_name):
    save_file_full_name = 'sf_compressed_' + file_name + '.bin'
    save_file_path = save_dir_path + '/' + save_file_full_name
    with open(save_file_path, 'wb') as file:
        file.write(compressed_data)


def write_decompressed_data(decompressed_data, save_dir_path, file_name, file_extension):
    save_file_full_name = 'sf_decompressed_' + file_name + file_extension
    save_file_path = save_dir_path + '/' + save_file_full_name
    with open(save_file_path, 'wb') as file:
        file.write(decompressed_data)


def remove_padding(padded_data):
    bit_array = bitarray()
    bit_array.frombytes(padded_data)
    padded_info = int(bit_array[:8].to01(), 2)
    bit_array = bit_array[8:]
    encoded_data = bit_array[:-padded_info]
    return encoded_data


def to_decompressed_data(compressed_data_path):
    with open(compressed_data_path, 'rb') as file:
        compressed_data = pickle.load(file)
        try:
            compress_version = compressed_data['compress_version']
        except KeyError:
            raise Exception('Invalid compressed shannon fano data.')
        if compress_version != 'sf_bin':
            raise Exception('Invalid compressed shannon fano data.')
        sf_tree = compressed_data['sf_tree_structure']
        sf_tree_root = compressed_data['sf_tree_root']
        file_name = compressed_data['file_name']
        file_extension = compressed_data['file_extension']
        encoded_data = remove_padding(compressed_data['data'])

        sf_tree_graph = networkx.node_link_graph(sf_tree)
        decoded_symbols = shannon_fano_coding.decompress(encoded_data, sf_tree_graph, sf_tree_root)
        decoded_symbols_bytes = bytes(decoded_symbols)

        return decoded_symbols_bytes, file_name, file_extension


class ShannonFanoBinary:
    def __init__(self, file_path):
        self.sf_tree_graph = None
        self.sf_code_dict = None
        self.sf_tree_root = None
        self.frequencies = None
        self.encoded_data = None
        self.root_node_id = None
        self.data, self.file_name, self.file_extension = read_file_to_bytearray(file_path)

    def process_data(self):
        (self.frequencies,
         self.sf_tree_root,
         self.root_node_id,
         self.sf_tree_graph,
         self.sf_code_dict,
         self.encoded_data) = shannon_fano_coding.sf_compress_data(self.data)

    def add_padding(self):
        # The double % 8 is used to ensure that pad_bits is always in the range of 0 to 7,
        # representing the number of bits needed to reach the next multiple of 8.
        num_pad_bits = (8 - len(self.encoded_data) % 8) % 8
        for i in range(num_pad_bits):
            self.encoded_data += bitarray('0')
        # Add this padding information to the beginning of compressed data
        # to keep track of how many bits have been added.
        # padding_info: exp. num_pad_bits=4 -> 0b100 -> 100 -> 00000100
        # First 8 bits of compressed data are padding info, showing the number of padding bits added.
        padding_info = bin(num_pad_bits)[2:].zfill(8)
        padded_data = bitarray(padding_info) + self.encoded_data
        return padded_data

    def to_compressed_data(self):
        # first 8 bits in padded_data represents padding info, how many bits have been added.
        padded_data = self.add_padding()
        # Convert bitarray to bytes
        compressed_bytes = padded_data.tobytes()
        sf_tree = networkx.readwrite.json_graph.node_link_data(self.sf_tree_graph)
        compressed_data = {
            'sf_tree_structure': sf_tree,  # Include the serialized Huffman tree(dict type)
            'sf_tree_root': self.root_node_id,  # Include the root node of the Huffman tree(int type)
            'compress_version': 'sf_bin',  # (str type)
            'file_name': self.file_name,  # (str type)
            'file_extension': self.file_extension,  # (str type)
            'data': compressed_bytes  # Include the converted bytes. Including padding and padding info.(bytes type)
        }
        compressed_data_bytes = pickle.dumps(compressed_data)
        return compressed_data_bytes


if __name__ == '__main__':
    # file_path = '../sample/test/video.mp4'

    file_path = filedialog.askopenfilename()

    file_dir_path = os.path.dirname(file_path)
    file_name, file_extension = os.path.splitext(os.path.basename(file_path))

    save_dir_path = file_dir_path

    save_compressed_file_path = save_dir_path + '/sf_compressed_' + file_name + '.bin'
    # save_decompressed_file_path = save_dir_path + '/sf_decompressed_' + file_name + file_extension

    start_time = time.time()
    print('Compressing the file ' + file_path)
    sf_binary = ShannonFanoBinary(file_path)
    sf_binary.process_data()
    compressed_data_bytes = sf_binary.to_compressed_data()
    write_compressed_data(compressed_data_bytes, save_dir_path, sf_binary.file_name)
    compress_time = time.time() - start_time

    start_time = time.time()
    print('Decompressing the file ' + save_compressed_file_path)
    decompressed_data_bytes, file_name, file_extension = to_decompressed_data(save_compressed_file_path)
    write_decompressed_data(decompressed_data_bytes, save_dir_path, file_name, file_extension)
    decompress_time = time.time() - start_time


    # Calculate compression ratio
    uncompressed_size = os.path.getsize(file_path)
    compressed_size = os.path.getsize(save_compressed_file_path)
    compression_ratio = uncompressed_size / compressed_size
    print(f'Uncompressed size: {uncompressed_size/1024/1024:.3f} MB')
    print(f'Compressed size: {compressed_size/1024/1024:.3f} MB')
    print(f'Compression ratio: {compression_ratio}')
    print(f'Compression time: {compress_time:.3f} s')
    print(f'Decompression time: {decompress_time:.3f} s')

