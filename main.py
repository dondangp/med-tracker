import streamlit as st
import pandas as pd
import json
import uuid
from datetime import datetime, date
import plotly.graph_objects as go
import smtplib


st.set_page_config(page_title="Medication Tracker", layout="centered", initial_sidebar_state="auto")

# File paths
patient_file_path = "fhir_data/patient/Patient.ndjson"
med_admin_path = "fhir_data/medication_administration/MedicationAdministration.ndjson"
med_request_path = "fhir_data/medication_request/MedicationRequest.ndjson"
editable_profile_path = "editable_profile.json"

# Define help section function
def help_section():
    st.title("Help & Support")
    
    st.markdown("## 📌 About the Medication Tracker")
    st.write(
        "This application helps patients track their medication intake, receive reminders, "
        "monitor side effects, and gain insights through reports and analytics. "
        "If you need assistance, check out the FAQs below or contact support."
    )

    st.markdown("## ❓ Frequently Asked Questions (FAQs)")

    with st.expander("How do I log my medication?"):
        st.write("Go to the 'Home' tab, and check the box next to your medication to mark it as taken.")

    with st.expander("How do I view my medications?"):
        st.write("Visit the 'Medications' tab to see all your active and inactive medications.")

    with st.expander("How is my adherence rate calculated?"):
        st.write("Your adherence rate is calculated based on the medications you've taken versus those you were scheduled to take. The app tracks this data and displays it as a percentage.")

    with st.expander("Can I update my personal information?"):
        st.write("Yes! Go to the 'Profile' tab to update your personal details.")

    with st.expander("What should I do if I experience side effects?"):
        st.write("Contact your healthcare provider immediately if you experience unexpected side effects.")

    with st.expander("How can I contact support?"):
        st.write("You can reach us at **support@medtracker.com** or call **+1-800-123-4567**.")

    st.markdown("## 📞 Contact & Support")
    st.info("For further assistance, email us at **support@medtracker.com** or call **+1-800-123-4567**.")

# Load patient
@st.cache_data
def load_patient():
    with open(patient_file_path, "r") as file:
        return json.loads(file.readline())

# Load NDJSON
def load_ndjson(path):
    try:
        with open(path, "r") as f:
            return [json.loads(line) for line in f]
    except:
        return []

# Get initial profile from patient
def get_initial_profile(p):
    return {
        "first_name": p['name'][0]['given'][0],
        "last_name": p['name'][0]['family'],
        "birth_date": p.get("birthDate", "N/A"),
        "gender": p.get("gender", "unknown"),
        "race": "",
        "ethnicity": "",
        "language": "",
        "religion": "",
        "address": p.get("address", [{}])[0].get("text", "N/A"),
        "email": next((t['value'] for t in p.get("telecom", []) if t['system'] == "email"), "N/A"),
        "phone": next((t['value'] for t in p.get("telecom", []) if t['system'] == "phone"), "N/A")
    }

# Check if medication was taken today
def was_medication_taken_today(med_id, administrations):
    today = date.today().isoformat()
    for admin in administrations:
        # Skip if not a MedicationAdministration
        if admin.get("resourceType") != "MedicationAdministration":
            continue
            
        # Get the medication ID from the administration
        admin_med_id = None
        for coding in admin.get("medicationCodeableConcept", {}).get("coding", []):
            if coding.get("system") == "http://www.nlm.nih.gov/research/umls/rxnorm":
                admin_med_id = coding.get("code")
                break
                
        if not admin_med_id:
            admin_med_id = admin.get("medicationCodeableConcept", {}).get("text", "")
            
        # Check if this is the medication we're looking for
        if admin_med_id != med_id:
            continue
            
        # Check if the administration was today
        admin_date = None
        try:
            admin_datetime = admin.get("effectiveDateTime", "")
            if admin_datetime:
                admin_date = admin_datetime.split("T")[0]  # Extract just the date part
        except:
            continue
            
        if admin_date == today:
            return True
            
    return False

# Load data
patient = load_patient()
med_requests = load_ndjson(med_request_path)
med_administrations = load_ndjson(med_admin_path)

# Session state
if "editable_profile" not in st.session_state:
    try:
        with open(editable_profile_path, "r") as f:
            st.session_state.editable_profile = json.load(f)
    except:
        st.session_state.editable_profile = get_initial_profile(patient)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = st.query_params.get("auth") == "true"

# Initialize taken medications in session state if not present
if "taken_medications" not in st.session_state:
    st.session_state.taken_medications = {}

# Get today's date for tracking
today = date.today().isoformat()
if "current_date" not in st.session_state:
    st.session_state.current_date = today
# If date changed, reset tracking
elif st.session_state.current_date != today:
    st.session_state.current_date = today
    st.session_state.taken_medications = {}

