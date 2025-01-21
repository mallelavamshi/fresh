import streamlit as st
import os
import requests
import pandas as pd
import json
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from PIL import Image
import io
import tempfile
from datetime import datetime
import uuid
import gdown
from openpyxl.styles import Alignment, PatternFill
from openpyxl.worksheet.dimensions import RowDimension, ColumnDimension
from openpyxl.utils import get_column_letter
import weasyprint
import base64

# Configure page
st.set_page_config(page_title="Image Analysis App", layout="wide")

# Hardcoded API Key
API_KEY = "app-53gFeCZttFUyoMs0HuL0eNyc"

# List of valid coupon codes
VALID_COUPON_CODES = {"CODE123", "DISCOUNT50", "FREEACCESS"}

def is_valid_coupon(coupon):
    return coupon in VALID_COUPON_CODES

def get_image_files_from_folder(folder_path):
    valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
    image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)]
    return image_files

def upload_file(image_path):
    upload_url = 'https://api.dify.ai/v1/files/upload'
    headers = {'Authorization': f'Bearer {API_KEY}'}
    with open(image_path, 'rb') as image_file:
        files = {'file': (os.path.basename(image_path), image_file, 'image/jpeg')}
        response = requests.post(upload_url, headers=headers, files=files)
        response.raise_for_status()
        return response.json().get('id')

def process_image(image_path):
    try:
        file_id = upload_file(image_path)
        url = 'https://api.dify.ai/v1/chat-messages'
        headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
        payload = {
            "query": "Analyze this image and provide a detailed description and value assessment",
            "files": [{"type": "image", "transfer_method": "local_file", "upload_file_id": file_id}]
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json().get('answer', 'No response received')
    except requests.exceptions.RequestException as e:
        return f"Error processing image: {str(e)}"

def main():
    st.title("Image Analysis App")
    coupon_code = st.text_input("Enter your coupon code:", type="password")
    
    if not is_valid_coupon(coupon_code):
        st.error("Invalid coupon code. Please enter a valid code.")
        return
    
    folder_path = st.text_input("Enter folder path containing images:").strip().replace("\\", "/")

    if folder_path and os.path.isdir(folder_path):
        if st.button("Process Images"):
            image_files = get_image_files_from_folder(folder_path)
            if not image_files:
                st.error("No valid images found in the folder.")
                return
            
            progress_bar = st.progress(0)
            results = []
            for i, image_path in enumerate(image_files):
                response = process_image(image_path)
                results.append((image_path, response))
                progress_bar.progress((i + 1) / len(image_files))
            
            for image_path, result in results:
                st.image(Image.open(image_path), caption=os.path.basename(image_path))
                st.write(result)
    else:
        st.warning("Please enter a valid folder path.")

if __name__ == "__main__":
    main()
