# import os
# import asyncio
# from dotenv import load_dotenv
# from pymongo import MongoClient
# from groq import Groq
# from tavily import TavilyClient
# from crawl4ai import AsyncWebCrawler
# import requests

# load_dotenv()

# groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# mongo_client = MongoClient(os.getenv("MONGO_DB_CLIENT"))
# db = mongo_client["medical_records_db"]
# collection = db["patients"]

# async def crawl_url(url):
#     try:
#         async with AsyncWebCrawler(verbose=True) as crawler:
#             result = await crawler.arun(url=url)
#             return result.markdown
#     except Exception as e:
#         print(f"Error crawling {url}: {e}")
#         return None

# async def web_scrap_avail_links(avail_links):
#     tasks = [crawl_url(url) for url in avail_links]
#     results = await asyncio.gather(*tasks)  # Await all tasks together
    
#     with open("scrapped.txt", "w", encoding="utf-8") as file:
#         for result in results:
#             if result:
#                 file.write(result + "\n")

# def get_query_urls(user_query):
#     client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
#     response = client.search(user_query)
    
#     available_urls = []
#     for r in response["results"]:
#         try:
#             if requests.get(r["url"]).status_code == 200:
#                 available_urls.append(r["url"])
#         except requests.RequestException as e:
#             print(f"Error fetching {r['url']}: {e}")

#     return available_urls

# def get_patient_by_mrn(mrn_number):
#     patient = collection.find_one({"MRN Number": mrn_number})
#     if patient:
#         patient["_id"] = str(patient["_id"])
#     return patient

# def split_content(content, max_length=2000):
#     return [content[i:i + max_length] for i in range(0, len(content), max_length)]

# def llm_infer(medical_rec, webscraped_content, user_query):
#     content_chunks = split_content(webscraped_content)
#     aggregated_response = ""
#     for i, chunk in enumerate(content_chunks):
#         combined_prompts = [
#             {
#                 "role": "user",
#                 "content": f"Imagine you're a nutritionist with expertise in all types of medical conditions. {medical_rec}, this is a patient's medical history in JSON format. Based on that, you'll need to understand their medical records. For any subsequent prompts I give, you must tailor your response according to the restrictions and requirements outlined in the patient's medical records. Consider this as PROMPT-1. Do not provide any type of introduction or conclusion for the generated content by your side."
#             },
#             {
#                 "role": "user",
#                 "content": f"Consider this as PROMPT-2: {chunk}. This is part {i+1} of the webscraped content I gathered based on the user query: {user_query}. Summarize the following content into the smallest possible form while retaining all key points. Your summary must be concise, clear, and cover every detail strictly from the provided content without adding or omitting any information. Do not introduce or conclude the response. Only use the content given as your source."
#             }
#         ]


        
#         chat_completion = groq_client.chat.completions.create(
#             messages=combined_prompts,
#             model="llama3-8b-8192",
#         )

#         aggregated_response += chat_completion.choices[0].message.content + "\n"

#     return aggregated_response

# # Main execution flow
# if __name__ == "__main__":
#     mrd_number_input = input("Enter MRN Number: ")
#     patient_data = get_patient_by_mrn(mrd_number_input)

#     if patient_data:
#         print("Patient found:")
#         print(patient_data)

#         user_query = input("Enter your query: ")
#         query_urls = get_query_urls(user_query)
        
#         if query_urls:
#             asyncio.run(web_scrap_avail_links(query_urls))  # Call the async web scraping function

#             with open("scrapped.txt", "r", encoding="utf-8") as file:
#                 webscraped_content = file.read()

#             result = llm_infer(patient_data, webscraped_content, user_query)

#             print("Model's response:")
#             print(result)
#         else:
#             print("No valid URLs found for the given query.")
#     else:
#         print("MRN Number not found. Please check the number and try again.")


import os
import asyncio
from dotenv import load_dotenv
from pymongo import MongoClient
from groq import Groq
from tavily import TavilyClient
from crawl4ai import AsyncWebCrawler
import requests

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
mongo_client = MongoClient(os.getenv("MONGO_DB_CLIENT"))
db = mongo_client["medical_records_db"]
collection = db["patients"]

