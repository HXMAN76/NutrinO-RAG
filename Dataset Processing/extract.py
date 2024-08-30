
import os
import logging
from pdf2image import convert_from_path
import google.generativeai as gemini
from dotenv import load_dotenv
import json
import time
from PIL import Image
import io
from collections import deque
import threading

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(filename='table_extraction.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# Gemini API configuration
gemini.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Rate limiting setup
MAX_REQUESTS_PER_MINUTE = 600
MAX_REQUESTS_PER_SECOND = 5
request_timestamps = deque()
tokens = MAX_REQUESTS_PER_SECOND
last_token_refresh = time.time()
rate_limit_lock = threading.Lock()

def wait_for_token():
    global tokens, last_token_refresh
    while True:
        with rate_limit_lock:
            now = time.time()
            time_passed = now - last_token_refresh
            new_tokens = time_passed * MAX_REQUESTS_PER_SECOND
            if new_tokens > 1:
                tokens = min(tokens + new_tokens, MAX_REQUESTS_PER_SECOND)
                last_token_refresh = now
            if tokens >= 1:
                tokens -= 1
                break
        time.sleep(0.1)

    # Check and enforce per-minute limit
    now = time.time()
    request_timestamps.append(now)
    if len(request_timestamps) > MAX_REQUESTS_PER_MINUTE:
        oldest = request_timestamps.popleft()
        if now - oldest < 60:
            sleep_time = 60 - (now - oldest)
            time.sleep(sleep_time)

def get_gem_response(input_prompt, image):
    wait_for_token()
    model = gemini.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt, image])
    return response.text

def input_image_setup(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    image_parts = [
        {
            "mime_type": "image/png",
            "data": img_byte_arr
        }
    ]
    return image_parts

def extract_tables_from_pdf(pdf_path, output_dir, start_page=1, end_page=None):
    # Convert PDF to images
    images = convert_from_path(pdf_path, first_page=start_page, last_page=end_page)
    
    input_prompt = """
    You are an expert in data extraction. Please analyze the image and extract all table data.
    Provide the extracted data in a structured JSON format, with each table represented as a list of lists.
    Each inner list should represent a row of the table, with individual cells as elements.
    If there are multiple tables, please provide them as separate elements in the JSON array.also convert the text without converting special characters to Unicode escape sequences. 
    Ensure the JSON output preserves the original characters..
    """

    for i, image in enumerate(images, start=start_page):
        image_path = os.path.join(output_dir, f'page_{i}.png')
        image.save(image_path, 'PNG')
        
        try:
            # Process image with Gemini Pro Vision
            image_data = input_image_setup(image)
            response = get_gem_response(input_prompt, image_data[0])
            
            # Save extracted data as JSON
            output_file = os.path.join(output_dir, f'table_data_page_{i}.json')
            with open(output_file, 'w') as f:
                json.dump(response, f)
            
            logging.info(f"Processed page {i} successfully")
        
        except Exception as e:
            logging.error(f"Error processing page {i}: {str(e)}")

def main():
    
    pdf_path = '2.pdf'
    output_dir = 'output-images'
    print("HI")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    extract_tables_from_pdf(pdf_path, output_dir)

if __name__ == "__main__":
    main()
