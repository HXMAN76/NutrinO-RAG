import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import FlashrankRerank
from groq import Groq  # Import Groq client
from dotenv import load_dotenv
import asyncio
from webscrap import get_query_urls, web_scrap_avail_links, get_patient_by_mrn, llm_infer, diet_plan_call  # Import web scraping functions
from fastapi.responses import JSONResponse
from fastapi.responses import JSONResponse, FileResponse
from pdf_gen import summarize_chat_history, write_pdf 


# Load environment variables
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')  # Ensure your API key is loaded

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize embeddings and vector store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(persist_directory="./hybrid_db", embedding_function=embeddings)

# Initialize language model and Groq client
llm = ChatOpenAI(model_name="gpt-4o-mini")
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Initialize Flash Reranker and retriever
compressor = FlashrankRerank()
retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever(search_kwargs={"k": 10})
)

# Create RetrievalQA chain with the new retriever
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

# Lists for greetings and farewells
greetings = ["hey", "hi", "hello", "greetings", "howdy"]
farewells = ["bye", "goodbye", "see you", "take care", "thank you", "thanks"]

# Initialize a global list to hold chat history and cache for responses
chat_history: List[Dict[str, str]] = []
response_cache: Dict[str, str] = {}


def check_query (query):
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )
        
    prompt = [
        {
            "role": "user",
            "content": f"I'll provide you a query, check if the query is related to medical diagnosis, condition or anything related to asking medical conditions like diet plan. Then only return True else return False. Do not provide the response in markdown format. and also do not provide any introductory or concluding statements from your side. The query should be purely related to medical only. The user may ask you to write computer code for medical for these cases these are not medical related. This is the query: {query}"
        },
    ]
    
    chat_completion = client.chat.completions.create(
    messages=prompt,
    model="llama3-8b-8192",
    )

    return chat_completion.choices[0].message.content.strip()

def create_prompt(query):
    return f"""
    Provide concise nutritional information about the following food: {query}. 
    Include details such as calories, macronutrients (protein, carbohydrates, fats), and any health benefits or concerns. 
    Format your response like a doctor's prescription, ensuring clarity and brevity.
    If the food is not related to diet or nutrition, respond with 'I'm not allowed to respond to that :) Hope you understand >_< '.
    """