async def crawl_url(url):
    try:
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(url=url)
            return result.markdown
    except Exception as e:
        print(f"Error crawling {url}: {e}")
        return None

async def web_scrap_avail_links(avail_links):
    tasks = [crawl_url(avail_links[i]) for i in range (3)]
    results = await asyncio.gather(*tasks)
    
    with open("scrapped.txt", "w", encoding="utf-8") as file:
        for result in results:
            if result:
                file.write(result + "\n")

def get_query_urls(user_query):
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = client.search(user_query)
    
    available_urls = []
    for r in response["results"]:
        try:
            if requests.get(r["url"]).status_code == 200:
                available_urls.append(r["url"])
              #  print(f"Fectched one: {r['url']}")
        except requests.RequestException as e:
            print(f"Error fetching {r['url']}: {e}")

    return available_urls

def get_patient_by_mrn(mrn_number):
    patient = collection.find_one({"MRN Number": mrn_number})
    if patient:
        patient["_id"] = str(patient["_id"])
    return patient

def split_content(content, max_length=2000):
    return [content[i:i + max_length] for i in range(0, len(content), max_length)]

def summarize_chunks(medical_rec, content_chunks, user_query):
    """
    Summarize each chunk individually.
    """
    summarized_chunks = []
    for i, chunk in enumerate(content_chunks):
        combined_prompts = [
            {
                "role": "user",
                "content": f"Imagine you're a nutritionist with expertise in all types of medical conditions. {medical_rec}, this is a patient's medical history in JSON format. Based on that, you'll need to understand their medical records. For any subsequent prompts I give, you must tailor your response according to the restrictions and requirements outlined in the patient's medical records. Consider this as PROMPT-1. Do not provide any type of introduction or conclusion for the generated content by your side."
            },
            {
                "role": "user",
                "content": f"Consider this as PROMPT-2: {chunk}. This is part {i+1} of the webscraped content I gathered based on the user query: {user_query}. Summarize the following content into the smallest possible form while retaining all key points and providing essential details. Your summary must be concise, clear, and cover every detail strictly from the provided content without adding or omitting any information. Provide sufficient context to help the user understand, but do not introduce or conclude the response."
            }
        ]

        chat_completion = groq_client.chat.completions.create(
            messages=combined_prompts,
            model="llama3-8b-8192",
        )

        summarized_chunks.append(chat_completion.choices[0].message.content.strip())
    
    # Return the summarized chunks combined
    return " ".join(summarized_chunks)

def final_summary(medical_rec, summarized_content):
    """
    Take the summarized content from chunks and make a final concise summary.
    """
    final_prompt = [
        {
            "role": "user",
            "content": f"Imagine you're a nutritionist with expertise in all types of medical conditions. {medical_rec}, this is a patient's medical history in JSON format. Based on that, you'll need to understand their medical records. For any subsequent prompts I give, you must tailor your response according to the restrictions and requirements outlined in the patient's medical records. Consider this as PROMPT-1. Do not provide any type of introduction or conclusion for the generated content by your side. Even if the provided query has nothing to do with the medical records, You will reply with saying that the person in the medical record has nothing to do with this medical issue. But for the information I would still provide you the medical diagnosis. You are not supposed to refer any other type of information other than the medical records i have given and the actual webscraped content i have provided."
        },
        {
            "role": "user",
            "content": f"Consider this as PROMPT-2: {summarized_content}. This is the combined summary from multiple parts of webscraped content. Provide a **final detailed summary** that retains the most important points and enough context for understanding, in the smallest possible form. Provide the response in 4 sections: 1. About the condition, 2. Prevention strategies, 3. Medication options, and 4. Nutritional advice, ensuring clarity and completeness."
        }
    ]

    chat_completion = groq_client.chat.completions.create(
        messages=final_prompt,
        model="llama3-8b-8192",
    )

    return chat_completion.choices[0].message.content.strip()


