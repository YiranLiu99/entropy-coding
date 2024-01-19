import glob
import os
from PIL import Image
from bitarray import bitarray


def read_image(input_file):
    # read image, if it is RGB, convert it to grayscale
    with Image.open(input_file) as img:
        # Convert image to grayscale
        img = img.convert("L")
        pixel_data = list(img.getdata())
        if isinstance(input_file, str):
            file_name, file_extension = os.path.splitext(os.path.basename(input_file))
        else:
            file_name, file_extension = os.path.splitext(input_file.filename)
    return img, pixel_data, file_name, file_extension


# read all images from folder
def read_images_from_directory(folder_path):
    image_files = glob.glob(os.path.join(folder_path, '*.bmp'))
    file_name_list = []
    for file_path in image_files:
        try:
            directory_path = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            file_name_list.append(directory_path + '/' + file_name)
        except Exception as e:
            print(f"Error reading image {file_path}: {e}")
    return file_name_list


def add_padding(encoded_data):
    # The double % 8 is used to ensure that pad_bits is always in the range of 0 to 7,
    # representing the number of bits needed to reach the next multiple of 8.
    num_pad_bits = (8 - len(encoded_data) % 8) % 8
    for i in range(num_pad_bits):
        encoded_data += bitarray('0')
    # Add this padding information to the beginning of compressed data
    # to keep track of how many bits have been added.
    # padding_info: exp. num_pad_bits=4 -> 0b100 -> 100 -> 00000100
    # First 8 bits of compressed data are padding info, showing the number of padding bits added.
    padding_info = bin(num_pad_bits)[2:].zfill(8)
    padded_data = bitarray(padding_info) + encoded_data
    return padded_data


def remove_padding(padded_data):
    bit_array = bitarray()
    bit_array.frombytes(padded_data)
    padded_info = int(bit_array[:8].to01(), 2)
    bit_array = bit_array[8:]
    encoded_data = bit_array[:-padded_info]
    return encoded_data
