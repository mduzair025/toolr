from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
from rembg import remove
from uuid import uuid4
import os
import subprocess

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def ensure_directory():
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

def convert_to_white_background(input_image):
    # Create a white background image
    white_bg = Image.new("RGBA", input_image.size, "WHITE")
    # Combine the original image with the white background
    white_bg.paste(input_image, mask=input_image.split()[3])  # 3 is the alpha channel
    return white_bg

def process_image(image_path):
    # Load the image
    input_image = Image.open(image_path)

    # Remove the background
    output_image = remove(input_image)

    # Convert transparent background to white
    white_bg_image = convert_to_white_background(output_image)
    white_bg_path = f"uploads/{str(uuid4())}_white_bg.png"
    white_bg_image.convert('RGB').save(white_bg_path, 'PNG')

    # Convert image to BMP format first
    bmp_path = f"{white_bg_path[:-4]}.bmp"
    img = Image.open(white_bg_path)
    img.save(bmp_path)

    # Convert PNG to SVG (using an external command like potrace)
    svg_path = f"uploads/{str(uuid4())}.svg"
    subprocess.run(["potrace", bmp_path, "-s", "-o", svg_path])

    os.remove(bmp_path)
    os.remove(white_bg_path)
    os.remove(image_path)
    return svg_path


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/convert', methods=['POST'])
def convert_images():
    ensure_directory()
    if 'images' not in request.files:
        return jsonify({'error': 'No images uploaded'}), 400
    response = []
    for image in request.files.getlist('images'):
        if image.filename == '':
            continue
        if image and allowed_file(image.filename):
            image_path = f'uploads/{image.filename}'
            image.save(image_path)
            try:
                processed_path = process_image(image_path)
                response.append(processed_path)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Invalid image format'}), 400
    return jsonify({'processed_images': response})

if __name__ == '__main__':
    app.run(debug=True)
