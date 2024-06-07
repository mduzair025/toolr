from flask import Flask, request, jsonify
from PIL import Image
import os
from uuid import uuid4
import subprocess  # Required to call the command line

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def ensure_directory():
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

def convert_to_svg(image_path):
    # Convert image to BMP format first
    bmp_path = f"{image_path[:-4]}.bmp"
    img = Image.open(image_path)
    img.save(bmp_path)

    # Use Potrace to convert BMP to SVG
    svg_path = f"uploads{str(uuid4())}.svg"
    subprocess.run(['potrace', bmp_path, '-s', '-o', svg_path], check=True)
    
    # Optionally remove the BMP file after conversion
    os.remove(bmp_path)

    return svg_path

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def hello():
    return 'Hello, World!'

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
                svg_path = convert_to_svg(image_path)
                response.append(svg_path)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Invalid image format'}), 400
    return jsonify({'svgs': response})

if __name__ == '__main__':
    app.run(debug=True)

