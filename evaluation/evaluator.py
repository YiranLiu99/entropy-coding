import json
import os
import time
import matplotlib.pyplot as plt
import PIL
from helper import image_helper
from huffman import huffman_image
from shannon import shannon_fano_image
from shannon import shannon_fano_binary
from huffman import huffman_binary


def evaluate_sf(file_name_list, save_directory):
    compression_ratio_list = []
    compression_time_list = []
    decompression_time_list = []

    for source_file_path in file_name_list:
        source_directory = os.path.dirname(source_file_path)
        file_name = os.path.basename(source_file_path)
        save_file_path = save_directory + file_name
        compressed_file_path = save_directory + 'sf_compressed_' + os.path.splitext(file_name)[0] + '.bin'
        decompressed_file_path = save_directory + 'sf_decompressed_' + file_name

        pil_img = PIL.Image.open(source_file_path)
        pil_img.save(save_file_path)

        print('Shannon Fano Compressing ' + file_name + '...')
        start_time = time.time()

        # # Compress the image and generate tree
        # sf_image = shannon_fano_image.ShannonFanoImage(save_file_path)
        # # Get frequencies, code_dict, tree graph, encoded data
        # sf_image.process_image()
        # # Combine all into compressed data file
        # compressed_data_bytes = sf_image.to_compressed_image()
        # # frequency_dict = sf_image.frequencies
        # # sf_codes_dict = sf_image.sf_code_dict
        #
        # # Save compressed data to a binary file
        # with open(compressed_file_path, 'wb') as file:
        #     file.write(compressed_data_bytes)

        sf_binary = shannon_fano_binary.ShannonFanoBinary(save_file_path)
        sf_binary.process_data()
        compressed_data_bytes = sf_binary.to_compressed_data()
        shannon_fano_binary.write_compressed_data(compressed_data_bytes, save_directory, sf_binary.file_name)

        compress_time = time.time() - start_time

        # Decompress the data
        print('Shannon Fano Decompressing ' + file_name + '...')
        start_time = time.time()
        # img, img_name = shannon_fano_image.to_decompressed_image(compressed_file_path)
        # # Save decompressed data to a file
        # img.save(decompressed_file_path)
        # decompressed_data_bytes, file_name, file_extension = shannon_fano_binary.to_decompressed_data(compressed_file_path)
        # shannon_fano_binary.write_decompressed_data(decompressed_data_bytes, save_directory, file_name, file_extension)
        decompress_time = time.time() - start_time

        # Calculate compression ratio
        uncompressed_size = os.path.getsize(source_file_path)
        compressed_size = os.path.getsize(compressed_file_path)
        compression_ratio = uncompressed_size / compressed_size
        compression_ratio_list.append(compression_ratio)
        compression_time_list.append(compress_time)
        decompression_time_list.append(decompress_time)

        # Print evaluation results
        print(f"Shannon Fano Compression Time: {compress_time:.4f} seconds")
        print(f"Shannon Fano Decompression Time: {decompress_time:.4f} seconds")
        print(f"Shannon Fano Compression Ratio: {compression_ratio:.6f}")
        print("=====================================================================================================")
    return compression_ratio_list, compression_time_list, decompression_time_list


def evaluate_huffman(file_name_list, save_directory):
    compression_ratio_list = []
    compression_time_list = []
    decompression_time_list = []

    for source_file_path in file_name_list:
        source_directory = os.path.dirname(source_file_path)
        file_name = os.path.basename(source_file_path)
        save_file_path = save_directory + file_name
        compressed_file_path = save_directory + 'sf_compressed_' + file_name + '.bin'
        decompressed_file_path = save_directory + 'sf_decompressed_' + file_name

        pil_img = PIL.Image.open(source_file_path)
        pil_img.save(save_file_path)

        print('Huffman Compressing ' + file_name + '...')
        start_time = time.time()

        # Compress the image and generate tree
        huff_image = huffman_image.HuffmanImage(save_file_path)
        # Get frequencies, code_dict, tree graph, encoded data
        huff_image.process_image()
        # Combine all into compressed data file
        compressed_data_bytes = huff_image.to_compressed_image()

        # Save compressed data to a binary file
        with open(compressed_file_path, 'wb') as file:
            file.write(compressed_data_bytes)

        compress_time = time.time() - start_time

        # Decompress the data
        print('Huffman Decompressing ' + file_name + '...')
        start_time = time.time()
        # img, img_name = huffman_image.to_decompressed_image(compressed_file_path)
        #
        # # Save decompressed data to a file
        # img.save(decompressed_file_path)
        decompress_time = time.time() - start_time

        # Calculate compression ratio
        uncompressed_size = os.path.getsize(source_file_path)
        compressed_size = os.path.getsize(compressed_file_path)
        compression_ratio = uncompressed_size / compressed_size
        compression_ratio_list.append(compression_ratio)
        compression_time_list.append(compress_time)
        decompression_time_list.append(decompress_time)

        # Print evaluation results
        print(f"Huffman Compression Time: {compress_time:.4f} seconds")
        print(f"Huffman Decompression Time: {decompress_time:.4f} seconds")
        print(f"Huffman Compression Ratio: {compression_ratio:.6f}")
        print("=====================================================================================================")
    return compression_ratio_list, compression_time_list, decompression_time_list


