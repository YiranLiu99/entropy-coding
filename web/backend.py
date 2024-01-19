# backend.py
import io
import json
import os
import PIL
from flask import Flask, render_template, request, jsonify, send_file
from helper import visualizer
from huffman import huffman_image
import plotly.io as pio
from shannon import shannon_fano_image

app = Flask(__name__)

HUF_UPLOAD_FOLDER = 'uploads/huffman/'
SF_UPLOAD_FOLDER = 'uploads/sf/'
ALLOWED_EXTENSIONS = {'bmp'}

app.config['HUF_IMG_UPLOAD_FOLDER'] = HUF_UPLOAD_FOLDER
app.config['SF_IMG_UPLOAD_FOLDER'] = SF_UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shannon')
def shannon():
    return render_template('shannon.html')


@app.route('/uploadImageAndHuffmanCompressDecompress', methods=['POST'])
def upload_image_and_huffman_compress_decompress():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    pil_img = PIL.Image.open(file)
    file_name, file_extension = os.path.splitext(file.filename)
    # Save the original image at directory uploads/file_name.bmp
    original_image_path = os.path.join(app.config['HUF_IMG_UPLOAD_FOLDER'], file_name + file_extension)
    pil_img.save(original_image_path)
    print(original_image_path)

    print('Compressing the image...')
    # Compress the image and generate Huffman tree
    huff_image = huffman_image.HuffmanImage(file)
    huff_image.process_image()
    huffman_tree_fig = huff_image.visual_huffman_tree_image()
    # Convert Figure object to JSON using plotly.io.to_json
    huffman_tree_fig_json = pio.to_json(huffman_tree_fig)
    compressed_data_bytes = huff_image.to_compressed_image()
    frequency_dict = huff_image.frequencies
    huffman_codes_dict = huff_image.huffman_codes_dict
    frequency_dict_json = json.dumps(frequency_dict)
    huffman_codes_dict_json = json.dumps(huffman_codes_dict)

    # Save compressed data to a binary file
    compressed_data_path = os.path.join(app.config['HUF_IMG_UPLOAD_FOLDER'], 'huffman_compressed_' + file_name + '.bin')
    with open(compressed_data_path, 'wb') as file:
        file.write(compressed_data_bytes)
    print(compressed_data_path)

    print('Decompressing the image...')
    huffman_image.save_decompressed_image('../web/uploads/huffman/huffman_compressed_' + file_name + '.bin',
                                          '../web/uploads/huffman/')
    print('uploads/huffman_decompressed_' + file_name + file_extension)

    # return jsonify({'plotly_figure': huffman_tree_fig_json})
    return jsonify({"plotly_figure": huffman_tree_fig_json,
                    "frequency_dict": frequency_dict_json,
                    "huffman_code_dict": huffman_codes_dict_json,
                    "compressed_data_path": compressed_data_path,
                    "original_image_path": original_image_path,
                    "image_name": file_name,
                    "image_extension": file_extension})


@app.route('/uploadImageAndShannonCompressDecompress', methods=['POST'])
def upload_image_and_shannon_compress_decompress():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    pil_img = PIL.Image.open(file)
    file_name, file_extension = os.path.splitext(file.filename)
    original_image_path = os.path.join(app.config['SF_IMG_UPLOAD_FOLDER'], file_name + file_extension)
    pil_img.save(original_image_path)
    print(original_image_path)

    print('Compressing the image...')
    # Compress the image and generate Huffman tree
    sf_image = shannon_fano_image.ShannonFanoImage(file)
    sf_image.process_image()
    sf_tree_fig = visualizer.visualize_tree(sf_image.sf_tree_graph)
    # Convert Figure object to JSON using plotly.io.to_json
    sf_tree_fig_json = pio.to_json(sf_tree_fig)
    compressed_data_bytes = sf_image.to_compressed_image()
    frequency_dict = sf_image.frequencies
    sf_codes_dict = sf_image.sf_code_dict
    frequency_dict_json = json.dumps(frequency_dict)
    sf_codes_dict_json = json.dumps(sf_codes_dict)

    # Save compressed data to a binary file
    compressed_data_path = os.path.join(app.config['SF_IMG_UPLOAD_FOLDER'], 'sf_compressed_' + file_name + '.bin')
    with open(compressed_data_path, 'wb') as file:
        file.write(compressed_data_bytes)
    print(compressed_data_path)

    print('Decompressing the image...')
    shannon_fano_image.save_decompressed_image('../web/uploads/sf/sf_compressed_' + file_name + '.bin',
                                     '../web/uploads/sf/')
    print('uploads/sf/sf_decompressed_' + file_name + file_extension)

    return jsonify({"plotly_figure": sf_tree_fig_json,
                    "frequency_dict": frequency_dict_json,
                    "sf_code_dict": sf_codes_dict_json,
                    "compressed_data_path": compressed_data_path,
                    "original_image_path": original_image_path,
                    "image_name": file_name,
                    "image_extension": file_extension})


# @app.route('/downloadHuffmanCompressedImageData', methods=['POST'])
# def download_huffman_compressed_image_data():
#     file_path = 'uploads/compressed_image_data.bin'
#     print(request)
#     print(111)
#     try:
#         return send_file(file_path, as_attachment=True)
#     except Exception as e:
#         return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
