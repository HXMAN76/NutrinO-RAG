from flask import Flask, request, jsonify, render_template
from flask_restful import Api, Resource
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA, LLMChain
from langchain.prompts import PromptTemplate
import os
import logging
import google.generativeai as gemini
import base64

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
gemini.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)
api = Api(app)

# Load the persisted Chroma database
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(persist_directory="./hybrid_db", embedding_function=embeddings)

# Initialize language model
llm = OpenAI(model_name="gpt-4o-mini")
# Create a RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True
)

class ChatbotAPI(Resource):
    def __init__(self):
        def __init__(self):
            self.greetings = ['hi', 'hello', 'hey', 'greetings', 'howdy', 'wassup']
            self.farewells = ['bye', 'goodbye', 'see you', 'farewell', 'thanks', 'thank you']
            
            # Initialize OpenAI model
            self.llm =  OpenAI(model_name="gpt-4o-mini")
            
            # Create a prompt template for meal component identification
            self.meal_prompt = PromptTemplate(
                input_variables=["meal"],
                template = """
    Given the meal name "{meal}", break it down into its individual food components. 

    Please ensure the following:
    1. **Decomposition of Complex Ingredients**: If an ingredient typically combines multiple components (e.g., "Chilli coconut chutney"), list each component separately (e.g., "Chilli", "Coconut").
    2. **Granular Identification**: Break down complex dishes into their base components. For example, for "Biriyani," list all ingredients such as "onion, tomato, rice, chicken, spices, oil, ghee."
    3. **Common Ingredients**: Identify commonly used spices, oils, and base ingredients typical to the cuisine.
    4. **Component Focus**: If the meal includes specific types of vegetables, meats, or grains, ensure they are listed as individual components (e.g., "chicken, basmati rice, cumin, coriander").
    5. **Avoid Ambiguity**: Only list specific, identifiable components. Do not generalize ingredients (e.g., use "coriander seeds" instead of just "spices").
    6. **Order of Listing**: List the components in the order of their prominence or quantity in the meal.
    7. **Accuracy**: Ensure all listed components are specific and relevant to the meal.

    Return the components as a comma-separated list, and do not include any additional text or explanation.
    """

            )
            
            # Create an LLMChain for meal component identification
            self.meal_chain = LLMChain(llm=self.llm, prompt=self.meal_prompt)

    def get_gem_response(self, input_prompt, image_data):
        model = gemini.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([input_prompt, image_data])
        return response.text

    def process_image(self, image_data):
        input_prompt = """
        You are an expert nutritionist. Analyze the food item(s) in this image and provide:

        1. A list of all food items visible
        2. Estimated total calories
        3. Nutritional breakdown including carbohydrates, proteins, fats, fibers, and sugars
        4. Whether the meal is generally considered healthy or not
        5. Any additional nutritional advice or insights

        Present the information in a clear, structured format.
        """
        return self.get_gem_response(input_prompt, image_data)

    def post(self):
        try:
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename:
                    image_data = {
                        "mime_type": file.content_type,
                        "data": base64.b64encode(file.read()).decode('utf-8')
                    }
                    response = self.process_image(image_data)
                    return jsonify({"answer": response})

            data = request.get_json()
            question = data.get('question', '').strip()
            
            if not question:
                return jsonify({"error": "No question provided"}), 400

            if self.is_greeting(question):
                return jsonify({"answer": "Hello! How can I assist you today? Feel free to ask about any meals and their nutritional information."})

            if self.is_farewell(question):
                return jsonify({"answer": "Goodbye! If you have any more questions about foods in the future, don't hesitate to ask."})

            # Check if the question is about a meal or specific food item
            if "eating" in question.lower() or any(food_word in question.lower() for food_word in ["food", "meal", "dish", "cuisine"]):
                meal_response = self.process_meal_query(question)
                return jsonify({"answer": meal_response})

            # If not a meal-specific query, use the general QA chain
            result = qa_chain({"query": question})
            
            if len(result['result']) < 20 or "I don't have" in result['result'].lower():
                # If the answer is too short or uncertain, try to get more specific information
                clarification_prompt = PromptTemplate(
                    input_variables=["question"],
                    template="The question is: {question}\nProvide a detailed answer about the nutritional content of this food item or ingredient. If exact information is not available, provide educated estimates based on similar foods. Include calorie content, macronutrients, and any significant micronutrients."
                )
                clarification_chain = LLMChain(llm=self.llm, prompt=clarification_prompt)
                clarified_response = clarification_chain.run(question)
                return jsonify({"answer": clarified_response})

            return jsonify({"answer": result['result']})

        except Exception as e:
            logging.error(f"Error processing request: {str(e)}")
            return jsonify({"error": "An error occurred while processing your request. Please try again or rephrase your question."})

        except Exception as e:
            logging.error(f"Error processing request: {str(e)}")
            return jsonify({"error": "An error occurred while processing your request. Please try again."})

api.add_resource(ChatbotAPI, '/api/chat')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