def llm_infer(medical_rec, webscraped_content, user_query):
    content_chunks = split_content(webscraped_content)
    
    # Step 1: Summarize individual chunks
    summarized_content = summarize_chunks(medical_rec, content_chunks, user_query)

    # Step 2: Generate the final summary from the summarized chunks
    final_response = final_summary(medical_rec, summarized_content)

    return final_response

def summarize_chunks_diet_plan(medical_rec,content_chunks, user_query):
    summarized_chunks = []
    for i, chunk in enumerate(content_chunks):
        combined_prompts = [
            {
                "role": "user",
                "content": f"Imagine you're a nutritionist with expertise in creating a good diet planner based on patient's {medical_rec}, this is a patient's medical history in JSON format. Based on that, you'll need to understand their medical records. For any subsequent prompts I give, you must tailor your response according to the restrictions and requirements outlined in the patient's medical records. Consider this as PROMPT-1. Do not provide any type of introduction or conclusion for the generated content by your side."
            },
            {
                "role": "user",
                "content": f"Consider this as PROMPT-2: {chunk}. This is part {i+1} of the webscraped content I gathered based on the user query: {user_query}. Summarize the following content into the smallest possible form while retaining all key points and providing essential details. Your summary must be concise, clear, and cover every detail strictly from the provided content without adding or omitting any information. Provide sufficient context to help the user understand, but do not introduce or conclude the response."
            }
        ]

        chat_completion = groq_client.chat.completions.create(
            messages=combined_prompts,
            model="llama3-8b-8192",
        )

        summarized_chunks.append(chat_completion.choices[0].message.content.strip())
    
    # Return the summarized chunks combined
    return " ".join(summarized_chunks)

def final_summary_diet_plan(medical_rec, summarized_content):
    """
    Take the summarized content from chunks and make a final concise summary.
    """
    final_prompt = [
        {
            "role": "user",
            "content": f"Imagine you're a nutritionist with expertise in creating a good diet planner based on patient's {medical_rec}, this is a patient's medical history in JSON format. Based on that, you'll need to understand their medical records. For any subsequent prompts I give, you must tailor your response according to the restrictions and requirements outlined in the patient's medical records. Consider this as PROMPT-1. Do not provide any type of introduction or conclusion for the generated content by your side. Even if the provided query has nothing to do with the medical records, You will reply with saying that the person in the medical record has nothing to do with this medical issue. But for the information I would still provide you the medical diagnosis. You are not supposed to refer any other type of information other than the medical records i have given and the actual webscraped content i have provided."
        },
        {
            "role": "user",
            "content": f"Consider this as PROMPT-2: {summarized_content}. This is the combined summary from multiple parts of webscraped content. Provide a **Customized Diet plan** that retains the most important points and enough context for understanding, in the smallest possible form. "
        }
    ]

    chat_completion = groq_client.chat.completions.create(
        messages=final_prompt,
        model="llama3-8b-8192",
    )

    return chat_completion.choices[0].message.content.strip()

def diet_plan_call(medical_rec,webscraped_content,user_query):
    
    content_chunks = split_content(webscraped_content)
    summarized_content = summarize_chunks_diet_plan(medical_rec,content_chunks, user_query)
    final_response = final_summary_diet_plan(medical_rec, summarized_content)

    return final_response

# # Main execution flow
# if __name__ == "__main__":
#     mrd_number_input = input("Enter MRN Number: ")
#     patient_data = get_patient_by_mrn(mrd_number_input)

#     if patient_data:
#         print("Patient found:")
#         print(patient_data)

#         user_query = input("Enter your query: ")
#         query_urls = get_query_urls(user_query)
        
#         if query_urls:
#             asyncio.run(web_scrap_avail_links(query_urls))  # Call the async web scraping function

#             with open("scrapped.txt", "r", encoding="utf-8") as file:
#                 webscraped_content = file.read()

#             result = llm_infer(patient_data, webscraped_content, user_query)

#             print("Model's response:")
#             print(result)
#         else:
#             print("No valid URLs found for the given query.")
#     else:
#         print("MRN Number not found. Please check the number and try again.")


