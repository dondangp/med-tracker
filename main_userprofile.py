import streamlit as st
import pandas as pd
import json
# from fhirclient import client
# from fhirclient.models.patient import Patient

# Path to the NDJSON file
patient_file_path = "fhir_data/patient/Patient.ndjson"

# load and parse the data
def load_patient_data(file_path):
    with open(file_path, "r") as file:
        patients = [json.loads(line) for line in file]
    return patients

patients = load_patient_data(patient_file_path)

patient = patients[0]


settings,profile, help = st.tabs(["Settings", "Profile", "Help"])

st.title("Medication Adherence Tracker")
home, medications, analytics = st.tabs(["Home", "Medications", "Analytics"])


# Profile Tab - Mel 
with profile:
    st.header(f"{patient['name'][0]['given'][0]} {patient['name'][0]['family']}")
    
    # Profile Picture
    st.image("default_user.png", width=300)
    
    # Fetch FHIR data
    # patient_id = "12345"  # Replace with dynamic patient ID
    # patient = Patient.read(patient_id, smart.server)
    
    personal, contact, conditions, immunizations, allergies, family = st.tabs(
        ["Personal Information", "Contact Information", "Conditions", "Immunizations", "Allergies", "Family Contacts"]
    )
    
    with personal:
        st.header("Personal Information")
        st.text(f"Full Name: {patient['name'][0]['given'][0]} {patient['name'][0]['family']}")   
        st.text(f"Date of Birth: {patient.get('birthDate', 'Not Available')}")
        st.text("Age: 74")
        # st.text(f"Age: {patient.birthDate.isostring if patient.birthDate else 'Not Available'}")
        st.text(f"Gender Identity: {patient.get('gender', 'Not Available')}")
        st.text("Race: ")
        st.text("Ethnicity: ")
    
        st.text("Language: ")
        # st.text(f"Language: {', '.join([lang.text for lang in patient.communication]) if patient.communication else 'Not Available'}")
        st.text("Religion: ")

    with contact:
        st.header("Contact Information")
        address = patient.get("address", [{"text": "Not Available"}])
        st.text(f"Address: {address[0].get('text', 'Not Available')}")
        telecom = patient.get("telecom", [])
        email = "Not Available"
        for t in telecom:
            if t["system"] == "email":
                email = t["value"]
                break

        phone = "Not Available"
        for t in telecom:
            if t["system"] == "phone":
                phone = t["value"]
                break
            
        st.text(f"Email: {email}")
        st.text(f"Phone Number: {phone}")

    with conditions:
        st.header("Conditions/Current Health Issues")
        st.text("Not Available")  # You can populate this using Conditions FHIR resources

    with immunizations:
        st.header("Immunizations")
        st.text("Not Available")  # You can populate this using Immunization FHIR resources
        
    with allergies:
        st.header("Allergies")
        st.text("Not Available")  # You can populate this using AllergyIntolerance FHIR resources

    with family:
        st.header("Family Contacts")
        st.text("Not Available")  # You can populate this if using RelatedPerson FHIR resources
    