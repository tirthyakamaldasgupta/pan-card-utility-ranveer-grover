import os
import json
from typing import Dict
import pytesseract
import cv2
from PIL import Image
import ftfy
import pan_read
import io
from dotenv import load_dotenv

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


def get_env_vars(*args: str) -> Dict[str, str]:
    env_vars = {}

    for arg in args:
        env_vars[arg] = os.getenv(arg)

        if not env_vars[arg]:
            raise EnvironmentError(f"'{arg}'")

    return env_vars


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

env_vars = get_env_vars("DB_HOST", "DB_USERNAME", "DB_PASSWORD", "DB_NAME")

DB_HOST = env_vars["DB_HOST"]
DB_USERNAME = env_vars["DB_USERNAME"]
DB_PASSWORD = env_vars["DB_PASSWORD"]
DB_NAME = env_vars["DB_NAME"]

connection = pymysql.connect(host=DB_HOST, user=DB_USERNAME, password=DB_PASSWORD, database=DB_NAME,
        autocommit=True)

for image_data in images_data:
    with connection.cursor() as cursor:
        try:
            statement = "SET SQL_MODE='ALLOW_INVALID_DATES'"

            cursor.execute(statement)

            statement = f"INSERT INTO pan_card_details (`date_of_birth`, `father_name`, `name`, `pan_card_number`) VALUES (f'{image_data['Date of Birth']}')"

            cursor.execute(statement)
        except pymysql.Error as err:
            continue
