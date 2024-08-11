from flask import Flask, request, jsonify, render_template
from flask_restful import Api, Resource
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA, LLMChain
from langchain.prompts import PromptTemplate
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

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

    def is_greeting(self, text):
        return any(text.lower().startswith(word) for word in self.greetings)

    def is_farewell(self, text):
        return any(word in text.lower().split() for word in self.farewells)

    def process_meal_query(self, question):
        # Extract the meal name from the question
        meal_name = question.split("eating")[-1].strip().split(".")[0].strip()
        
        # Use the meal_chain to identify food components
        components = self.meal_chain.run(meal_name).split(', ')
        
        # Query the database for each component
        nutritional_info = []
        for component in components:
            result = qa_chain({"query": f"Detailed nutrition facts for {component}"})
            nutritional_info.append(f"{component}: {result['result']}")
        
        # Use OpenAI to generate a comprehensive response
        response_prompt = PromptTemplate(
            input_variables=["question", "components", "nutritional_info"],
            template="""Format your response as follows:

Nutritional Information for [Food Item]
Serving Size: [Specify a standard serving size]

Caloric Content:
- Calories: [Amount]

Macronutrients:
1. Carbohydrates: [Amount]
2. Proteins: [Amount]
3. Fats: [Amount]

Micronutrients:
[List any significant vitamins and minerals]"""
        )
        response_chain = LLMChain(llm=self.llm, prompt=response_prompt)
        
        final_response = response_chain.run({
            "question": question,
            "components": ", ".join(components),
            "nutritional_info": "\n".join(nutritional_info)
        })
        
        return final_response

    def post(self):
        try:
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

api.add_resource(ChatbotAPI, '/api/chat')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)



