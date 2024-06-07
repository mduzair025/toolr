from flask import Flask, request, jsonify
from PIL import Image, ImageDraw
import cairosvg

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def convert_to_svg(image_path):
    # First, save the image as PNG if not already
    temp_png_path = f"{image_path[:-4]}.png"
    img = Image.open(image_path)
    img.save(temp_png_path)

    # Convert the PNG file to SVG
    svg_path = f"{image_path[:-4]}.svg"
    cairosvg.png2svg(url=temp_png_path, write_to=svg_path)  # Hypothetical function call

    return svg_path

# def convert_to_svg(image_path):
#     img = Image.open(image_path)
#     # Convert to grayscale (optional)
#     img = img.convert('L')
#     # Create a new blank image (white background)
#     svg_img = ImageDraw.Draw(img.convert('RGBA'))
#     # Loop through each pixel and set opacity based on grayscale value
#     for y in range(img.height):
#         for x in range(img.width):
#             grayscale = img.getpixel((x, y))
#             opacity = int(255 - grayscale)
#             svg_img.point((x, y), fill=(0, 0, 0, opacity))

#     # Save as SVG
#     with open(f"{image_path[:-4]}.svg", 'wb') as f:
#         img.save(f, format='SVG')
#     return f"{image_path[:-4]}.svg"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/convert', methods=['POST'])
def convert_images():
    if 'images' not in request.files:
        return jsonify({'error': 'No images uploaded'}), 400
    response = []
    for image in request.files.getlist('images'):
        if image.filename == '':
            continue
        if image and allowed_file(image.filename):
            image_path = f'uploads/{image.filename}'
            image.save(image_path)
            svg_path = convert_to_svg(image_path)
            response.append(svg_path)
        else:
            return jsonify({'error': 'Invalid image format'}), 400
    return jsonify({'svgs': response})


if __name__ == '__main__':
    app.run(debug=True)
