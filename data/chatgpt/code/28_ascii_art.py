# generate python code to read in an image and render the image using ascii art.  
# worked out of the box

from PIL import Image
import numpy as np

# Define ASCII characters
ASCII_CHARS = "@%#*+=-:. "

# Load image and convert to grayscale
def load_image(image_path):
    img = Image.open(image_path)
    img_gray = img.convert("L")
    return img_gray

# Resize image
def resize_image(image, new_width):
    aspect_ratio = image.height / image.width
    new_height = int(aspect_ratio * new_width)
    resized_image = image.resize((new_width, new_height))
    return resized_image

# Convert grayscale image to ASCII
def pixel_to_ascii(pixel_value):
    return ASCII_CHARS[pixel_value * len(ASCII_CHARS) // 256]

def image_to_ascii(image):
    np_image = np.array(image)
    ascii_image = np.vectorize(pixel_to_ascii)(np_image)
    return "\n".join("".join(row) for row in ascii_image)

def main(image_path, new_width=80):
    image = load_image(image_path)
    resized_image = resize_image(image, new_width)
    ascii_art = image_to_ascii(resized_image)

    with open("ascii_art.txt", "w") as f:
        f.write(ascii_art)

    print(ascii_art)

if __name__ == "__main__":
    import sys
    image_path = sys.argv[1]
    main(image_path)
