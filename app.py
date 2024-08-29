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
import re

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
        self.greetings = ['hi', 'hello', 'hey', 'greetings', 'howdy', 'wassup']
        self.farewells = ['bye', 'goodbye', 'see you', 'farewell', 'thanks', 'thank you']
        
        # Initialize OpenAI model
        self.llm = OpenAI(model_name="gpt-4o-mini")
        
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

        # Create a prompt template for diet plan generation
        self.diet_plan_prompt = PromptTemplate(
            input_variables=["query"],
            template="{query}"
        )

        # Create an LLMChain for diet plan generation
        self.diet_plan_chain = LLMChain(llm=self.llm, prompt=self.diet_plan_prompt)

    def is_greeting(self, text):
        return any(text.lower().startswith(word) for word in self.greetings)

    def is_farewell(self, text):
        return any(word in text.lower().split() for word in self.farewells)
    
    def get_gem_response(self, input_prompt, image):
        model = gemini.GenerativeModel('gemini-pro-vision')
        response = model.generate_content([input_prompt, image[0]])
        return response.text

    def input_image_setup(self, uploaded_file):
        if uploaded_file is not None:
            # Read the file into bytes
            bytes_data = uploaded_file.getvalue()

            image_parts = [
                {
                    "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                    "data": bytes_data
                }
            ]
            return image_parts
        else:
            raise FileNotFoundError("OOPS ! ..... File not found")

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

    def is_diet_plan_query(self, query):
        keywords = ['diet plan', 'meal plan', 'food plan', 'nutrition plan', 'eating plan']
        conditions = ['having', 'diagnosed with', 'suffering from', 'with']
        regions = ['from', 'live in', 'based in']
        
        has_diet_keywords = any(keyword in query.lower() for keyword in keywords)
        has_condition = any(condition in query.lower() for condition in conditions)
        has_region = any(region in query.lower() for region in regions)
        has_age = bool(re.search(r'\d+\s*(?:year|yr)s?\s*old|(?:man|woman|boy|girl|person)', query.lower()))
        
        return has_diet_keywords and sum([has_condition, has_region, has_age]) >= 2

    def format_diet_plan_query(self, query):
        age_match = re.search(r'(\d+)\s*(?:year|yr)s?\s*old', query.lower())
        age = age_match.group(1) if age_match else "adult"
        
        gender_match = re.search(r'\b(man|woman|boy|girl|person)\b', query.lower())
        gender = gender_match.group(1) if gender_match else "person"
        
        gender_map = {"man": "adult male", "woman": "adult female", "boy": "young male", "girl": "young female", "person": "person"}
        gender = gender_map.get(gender, "person")
        
        condition_match = re.search(r'(?:having|diagnosed with|suffering from|with)\s+(\w+(?:\s+\w+)*)', query.lower())
        condition = condition_match.group(1) if condition_match else "no specific condition"
        
        region_match = re.search(r'(?:from|live in|based in)\s+(\w+)', query.lower())
        region = region_match.group(1) if region_match else "unspecified region"
        
        formatted_query = f"Please suggest a proper diet plan for a {age}-year-old {gender} with {condition} from {region}. The plan should include 3 meals a day [Breakfast, Lunch and Dinner] based on the regional cuisine."
        
        return formatted_query
    
    def format_output(self, output):
        #to format the resulted ouput spliting the ouput with ### to get the needed contents
        output = output.replace("**","")
        res = output.split("###")[1:-1]
        return "".join(res)

    def post(self):
        try:
            data = request.get_json()
            question = data.get('question', '').strip()
            
            if not question:
                return jsonify({"error": "No question provided"}), 400

            if self.is_greeting(question):
                return jsonify({"answer": "Hello! How can I assist you today? Feel free to ask about any meals, their nutritional information, or request a personalized diet plan."})

            if self.is_farewell(question):
                return jsonify({"answer": "Goodbye! If you have any more questions about foods or diet plans in the future, don't hesitate to ask."})

            # Check if the question is about a diet plan
            if self.is_diet_plan_query(question):
                formatted_query = self.format_diet_plan_query(question)
                diet_plan = self.diet_plan_chain.run(formatted_query)
                return jsonify({"answer": self.format_output(diet_plan)})

            # Check if the question is about a meal or specific food item
            if "eating" in question.lower() or any(food_word in question.lower() for food_word in ["meal", "dish", "cuisine"]):
                meal_response = self.process_meal_query(question)
                return jsonify({"answer": self.format_output(meal_response)})

            # If not a meal-specific query or diet plan request, use the general QA chain
            result = qa_chain({"query": question})
            
            if len(result['result']) < 20 or "I don't have" in result['result'].lower():
                # If the answer is too short or uncertain, try to get more specific information
                clarification_prompt = PromptTemplate(
                    input_variables=["question"],
                    template="The question is: {question}\nProvide a detailed answer about the nutritional content of this food item or ingredient. If exact information is not available, provide educated estimates based on similar foods. Include calorie content, macronutrients, and any significant micronutrients."
                )
                clarification_chain = LLMChain(llm=self.llm, prompt=clarification_prompt)
                clarified_response = clarification_chain.run(question)
                return jsonify({"answer": self.format_output(clarified_response)})

            return jsonify({"answer": self.format_output(result['result'])})

        except Exception as e:
            logging.error(f"Error processing request: {str(e)}")
            return jsonify({"error": "An error occurred while processing your request. Please try again or rephrase your question."})

api.add_resource(ChatbotAPI, '/api/chat')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
