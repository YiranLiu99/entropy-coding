import math
import os
import numpy as np
from PIL import Image, ImageDraw
import random


def convert_to_grayscale(file_path):
    with Image.open(file_path) as img:
        file_full_name = os.path.basename(file_path)
        file_name, file_extension = os.path.splitext(file_full_name)
        # Convert image to grayscale
        img = img.convert("L")
        # Save the grayscale image
        img.save('gray_' + file_name + '.bmp', 'bmp')


def generate_random_grayscale_bmp(width, height, num_grayscale):
    image = Image.new('L', (width, height))
    pixels = image.load()
    grayscale_values = random.sample(range(256), min(num_grayscale, 256))
    for x in range(width):
        for y in range(height):
            pixels[x, y] = random.choice(grayscale_values)
    return image


def resize_image(input_path, output_path, new_width, new_height):
    original_image = Image.open(input_path)
    resized_image = original_image.resize((new_width, new_height))
    resized_image.save(output_path)


# convert_to_grayscale('../image_sample/building_4000_6000.jpg')

# size_list = [(400, 600), (800, 1200), (1200, 1800), (1600, 2400), (2000, 3000), (2400, 3600), (2800, 4200), (3200, 4800), (3600, 5400), (4000, 6000)]
# for i, size in enumerate(size_list):
#     width = size[0]
#     height = size[1]
#     size_name = str(width) + '_' + str(height)
#     resize_image('../image_sample/building_4000_6000.bmp', '../image_sample/evaluation_sample/change_num_symbol/' + str(i+1) + '_building_' + size_name + '.bmp', width, height)


# width = 1024
# height = 1024
# # generate num list: [20, 30, 40, 50, ..., 255]
# num_grayscale_list = [i for i in range(20, 256, 10)] + [255]
# # generate images(1024*1024) for each num_grayscale
# for num in num_grayscale_list:
#     bmp_image = generate_grayscale_bmp(width, height, num)
#     bmp_image.save('../image_sample/evaluation_sample/change_num_symbol_type/gray_' + str(width) + '_' + str(height) + '_' + str(num) + '.bmp')


width = 1024
height = 1024
num_grayscale = 2
bmp_image = generate_random_grayscale_bmp(width, height, num_grayscale)
bmp_image.save('../image_sample/grayscale_image' + str(width) + '_' + str(height) + '_' + str(num_grayscale) + '.bmp')
bmp_image.show()