def analyse_num_symbol_type():
    # Remain data size, change num of symbol type. Compare compression ratio under different num of symbol type
    folder_path = '../sample/evaluation_sample/change_num_symbol_type'
    file_path_list = image_helper.read_images_from_directory(folder_path)
    file_path_list.sort(key=get_number_from_filename)

    (sf_compression_ratio_changing_num_symbol_type_list,
     sf_compression_time_changing_num_symbol_type_list,
     sf_decompression_time_changing_num_symbol_type_list) = evaluate_sf(file_path_list,
                                                                        'image/change_num_symbol_type/sf/')

    (huffman_compression_ratio_changing_num_symbol_type_list,
     huffman_compression_time_changing_num_symbol_type_list,
     huffman_decompression_time_changing_num_symbol_type_list) = evaluate_huffman(file_path_list,
                                                                                  'image/change_num_symbol_type/huffman/')

    num_symbol_type_list = [i for i in range(20, 256, 10)] + [255]
    # Plot the results
    plt.plot(num_symbol_type_list, sf_compression_ratio_changing_num_symbol_type_list, marker='o', label='Shannon-Fano')
    plt.plot(num_symbol_type_list, huffman_compression_ratio_changing_num_symbol_type_list, marker='o', label='Huffman')
    plt.xlabel('Number of Symbol Types')
    plt.ylabel('Compression Ratio')
    plt.title('Shannon-Fano vs. Huffman')
    plt.legend()
    plt.grid(True)
    plt.savefig('image/num_symbol_type.png')
    plt.show()

    # plt.plot(num_symbol_type_list, sf_compression_time_changing_num_symbol_type_list, marker='o', label='Shannon-Fano')
    # plt.plot(num_symbol_type_list, huffman_compression_time_changing_num_symbol_type_list, marker='o', label='Huffman')
    # plt.xlabel('Number of Symbol Types')
    # plt.ylabel('Compression Time (seconds)')
    # plt.title('Shannon-Fano vs. Huffman')
    # plt.legend()
    # plt.grid(True)
    # plt.show()

    # plt.plot(num_symbol_type_list, sf_decompression_time_changing_num_symbol_type_list, marker='o',
    #          label='Shannon-Fano')
    # plt.plot(num_symbol_type_list, huffman_decompression_time_changing_num_symbol_type_list, marker='o',
    #          label='Huffman')
    # plt.xlabel('Number of Symbol Types')
    # plt.ylabel('Decompression Time (seconds)')
    # plt.title('Shannon-Fano vs. Huffman')
    # plt.legend()
    # plt.grid(True)
    # plt.show()


def analyse_data_size():
    # Remain num of symbol type, change data size(num of symbols). Compare compression ratio under different data size
    width_height_list = [(400, 600), (800, 1200), (1200, 1800), (1600, 2400), (2000, 3000), (2400, 3600), (2800, 4200),
                         (3200, 4800), (3600, 5400), (4000, 6000)]
    num_symbol_list = [width * height for width, height in width_height_list]
    num_symbol_list = format_numbers_for_legend(num_symbol_list)
    folder_path = '../sample/evaluation_sample/change_num_symbol'
    file_path_list = image_helper.read_images_from_directory(folder_path)
    file_path_list.sort(key=get_number_from_filename)

    (sf_compression_ratio_changing_data_size_list,
     sf_compression_time_changing_data_size_list,
     sf_decompression_time_changing_data_size_list) = evaluate_sf(file_path_list, 'image/change_num_symbol/sf/')

    (huffman_compression_ratio_changing_data_size_list,
     huffman_compression_time_changing_data_size_list,
     huffman_decompression_time_changing_data_size_list) = evaluate_huffman(file_path_list,
                                                                            'image/change_num_symbol/huffman/')

    # Plot the results
    plt.plot(num_symbol_list, sf_compression_ratio_changing_data_size_list, marker='o', label='Shannon-Fano')
    plt.plot(num_symbol_list, huffman_compression_ratio_changing_data_size_list, marker='o', label='Huffman')
    plt.xlabel('Number of Symbols')
    plt.ylabel('Compression Ratio')
    plt.title('Shannon-Fano vs. Huffman')
    plt.legend()
    plt.grid(True)
    plt.savefig('image/num_symbol.png')
    plt.show()

    # plt.plot(num_symbol_list, sf_compression_time_changing_data_size_list, marker='o', label='Shannon-Fano')
    # plt.plot(num_symbol_list, huffman_compression_time_changing_data_size_list, marker='o', label='Huffman')
    # plt.xlabel('Number of Symbols')
    # plt.ylabel('Compression Time (seconds)')
    # plt.title('Shannon-Fano vs. Huffman')
    # plt.legend()
    # plt.grid(True)
    # plt.show()

    # plt.plot(num_symbol_list, sf_decompression_time_changing_data_size_list, marker='o', label='Shannon-Fano')
    # plt.plot(num_symbol_list, huffman_decompression_time_changing_data_size_list, marker='o', label='Huffman')
    # plt.xlabel('Number of Symbols')
    # plt.ylabel('Decompression Time (seconds)')
    # plt.title('Shannon-Fano vs. Huffman')
    # plt.legend()
    # plt.grid(True)
    # plt.show()


def get_number_from_filename(file_path):
    try:
        return int(os.path.basename(file_path).split('_')[0])
    except ValueError:
        return float('inf')


def format_numbers_for_legend(numbers):
    formatted_numbers = []
    for num in numbers:
        if num < 1000:
            formatted_numbers.append(str(num))
        elif num < 1e6:
            formatted_numbers.append(f"{num / 1e3:.0f}k")
        elif num < 1e9:
            formatted_numbers.append(f"{num / 1e6:.0f}M")
        else:
            formatted_numbers.append(f"{num / 1e9:.0f}B")
    return formatted_numbers


if __name__ == '__main__':
    analyse_num_symbol_type()
    analyse_data_size()