# Login
if not st.session_state.logged_in:
    st.title("🔐 Medication Tracker Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "tarunta" and password == "password123":
            st.session_state.logged_in = True
            st.query_params.update({"auth": "true"})
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

if st.button("Logout"):
    st.session_state.logged_in = False
    st.query_params.clear()
    st.rerun()

# Extract medications
active_medications, stopped_medications = [], []
for entry in med_requests:
    if entry.get("resourceType") != "MedicationRequest":
        continue
    med_text = entry.get("medicationCodeableConcept", {}).get("text", "Unknown")
    coding = next((c for c in entry.get("medicationCodeableConcept", {}).get("coding", []) if c.get("system") == "http://www.nlm.nih.gov/research/umls/rxnorm"), {})
    dosage = entry.get("dosageInstruction", [{}])[0].get("text", "Dosage not specified")
    prescriber = entry.get("requester", {}).get("display", "Unknown Prescriber")
    effective_date = entry.get("authoredOn", "Unknown Date")
    med = {
        "Medication": med_text,
        "Dosage": dosage,
        "Prescriber": prescriber,
        "Effective Date": effective_date,
        "RequestID": entry.get("id", ""),
        "RXnormCode": coding.get("code", ""),
        "RXnormSystem": coding.get("system", ""),
        "RXnormDisplay": coding.get("display", med_text),
        "Original": entry
    }
    (active_medications if entry.get("status") == "active" else stopped_medications).append(med)

# Custom CSS
st.markdown("""
<style>
    .stApp { background-color: white; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f8ff;
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
        color: #2c3e50;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e90ff !important;
        color: white !important;
    }
    p, span, label, .stMarkdown, div { color: #2c3e50 !important; }
    .medication-item {
        background-color: #f8f9fa;
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .taken-medication {
        background-color: #d4edda;
        border-color: #c3e6cb;
    }
</style>
""", unsafe_allow_html=True)

# Tabs
home, medications, analytics, profile, help = st.tabs(["\U0001F3E0 Home", "\U0001F48A Medications", "\U0001F4CA Analytics", "Profile", "\u2753 Help"])

# Home
with home:
    st.title("Medication Tracker App")
    st.subheader(f"Hello, {st.session_state.editable_profile['first_name']}!")
    st.subheader("Adherence Rate")
    fig = go.Figure(go.Pie(labels=["Progress", "Remaining"], values=[70, 30], hole=0.7, marker=dict(colors=["lightgreen", "lightgray"])))
    fig.update_layout(title="Progress: 70%", showlegend=False, width=500, height=500)
    st.plotly_chart(fig)

    # Email sending function
    def send_email():
        try:
            host = 'smtp.gmail.com'
            port = 587
            from_email = 'cs6440medicationtracker@gmail.com'
            to_email = 'ramongored@gmail.com'
            password = 'nobn kuta ecgz dkti'  
            
            message = """Subject: Mail sent using python
            
            Hi,
            
            Please check your medications.
            """
            smtp = smtplib.SMTP(host, port)
            smtp.ehlo()
            smtp.starttls()
            smtp.login(from_email, password)
            smtp.sendmail(from_email, to_email, message)
            smtp.quit()
            return "Email sent successfully!"
        except Exception as e:
            return f"Error: {e}"

    st.subheader("\u2705 Mark Active Medications as Administered")
    
    # Check for already taken medications today from database
    for med in active_medications:
        med_id = med["RXnormCode"] or med["Medication"]
        if med_id not in st.session_state.taken_medications:
            # Check if this medication was already taken today according to the database
            if was_medication_taken_today(med_id, med_administrations):
                st.session_state.taken_medications[med_id] = True
    
    for i, med in enumerate(active_medications):
        med_id = med["RXnormCode"] or med["Medication"]
        k = f"med_checkbox_{i}"
        
        # Get initial value for checkbox - True if already taken today
        initial_value = med_id in st.session_state.taken_medications and st.session_state.taken_medications[med_id]
        
        # Display checkbox with appropriate label
        label = f"{med['Medication']} ({med['Dosage']}) - RXnorm: {med['RXnormCode'] or 'N/A'}"
        if initial_value:
            label += " ✓ (Taken today)"
        
        # Create the checkbox
        checked = st.checkbox(label, value=initial_value, key=k)
        
        # If status changed from unchecked to checked
        if checked and not initial_value:
            # Record in session state
            st.session_state.taken_medications[med_id] = True
            
            # Create MedicationAdministration entry
            med_admin_entry = {
                "resourceType": "MedicationAdministration",
                "id": str(uuid.uuid4()),
                "status": "completed",
                "medicationCodeableConcept": {
                    "coding": [
                        {
                            "system": med['RXnormSystem'] or "http://www.nlm.nih.gov/research/umls/rxnorm",
                            "code": med['RXnormCode'] or "Unknown",
                            "display": med['RXnormDisplay'] or med['Medication']
                        }
                    ],
                    "text": med["Medication"]
                },
                "subject": med["Original"].get("subject", {"reference": f"Patient/{patient['id']}"}),
                "context": med["Original"].get("encounter", {"reference": f"Encounter/{str(uuid.uuid4())}"}),
                "effectiveDateTime": datetime.now().isoformat(),
                "reasonCode": med["Original"].get("reasonCode", [
                    {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/reason-medication-given",
                            "code": "b",
                            "display": "Given as Ordered"
                        }],
                        "text": "Self-administered medication"
                    }
                ]),
                "performer": [{"actor": {"display": "Patient"}}]
            }
            
            # Write to NDJSON file
            with open(med_admin_path, "a") as f:
                f.write(json.dumps(med_admin_entry) + "\n")
            
            # Reload administrations to update the in-memory list
            med_administrations.append(med_admin_entry)
            
            st.success(f"✅ Recorded: {med['Medication']}")
            
        # Update session state if checkbox was unchecked
        elif not checked and initial_value:
            st.session_state.taken_medications[med_id] = False
            st.warning(f"⚠️ Unmarked: {med['Medication']} - Note: the database record still exists")

    # Streamlit interface for email
    st.title("Send Test Email")
    if st.button("Send Email"):
        result = send_email()
        st.write(result)

