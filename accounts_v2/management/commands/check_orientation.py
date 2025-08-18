import cv2
import pytesseract
from pytesseract import Output
import requests
import numpy as np

# Load image from URL
url = "https://blr1.digitaloceanspaces.com/vc-thumbnails/studentpeeps/collegeidcards/17554252175193271639051337071390.jpg"
resp = requests.get(url, stream=True).content
img_array = np.asarray(bytearray(resp), dtype=np.uint8)
img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

# Run OSD (Orientation & Script Detection)
osd = pytesseract.image_to_osd(img, output_type=Output.DICT)

# Get rotation angle
rotate = osd.get("rotate", 0)
print(f"Detected rotation: {rotate}°")

# Rotate the image if required
if rotate != 0:
    if rotate == 90:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif rotate == 180:
        img = cv2.rotate(img, cv2.ROTATE_180)
    elif rotate == 270:
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    print(f"Image rotated by {rotate}°")

# Run OCR on corrected image
text = pytesseract.image_to_string(img)
print("\nExtracted Text:\n")
print(text)