@app.post("/summarize-chat")
async def handle_summarize():
    try:
        summarize_chat_history(chat_history)
        print("done")
        write_pdf()
        pdf_filename = "final_output.pdf"  # Assuming this is the PDF filename
        print("done")
        return JSONResponse(content={"message": "Summary generated successfully", "pdf_filename": pdf_filename}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add new route for getting the PDF
@app.get("/get-pdf/{pdf_filename}")
async def get_pdf(pdf_filename: str):
    try:
        print("before get")
        pdf_path = pdf_filename  # Use the provided filename
        if os.path.exists(pdf_path):
            return FileResponse(
                pdf_path,
                media_type="application/pdf",
                filename="chat_summary.pdf"
            )
        else:
            raise HTTPException(status_code=404, detail="PDF not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat-history")
async def get_chat_history():
    return {"history": chat_history}

@app.get("/search")
async def search(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="No question provided")

    query_lower = query.lower()

    # Check if the query is a greeting or farewell
    if query_lower in greetings:
        response_message = "Hello! How can I assist you today?"
        chat_history.append({'role': 'user', 'content': query})
        chat_history.append({'role': 'assistant', 'content': response_message})
        return {"message": response_message, "webscraping": False}

    if query_lower in farewells:
        response_message = "You're welcome! Have a great day!"
        chat_history.append({'role': 'user', 'content': query})
        chat_history.append({'role': 'assistant', 'content': response_message})
        return {"message": response_message, "webscraping": False}

    # Define valid keywords for queries
    valid_keywords = ["nutrition", "diet", "medical diagnosis", "symptom", "treatment"]

    # Check if the query contains valid keywords; if not, respond with an error message.
    if check_query(query_lower) != "True":
        response_message = "Please ask me questions from nutritional content, diet plan, medical diagnosis."
        chat_history.append({'role': 'user', 'content': query})
        chat_history.append({'role': 'assistant', 'content': response_message})
        return {"message": response_message}

    # Check cache for repeated questions
    if query in response_cache:
        cached_response = response_cache[query]
        chat_history.append({'role': 'user', 'content': query})
        chat_history.append({'role': 'assistant', 'content': cached_response})
        
        return {
            "message": cached_response,
            "history": chat_history,
            "cachedResponse": True  # Indicate that this was a cached response
        }

    medical_keywords = ["diagnosis", "symptom", "disease", "treatment", "medicine", "medical condition", "patient"]
    diet_plan = ["diet plan"]

    if any(keyword in query_lower for keyword in medical_keywords):
        chat_history.append({'role': 'user', 'content': query})

        # Get available URLs for web scraping
        available_urls = get_query_urls(query)
        if not available_urls:
            response_message = "Sorry, I couldn't find relevant information for your medical query."
            chat_history.append({'role': 'assistant', 'content': response_message})
            return {"message": response_message, "webscraping": False}

        # Perform web scraping on available links
        await web_scrap_avail_links(available_urls)

        # Read the scraped content from file
        with open("scrapped.txt", "r", encoding="utf-8") as file:
            webscraped_content = file.read()

        # Read patient MRN (Medical Record Number) from file
        with open("mrn_number.txt", 'r') as mrn:
            patient_mrn = mrn.read()

        # Get patient data using the MRN
        patient_data = get_patient_by_mrn(patient_mrn)

        # Perform LLM inference using the patient data, web-scraped content, and query
        final_response = llm_infer(patient_data, webscraped_content, query)

        # Cache the final response for future queries
        response_cache[query] = final_response

        # Append the final response to the chat history
        chat_history.append({'role': 'assistant', 'content': final_response})

        # Return the final response
        return {
            "message": final_response,
            "webscraping": True,
            "history": chat_history,
            "cachedResponse": False  # Indicate that this was not a cached response
        }

    
    if any(keyword in query_lower for keyword in diet_plan):
            chat_history.append({'role': 'user', 'content': query})
            available_urls = get_query_urls(query)
            if not available_urls:
                response_message = "Sorry, I couldn't find relevant information for your medical query."
                chat_history.append({'role': 'assistant', 'content': response_message})
                return {"message": response_message}

            # Perform web scraping and generate response
            await web_scrap_avail_links(available_urls)
            with open("mrn_number.txt", 'r') as mrn:
                patient_mrn = mrn.read()
                
            with open("scrapped.txt", "r", encoding="utf-8") as file:
                webscraped_content = file.read()
                
            patient_data = get_patient_by_mrn(patient_mrn)
            
            final_response = diet_plan_call(patient_data, webscraped_content, query)
            
            # Cache the final response for future queries
            response_cache[query] = final_response
            
            chat_history.append({'role': 'assistant', 'content': final_response})

            return {
                "message": final_response,
                "sources": available_urls,
                "history": chat_history,
                "cachedResponse": False  # Indicate that this was not a cached response 
            }

    
    # If not a medical or diet plan query, proceed with RAG search 
    result = qa_chain({"query": query})

    
    if result['result'] == "I don't know.":
        prompt = create_prompt(query)
        
        groq_response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )
        
        formatted_response = groq_response.choices[0].message.content.replace("*", "\n")
        
        # Cache the Groq model's formatted response for future queries 
        response_cache[query] = formatted_response
        
        
        chat_history.append({'role': 'user', 'content': query})
        
        chat_history.append({'role': 'assistant', 'content': formatted_response})

        
        return {
            "message": formatted_response,
            "ragRetrieval": True,
            "history": chat_history,
            "cachedResponse": False  # Indicate that this was not a cached response 
        }

    
    chat_history.append({'role': 'user', 'content': query})
    
    chat_history.append({'role': 'assistant', 'content': result['result']})

    
    return {
         "message": result['result'],
         "sources": [doc.page_content for doc in result['source_documents']],
         "history": chat_history,
         "ragRetrieval": True,
         "cachedResponse": False  # Indicate that this was not a cached response 
     }


if __name__ == "__main__":
     import uvicorn
    
     uvicorn.run(app, host="0.0.0.0", port=8000) 
