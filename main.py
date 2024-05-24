import os
import json
import pytesseract
import cv2
from PIL import Image
import ftfy
import pan_read
import io

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\com\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
)

def process_image(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    var = cv2.Laplacian(img, cv2.CV_64F).var()
    
    if var < 50:
        print(f"Image {image_path} is Too Blurry....")
        return None
    
    text = pytesseract.image_to_string(Image.open(image_path), lang="eng")
    
    text = ftfy.fix_text(text)
    text = ftfy.fix_encoding(text)
    
    # for pan card
    data = pan_read.pan_read_data(text)
    
    return data

def read_images_from_folder(folder_path):
    images_data = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            image_path = os.path.join(folder_path, filename)
            data = process_image(image_path)
            if data:
                images_data.append(data)
    
    return images_data

folder_path = r"C:\Users\com\Downloads\PAN_card_OCR\images"  # Replace with your folder path
images_data = read_images_from_folder(folder_path)

# Save the list of dictionaries to a JSON file
with io.open("info.json", "w", encoding="utf-8") as outfile:
    data = json.dumps(
        images_data, indent=4, sort_keys=True, separators=(",", ": "), ensure_ascii=False
    )
    outfile.write(data)

print("Processed data saved to info.json")
