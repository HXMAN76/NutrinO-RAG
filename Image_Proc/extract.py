import google.generativeai as gemini
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Google Generative AI
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set it in the .env file.")
else:
    gemini.configure(api_key=api_key)

def get_food_items_from_image(image_bytes, mime_type):
    input_prompt = """
    You are an expert in identifying the food items through an image. List out the food items that can be seen in the provided image and provide the names of the food in JSON format.
    """

    def get_gem_response(input_prompt, image_data):
        try:
            model = gemini.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content([input_prompt, image_data])
            return response.text
        except Exception as e:
            raise RuntimeError(f"Error during API call: {e}")

    def input_image_setup(image_bytes, mime_type):
        # Prepare the image data for API consumption
        image_data = {
            "mime_type": mime_type,
            "data": image_bytes
        }
        return image_data

    image_data = input_image_setup(image_bytes, mime_type)
    response_text = get_gem_response(input_prompt, image_data)
    
    def extract_json_from_text(text):
        # Clean up the response text
        text = text.strip()
        # Remove the leading and trailing backticks and any extra `json` tag
        if text.startswith('```json'):
            text = text[len('```json'):].strip()
        if text.endswith('```'):
            text = text[:-len('```')].strip()
        # Remove any other non-JSON content (e.g., leading/trailing `json`)
        text = text.strip().strip('`').strip()
        
        # Handle list response directly
        try:
            parsed_list = json.loads(text)
            if isinstance(parsed_list, list):
                # Wrap list in a JSON object with 'food_items' key
                json_output = json.dumps({"food_items": parsed_list}, ensure_ascii=False, indent=2)
                return json_output
            else:
                raise ValueError("The response is not a list. Expected a JSON list.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse the extracted JSON: {e}")
        
    return extract_json_from_text(response_text)

# Example usage (for testing purposes)
# if __name__ == "__main__":
#     image_path = "C:\\Users\\Baranidharan Se\\OneDrive\\Pictures\\Screenshots\\Screenshot 2024-08-07 210555.png"
#     with open(image_path, 'rb') as img_file:
#         image_bytes = img_file.read()
#         mime_type = 'image/jpeg'
#     try:
#         result = get_food_items_from_image(image_bytes, mime_type)
#         print(result)
#     except Exception as e:
#         print(f"An error occurred: {e}")
