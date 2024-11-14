import streamlit as st
from pymongo import MongoClient
import os
import time
import subprocess
import platform
from dotenv import load_dotenv

# Page configuration
st.set_page_config(
    page_title="Medical Records System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with dark blue theme
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #1e2a3a;
        --secondary-color: #ffffff;
        --accent-color: #3699FF;
        --background-light: #f8f9fa;
        --text-color: #ffffff;
    }
    
    .main {
        padding: 2rem;
        background-color: #f5f6f8;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: var(--accent-color);
        color: white;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: violet;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(54, 153, 255, 0.2);
    }
    
    .header-container {
        background-color: var(--primary-color);
        color: var(--text-color);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .form-container {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border: 1px solid #e0e0e0;
    }
    
    .stTextInput > div > div {
        background-color: white;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
    }
    
    .stTextInput > div > div:focus-within {
        border-color: var(--accent-color);
        box-shadow: 0 0 0 2px rgba(54, 153, 255, 0.2);
    }
    
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
    }
    
    h1, h2, h3 {
        color: var(--primary-color);
    }
    
    .header-container h1 {
        color: var(--text-color);
    }
    
    .stTab {
        background-color: var(--primary-color);
        color: var(--text-color);
    }
    
    .success-message {
        background-color: #28a745;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .warning-message {
        background-color: #ffc107;
        color: #000;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Card-like sections */
    .section-card {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .section-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    /* Custom progress bar */
    .stProgress > div > div {
        background-color: var(--accent-color);
    }
    
    /* Custom tabs */
    .stTabs > div > div > div {
        background-color: var(--primary-color);
        color: white;
        border-radius: 5px 5px 0 0;
    }
    
    .stTabs > div > div > div[data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs > div > div > div[data-baseweb="tab"] {
        background-color: transparent;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
    }
    
    .stTabs > div > div > div[data-baseweb="tab"][aria-selected="true"] {
        background-color: var(--accent-color);
    }
    </style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# MongoDB Atlas connection
connection_url = os.getenv("MONGO_DB_CLIENT")
client = MongoClient(connection_url)
db = client["medical_records_db"]
collection = db["patients"]

# Utility functions
def get_patient_by_mrn(mrn_number):
    return collection.find_one({"MRN Number": mrn_number})

def save_patient_data(patient_data):
    collection.insert_one(patient_data)

def update_patient_data(mrn_number, updated_data):
    collection.update_one({"MRN Number": mrn_number}, {"$set": updated_data})

def activate_chat_application():
    st.write("Activating chat application...")
    
    # Commands for the chat application
    command_uvicorn = ["uvicorn", "main:app", "--reload"]
    command_npm = ["npm", "start"]

    if platform.system() == "Windows":
        process_uvicorn = subprocess.Popen(command_uvicorn, cwd="./", creationflags=subprocess.CREATE_NEW_CONSOLE, shell=True)
        time.sleep(10)
        process_npm  = subprocess.Popen(command_npm, cwd="./", creationflags=subprocess.CREATE_NEW_CONSOLE, shell=True)

    else:
        process_uvicorn = subprocess.Popen(command_uvicorn, cwd="./")
        time.sleep(10)
        process_npm  = subprocess.Popen(command_npm, cwd="../")

    if process_uvicorn.poll() is None and process_npm.poll() is None:
        st.write("Chat application started successfully.")
    else:
        st.write("Failed to start the chat application. Please check the terminal for errors.")
# Initialize session state
if "create_new_patient" not in st.session_state:
    st.session_state.create_new_patient = False

# Main UI
def main():
    with st.container():
        st.markdown('<div class="header-container">', unsafe_allow_html=True)
        st.title("🏥 Medical Records Management System")
        st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state.create_new_patient:
        display_main_form()
    else:
        display_new_patient_form()

def display_main_form():
    with st.container():
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.subheader("📝 Patient Information")
        
        mrd_number_input = st.text_input("Enter MRN Number", placeholder="e.g., MRN123456")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🔎 Search Patient Details"):
                if mrd_number_input:
                    patient_data = get_patient_by_mrn(mrd_number_input)
                    if patient_data:
                        display_patient_details(patient_data)
                    else:
                        st.warning("Patient not found. Would you like to create a new record?")
                else:
                    st.warning("Please enter an MRN number")
        
        with col2:
            if st.button("💬 Open Chat"):
                if mrd_number_input:
                    patient_data = get_patient_by_mrn(mrd_number_input)
                    if patient_data:
                        activate_chat_application()
                    else:
                        st.warning("Invalid MRN number")
                else:
                    st.warning("Please enter an MRN number")
        
        with col3:
            if st.button("➕ Create New Patient"):
                st.session_state.create_new_patient = True
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def display_patient_details(patient_data):
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.subheader(f"Patient Details: {patient_data['Name']}")
    
    # Basic Information
    st.markdown("### Basic Information")
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Patient Name", value=patient_data.get("Name", ""))
        patient_age = st.number_input("Age", value=int(patient_data.get("Age", 0)), min_value=0, max_value=120)
        patient_email = st.text_input("Email Address", value=patient_data.get("Email", ""))
    with col2:
        patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                    index=["Male", "Female", "Other"].index(patient_data.get("Gender", "Other")))
        patient_phone = st.text_input("Phone Number", value=patient_data.get("Phone", ""))
        patient_occupation = st.text_input("Occupation", value=patient_data.get("Occupation", ""))

    # Medical Information
    st.markdown("### Medical Information")
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Weight (kg)", value=float(patient_data.get("Weight", 0.0)), min_value=0.0)
        weight_changes = st.text_area("Weight Changes", value=patient_data.get("Weight Changes", ""))
        specific_diet = st.text_area("Specific Diet", value=patient_data.get("Specific Diet", ""))
    with col2:
        food_intolerances = st.text_area("Food Intolerances/Allergies", 
                                        value=patient_data.get("Food Intolerances/Allergies", ""))
        on_medications = st.text_area("Current Medications", value=patient_data.get("On Medications", ""))
        other_medical_history = st.text_area("Other Medical History", 
                                           value=patient_data.get("Other Medical History", ""))

    # Health Information
    st.markdown("### Health Information")
    col1, col2 = st.columns(2)
    with col1:
        other_health_issues = st.text_area("Other Health Issues", 
                                         value=patient_data.get("Other Health Issues", ""))
        physical_activity_type = st.text_input("Physical Activity Type", 
                                             value=patient_data.get("Physical Activity Type", ""))
        physical_activity_duration = st.number_input("Physical Activity Duration (minutes/day)", 
                                                   value=int(patient_data.get("Physical Activity Duration (minutes/day)", 0)),
                                                   min_value=0)
    with col2:
        diet_type = st.text_input("Diet Type", value=patient_data.get("Diet Type", ""))
        dietary_restrictions = st.text_area("Dietary Restrictions", 
                                          value=patient_data.get("Dietary Restrictions", ""))
        preferred_cuisine = st.multiselect("Preferred Cuisine", 
                                         ["Indian", "Continental", "Chinese", "Italian", "Mexican", "Other"],
                                         default=patient_data.get("Preferred Cuisine", []))

    if st.button("💾 Update Patient Data"):
        updated_data = {
            "Name": patient_name,
            "Age": patient_age,
            "Gender": patient_gender,
            "Email": patient_email,
            "Phone": patient_phone,
            "Occupation": patient_occupation,
            "Weight": weight,
            "Weight Changes": weight_changes,
            "Specific Diet": specific_diet,
            "Food Intolerances/Allergies": food_intolerances,
            "On Medications": on_medications,
            "Other Medical History": other_medical_history,
            "Other Health Issues": other_health_issues,
            "Physical Activity Type": physical_activity_type,
            "Physical Activity Duration (minutes/day)": physical_activity_duration,
            "Diet Type": diet_type,
            "Dietary Restrictions": dietary_restrictions,
            "Preferred Cuisine": preferred_cuisine
        }
        update_patient_data(patient_data["MRN Number"], updated_data)
        st.success("Patient data updated successfully!")
        time.sleep(2)
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def display_new_patient_form():
    with st.container():
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.subheader("➕ Create New Patient Record")
        
        # Basic Information
        st.markdown("### Basic Information")
        col1, col2 = st.columns(2)
        with col1:
            mrn_number = st.text_input("MRN Number", placeholder="e.g., MRN123456")
            patient_name = st.text_input("Patient Name")
            patient_age = st.number_input("Age", min_value=0, max_value=120)
        with col2:
            patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            patient_email = st.text_input("Email Address")
            patient_phone = st.text_input("Phone Number")
        
        patient_occupation = st.text_input("Occupation")

        # Medical Information
        st.markdown("### Medical Information")
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
            weight_changes = st.text_area("Weight Changes")
            specific_diet = st.text_area("Specific Diet")
        with col2:
            food_intolerances = st.text_area("Food Intolerances/Allergies")
            on_medications = st.text_area("Current Medications")
            other_medical_history = st.text_area("Other Medical History")

        # Health Information
        st.markdown("### Health Information")
        col1, col2 = st.columns(2)
        with col1:
            other_health_issues = st.text_area("Other Health Issues")
            physical_activity_type = st.text_input("Physical Activity Type")
            physical_activity_duration = st.number_input("Physical Activity Duration (minutes/day)", min_value=0)
        with col2:
            diet_type = st.text_input("Diet Type")
            dietary_restrictions = st.text_area("Dietary Restrictions")
            preferred_cuisine = st.multiselect("Preferred Cuisine", 
                                             ["Indian", "Continental", "Chinese", "Italian", "Mexican", "Other"])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Patient Data"):
                if mrn_number:
                    new_data = {
                        "MRN Number": mrn_number,
                        "Name": patient_name,
                        "Age": patient_age,
                        "Gender": patient_gender,
                        "Email": patient_email,
                        "Phone": patient_phone,
                        "Occupation": patient_occupation,
                        "Weight": weight,
                        "Weight Changes": weight_changes,
                        "Specific Diet": specific_diet,
                        "Food Intolerances/Allergies": food_intolerances,
                        "On Medications": on_medications,
                        "Other Medical History": other_medical_history,
                        "Other Health Issues": other_health_issues,
                        "Physical Activity Type": physical_activity_type,
                        "Physical Activity Duration (minutes/day)": physical_activity_duration,
                        "Diet Type": diet_type,
                        "Dietary Restrictions": dietary_restrictions,
                        "Preferred Cuisine": preferred_cuisine
                    }
                    save_patient_data(new_data)
                    st.success("New patient data saved successfully!")
                    st.session_state.create_new_patient = False
                    time.sleep(2)
                    st.rerun()
                else:
                    st.warning("Please enter an MRN Number")
        
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.create_new_patient = False
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

# import streamlit as st
# from pymongo import MongoClient
# import os
# import time
# import subprocess
# import platform
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # MongoDB Atlas connection
# connection_url = os.getenv("MONGO_DB_CLIENT")
# client = MongoClient(connection_url)
# db = client["medical_records_db"]  # Use your database name
# collection = db["patients"]  # Use your collection name

# # Utility function to find patient by MRN
# def get_patient_by_mrn(mrn_number):
#     return collection.find_one({"MRN Number": mrn_number})

# # Save new patient data to MongoDB
# def save_patient_data(patient_data):
#     collection.insert_one(patient_data)

# # Update patient data in MongoDB
# def update_patient_data(mrn_number, updated_data):
#     collection.update_one({"MRN Number": mrn_number}, {"$set": updated_data})

# # Function to activate chat application
# def activate_chat_application():
#     st.write("Activating chat application...")
    
#     # Commands for the chat application
#     command_uvicorn = ["uvicorn", "main:app", "--reload"]
#     command_npm = ["npm", "start"]

#     if platform.system() == "Windows":
#         process_uvicorn = subprocess.Popen(command_uvicorn, cwd="./", creationflags=subprocess.CREATE_NEW_CONSOLE, shell=True)
#         time.sleep(10)
#         process_npm  = subprocess.Popen(command_npm, cwd="./", creationflags=subprocess.CREATE_NEW_CONSOLE, shell=True)

#     else:
#         process_uvicorn = subprocess.Popen(command_uvicorn, cwd="./")
#         time.sleep(10)
#         process_npm  = subprocess.Popen(command_npm, cwd="../")

#     if process_uvicorn.poll() is None and process_npm.poll() is None:
#         st.write("Chat application started successfully.")
#     else:
#         st.write("Failed to start the chat application. Please check the terminal for errors.")

# # Streamlit session state
# if "create_new_patient" not in st.session_state:
#     st.session_state.create_new_patient = False

# # First page to enter MRN number
# st.title("Patient Data Collection Form")

# if not st.session_state.create_new_patient:
#     st.header("Enter MRN Number")
#     mrn_number_input = st.text_input("MRN Number")
    
#     with open ("mrn_number.txt", "w") as mrn:
#         mrn.write(mrn_number_input)

#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("Chat Application"):
#             if mrn_number_input:
#                 patient_data = get_patient_by_mrn(mrn_number_input)
#                 if patient_data:
#                     activate_chat_application()
#                 else:
#                     st.warning("Check your MRN number in order to access the chat application.")
#             else:
#                 st.warning("Check your MRN number in order to access the chat application.")

#         if st.button("Submit MRN Number", key="submit_mrn_number"):
#             if mrn_number_input:
#                 # Check if MRN exists in MongoDB
#                 patient_data = get_patient_by_mrn(mrn_number_input)
#                 if patient_data:
#                     st.success("Patient found in the system.")
                    
#                     # Display the existing data and allow updates
#                     st.header("Update Patient Information")
#                     patient_name = st.text_input("Patient Name", patient_data["Name"])
#                     patient_age = st.number_input("Age", min_value=0, max_value=120, step=1, value=int(patient_data["Age"]))
#                     patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(patient_data["Gender"]))
#                     patient_email = st.text_input("Email Address", patient_data["Email"])
#                     patient_phone = st.text_input("Phone Number", patient_data["Phone"])
#                     patient_occupation = st.text_input("Occupation", patient_data["Occupation"])
#                     weight = st.number_input("Weight", min_value=0.0, value=float(patient_data["Weight"]))
#                     weight_changes = st.text_input("Weight Changes", value=patient_data["Weight Changes"])
#                     specific_diet = st.text_input("Specific Diet", value=patient_data["Specific Diet"])
#                     food_intolerances = st.text_input("Food Intolerances/Allergies", value=patient_data["Food Intolerances/Allergies"])
#                     on_medications = st.text_input("On Medications", value=patient_data["On Medications"])
#                     other_medical_history = st.text_input("Other Medical History", value=patient_data["Other Medical History"])
#                     other_health_issues = st.text_input("Other Health Issues", value=patient_data["Other Health Issues"])
#                     physical_activity_type = st.text_input("Physical Activity Type", value=patient_data["Physical Activity Type"])
#                     physical_activity_duration = st.number_input("Physical Activity Duration (minutes/day)", min_value=0, value=int(patient_data["Physical Activity Duration (minutes/day)"]))
#                     diet_type = st.text_input("Diet Type", value=patient_data["Diet Type"])
#                     dietary_restrictions = st.text_input("Dietary Restrictions", value=patient_data["Dietary Restrictions"])
#                     preferred_cuisine = st.text_input("Preferred Cuisine", value=patient_data["Preferred Cuisine"])
#                     other_conditions = st.text_input("Other Conditions", value=patient_data["Other Conditions"])

#                     if st.button("Update Patient Data", key="update_patient_data"):
#                         # Prepare the updated data dictionary
#                         updated_data = {
#                             "Name": patient_name,
#                             "Age": patient_age,
#                             "Gender": patient_gender,
#                             "Email": patient_email,
#                             "Phone": patient_phone,
#                             "Occupation": patient_occupation,
#                             "Weight": weight,
#                             "Weight Changes": weight_changes,
#                             "Specific Diet": specific_diet,
#                             "Food Intolerances/Allergies": food_intolerances,
#                             "On Medications": on_medications,
#                             "Other Medical History": other_medical_history,
#                             "Other Health Issues": other_health_issues,
#                             "Physical Activity Type": physical_activity_type,
#                             "Physical Activity Duration (minutes/day)": physical_activity_duration,
#                             "Diet Type": diet_type,
#                             "Dietary Restrictions": dietary_restrictions,
#                             "Preferred Cuisine": preferred_cuisine,
#                             "Other Conditions": other_conditions
#                         }
#                         update_patient_data(mrn_number_input, updated_data)
#                         st.success("Patient data updated successfully!")
#                         st.write("Updated Patient Data:")
#                         st.write(updated_data)
#                 else:
#                     st.warning("MRD number not found. Would you like to create a new patient profile?")
    
#     with col2:
#         if st.button("Create New Patient", key="create_new_patient_2"):
#             st.session_state.create_new_patient = True
#             st.rerun()

# if st.session_state.create_new_patient:
#     st.header("Create New Patient Profile")
#     mrn_number = st.text_input("MRD Number")
#     patient_name = st.text_input("Patient Name")
#     patient_age = st.number_input("Age", min_value=0, max_value=120, step=1)
#     patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
#     patient_email = st.text_input("Email Address")
#     patient_phone = st.text_input("Phone Number")
#     patient_occupation = st.text_input("Occupation")

#     # Collect medical information
#     st.header("Medical Information")
#     weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
#     weight_changes = st.text_area("Weight Changes", help="Describe any recent weight changes")
#     specific_diet = st.text_area("Specific Diet", help="If the patient is following any specific diet, mention it here")
#     food_intolerances = st.text_area("Food Intolerances/Allergies", help="List any known food intolerances or allergies")
#     on_medications = st.text_area("Current Medications", help="List any medications the patient is currently taking")
#     other_medical_history = st.text_area("Other Medical History", help="Provide details of any other relevant medical history")

#     # Comorbidities/Health Issues
#     st.header("Comorbidities / Health Issues")
#     other_health_issues = st.text_area("Other Health Issues (please specify)")

#     # Physical Activity
#     st.header("Physical Activity")
#     physical_activity_type = st.text_area("Type of Physical Activity", help="Describe the type of physical activity")
#     physical_activity_duration = st.number_input("Duration of Physical Activity (minutes per day)", min_value=0)

#     # Dietary Preferences
#     st.header("Dietary Preferences")
#     diet_type = st.text_area("Type of Diet", help="Mention the type of diet the patient follows (e.g., vegetarian, non-vegetarian)")
#     dietary_restrictions = st.text_area("Dietary Restrictions", help="Specify any dietary restrictions")
#     preferred_cuisine = st.multiselect("Preferred Cuisine", ["Indian", "Continental", "Chinese", "Italian", "Mexican", "Other"])

#     other_conditions = st.text_area("Other Conditions", help="Mention any other conditions not covered above")

#     if st.button("Save Patient Data"):
#         if mrn_number:
#             new_data = {
#                 "MRN Number": mrn_number,
#                 "Name": patient_name,
#                 "Age": patient_age,
#                 "Gender": patient_gender,
#                 "Email": patient_email,
#                 "Phone": patient_phone,
#                 "Occupation": patient_occupation,
#                 "Weight": weight,
#                 "Weight Changes": weight_changes,
#                 "Specific Diet": specific_diet,
#                 "Food Intolerances/Allergies": food_intolerances,
#                 "On Medications": on_medications,
#                 "Other Medical History": other_medical_history,
#                 "Other Health Issues": other_health_issues,
#                 "Physical Activity Type": physical_activity_type,
#                 "Physical Activity Duration (minutes/day)": physical_activity_duration,
#                 "Diet Type": diet_type,
#                 "Dietary Restrictions": dietary_restrictions,
#                 "Preferred Cuisine": preferred_cuisine,
#                 "Other Conditions": other_conditions
#             }
#             save_patient_data(new_data)
#             st.success("New patient data saved successfully!")
#             st.session_state.create_new_patient = False  # Reset the session state
#             st.experimental_rerun()
#         else:
#             st.warning("Please enter an MRN Number to save the new patient data.")