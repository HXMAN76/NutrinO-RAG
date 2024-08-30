import openai
from dotenv import load_dotenv
import os
import json

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Prompt template
PROMPT_TEMPLATE = """think you are an expert in extracting any information from any format of text and converting them into meaningfull sentences para wise without conlusion and intro in .txt format. """

def process_json_file(file_path):
    with open(file_path, 'r',encoding='utf-8',errors='ignore') as file:
        data = json.load(file)
    
    # Combine the prompt with the JSON data
    full_prompt = f"{PROMPT_TEMPLATE}\n\nJSON Data:\n{json.dumps(data)}"
    
    # Call the GPT-4 API
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": full_prompt}
        ]
    )
    
    return response.choices[0].message['content']

def main():
    folder_path = "C:\\Users\\saini\\Downloads\\output_table\\Not_processed\\table-3"  # Replace with your folder path
    output_file = "E:\\Proj_Nutrionist_app\\Pending_3.txt"  # Use .txt for the output file
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for i in range(1, 51):
            file_name = f"table_data_page_{i}.json"
            file_path = os.path.join(folder_path, file_name)
            
            if os.path.exists(file_path):
                print(f"Processing {file_name}...")
                result = process_json_file(file_path)
                outfile.write(f"Results for {file_name}:\n")
                outfile.write(result)
                outfile.write("\n\n")
            else:
                print(f"File {file_name} not found. Skipping.")

    print(f"Processing complete. Results saved to {output_file}")

if __name__ == "__main__":
    main()
