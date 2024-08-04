import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv
import json
import time
from PIL import Image
import base64

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(filename='table_extraction.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Gemini API configuration
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_image(image_path):
    try:
        # Encode the image
        base64_image = encode_image(image_path)

        # Set up the model
        model = genai.GenerativeModel('gemini-1.5-flash.')
        

        # Prepare the prompt
        prompt = """
        Analyze this image and extract all table data.
        Provide the extracted data in a structured JSON format.
        Each table should be represented as a list of lists, where each inner list represents a row of the table.
        If there are multiple tables, provide them as separate elements in the JSON array.
        """

        # Generate content
        response = model.generate_content([
            prompt,
            {
                "mime_type": "image/jpeg",
                "data": base64_image
            }
        ])

        # Process and return the response
        return json.loads(response.text)

    except Exception as e:
        logging.error(f"Error processing image {image_path}: {str(e)}")
        return None

def process_images_in_directory(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_extracted.json")

            logging.info(f"Processing image: {filename}")
            extracted_data = process_image(image_path)

            if extracted_data:
                with open(output_path, 'w') as f:
                    json.dump(extracted_data, f, indent=2)
                logging.info(f"Extracted data saved to: {output_path}")
            else:
                logging.warning(f"Failed to extract data from: {filename}")

            # Add a delay to respect rate limits (adjust as needed)
            time.sleep(1)

def main():
    input_dir = 'Ref_Output'
    output_dir = 'JSON-Output'

    process_images_in_directory(input_dir, output_dir)
    print("Processing completed. Check the log file for details.")

if __name__ == "__main__":
    main()