# Medications
with medications:
    tab1, tab2 = st.tabs(["💊 Active Medications", "❌ Inactive Medications"])
    with tab1:
        for med in active_medications:
            med_id = med["RXnormCode"] or med["Medication"]
            taken_today = med_id in st.session_state.taken_medications and st.session_state.taken_medications[med_id]
            
            # Add a special class if taken today
            extra_class = "taken-medication" if taken_today else ""
            
            st.markdown(f"""
            <div class='medication-item {extra_class}'>
                <b>{med['Medication']}</b><br>
                <i>{med['Dosage']}</i><br>
                <span>Prescribed by: {med['Prescriber']}</span><br>
                <span>Effective Date: {med['Effective Date']}</span><br>
                <span>RXnorm Code: {med['RXnormCode'] or 'N/A'}</span>
                {f"<br><b>✓ Taken today</b>" if taken_today else ""}
            </div>
            """, unsafe_allow_html=True)
    with tab2:
        if stopped_medications:
            for med in stopped_medications:
                st.markdown(f"""
                <div class='medication-item'>
                    <b>{med['Medication']}</b><br>
                    <i>{med['Dosage']}</i><br>
                    <span>Prescribed by: {med['Prescriber']}</span><br>
                    <span>Effective Date: {med['Effective Date']}</span><br>
                    <span>RXnorm Code: {med['RXnormCode'] or 'N/A'}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No inactive medications found.")

# Analytics
with analytics:
    st.subheader("📊 Medication Adherence Analytics")
    data = pd.DataFrame({
        "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "Medication Taken (%)": [80, 95, 100, 60, 90, 100, 70]
    })
    data = data.set_index("Day").sort_index()
    st.bar_chart(data)

# Profile
with profile:
    if st.button("💾 Save Profile"):
        with open(editable_profile_path, "w") as f:
            json.dump(st.session_state.editable_profile, f, indent=2)
        st.success("Profile saved successfully.")

    tabs = st.tabs(["Personal Information", "Contact Information", "Conditions", "Immunizations", "Allergies", "Family Contacts"])
    with tabs[0]:
        p = st.session_state.editable_profile
        p["first_name"] = st.text_input("First Name", p["first_name"])
        p["last_name"] = st.text_input("Last Name", p["last_name"])
        p["birth_date"] = st.text_input("Date of Birth", p["birth_date"])
        p["gender"] = st.selectbox("Gender", ["male", "female", "other", "unknown"], index=["male", "female", "other", "unknown"].index(p["gender"]))
        p["race"] = st.text_input("Race", p["race"])
        p["ethnicity"] = st.text_input("Ethnicity", p["ethnicity"])
        p["language"] = st.text_input("Language", p["language"])
        p["religion"] = st.text_input("Religion", p["religion"])
    with tabs[1]:
        p["address"] = st.text_input("Address", p["address"])
        p["email"] = st.text_input("Email", p["email"])
        p["phone"] = st.text_input("Phone Number", p["phone"])
    with tabs[2]: st.text("Not Available")
    with tabs[3]: st.text("Not Available")
    with tabs[4]: st.text("Not Available")
    with tabs[5]: st.text("Not Available")

# Help
with help:
    help_section()