from PIL import Image
import numpy as np
import cv2

def load_image(image_path):
    """Load an image and convert it to RGB format."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Image not found at {image_path}")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

def save_image(image_array, save_path):
    """Save a NumPy image array to a file."""
    image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
    cv2.imwrite(save_path, image_bgr)
