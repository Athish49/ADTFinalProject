import streamlit as st
import requests
import datetime
import pandas as pd
import json
import matplotlib.pyplot as plt

BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="Healthcare App", layout="centered")

# Load user config
@st.cache_data
def load_users():
    with open("users_config.json") as f:
        return json.load(f)["users"]

# Session state management
if "page" not in st.session_state:
    st.session_state.page = "login"
if "patient_id" not in st.session_state:
    st.session_state.patient_id = None
if "appointment_id" not in st.session_state:
    st.session_state.appointment_id = None
if "test_id" not in st.session_state:
    st.session_state.test_id = None
if "prescription_id" not in st.session_state:
    st.session_state.prescription_id = None
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "role" not in st.session_state:
    st.session_state.role = None

st.title("🏥 Cardiovascular Healthcare App")

# ------------------ LOGIN PAGE ------------------ #
if st.session_state.page == "login":
    st.subheader("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

    if login_btn:
        users = load_users()
        for user in users:
            if user["username"] == username and user["password"] == password:
                st.session_state.logged_in_user = username
                st.session_state.role = user["role"]
                st.session_state.page = "home"
                st.rerun()
        else:
            st.error("Invalid username or password.")

# ------------------ HOME PAGE ------------------ #
elif st.session_state.page == "home":
    if st.session_state.role == "admin":
        if st.button("Analyze All Records"):
            st.session_state.page = "analyze"
            st.rerun()

    with st.form("start_form"):
        option = st.radio("Are you a new or existing patient?", ["New Patient", "Existing Patient"])
        start = st.form_submit_button("Continue")

    if start:
        if option == "New Patient":
            st.session_state.page = "new_patient_personal"
        else:
            st.session_state.page = "existing_patient"
        st.rerun()

# ------------------ NEW PATIENT FLOW ------------------ #
elif st.session_state.page == "new_patient_personal":
    st.subheader("Enter Personal Details")
    with st.form("personal_form"):
        name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=0, step=1)
        gender = st.selectbox("Gender", ["Male", "Female"])
        height = st.number_input("Height (cm)", min_value=30.0)
        weight = st.number_input("Weight (kg)", min_value=1.0)
        submitted = st.form_submit_button("Submit Personal Info")

    gender = 1 if gender == "Male" else 2

    if submitted:
        payload = {"name": name, "age": age, "gender": gender, "height": height, "weight": weight}
        res = requests.post(f"{BASE_URL}/patients/new", json=payload)
        if res.status_code == 200:
            st.session_state.patient_id = res.json()["patient_id"]
            st.success(f"Patient created successfully. ID: {st.session_state.patient_id}")
            st.session_state.page = "new_patient_lifestyle"
            st.rerun()
        else:
            st.error(res.json()['detail'])

elif st.session_state.page == "new_patient_lifestyle":
    st.subheader("Lifestyle Info")
    with st.form("lifestyle_form"):
        smoke = st.radio("Do you smoke?", ["Yes", "No"])
        alco = st.radio("Do you consume alcohol?", ["Yes", "No"])
        active = st.radio("Are you physically active?", ["Yes", "No"])
        submitted2 = st.form_submit_button("Submit Lifestyle Info")

        smoke = 1 if smoke == "Yes" else 0
        alco = 1 if alco == "Yes" else 0
        active = 1 if active == "Yes" else 0

    if submitted2:
        payload = {"patient_id": st.session_state.patient_id, "smoke": smoke, "alco": alco, "active": active}
        res = requests.post(f"{BASE_URL}/patients/lifestyle", json=payload)
        if res.status_code == 200:
            st.success("Lifestyle data submitted.")
            st.session_state.page = "new_patient_appointment"
            st.rerun()
        else:
            st.error(res.json()['detail'])

elif st.session_state.page == "new_patient_appointment":
    st.subheader("Create Appointment")
    with st.form("appointment_form"):
        appt_type = st.selectbox("Type of Appointment", ["Initial Consult", "Follow-up", "Test Review"])
        appt_date = st.date_input("Appointment Date", value=datetime.date.today())
        submitted3 = st.form_submit_button("Book Appointment")

    if submitted3:
        payload = {"patient_id": st.session_state.patient_id, "appointment_type": appt_type, "appointment_date": str(appt_date)}
        res = requests.post(f"{BASE_URL}/appointments", json=payload)
        if res.status_code == 200:
            result = res.json()
            st.session_state.appointment_id = result['appointment_id']
            st.success(f"Appointment booked. ID: {st.session_state.appointment_id}, Doctor ID: {result['assigned_doctor_id']}")
            st.session_state.page = "new_patient_test"
            st.rerun()
        else:
            st.error(res.json()['detail'])

elif st.session_state.page == "new_patient_test":
    st.subheader("Enter Test Details")
    with st.form("test_form"):
        ap_hi = st.number_input("Systolic BP", min_value=80, max_value=300)
        ap_lo = st.number_input("Diastolic BP", min_value=40, max_value=200)
        chol = st.selectbox("Cholesterol Level", ["Normal", "Above Normal", "Well Above Normal"])
        gluc = st.selectbox("Glucose Level", ["Normal", "Above Normal", "Well Above Normal"])
        submitted4 = st.form_submit_button("Submit Test")

        chol = 1 if chol == "Normal" else 2 if chol == "Above Normal" else 3
        gluc = 1 if gluc == "Normal" else 2 if gluc == "Above Normal" else 3

    if submitted4:
        payload = {
            "appointment_id": st.session_state.appointment_id,
            "ap_hi": ap_hi,
            "ap_lo": ap_lo,
            "cholesterol": chol,
            "gluc": gluc
        }
        res = requests.post(f"{BASE_URL}/tests", json=payload)
        if res.status_code == 200:
            st.session_state.test_id = res.json()["test_id"]
            st.success(f"Test submitted. Test ID: {st.session_state.test_id}")
            st.session_state.page = "new_patient_prescription"
            st.rerun()
        else:
            st.error(res.json()['detail'])

elif st.session_state.page == "new_patient_prescription":    
    col1, col2, col3 = st.columns([4, 3.5, 5])

    # ------------------ Column 1: Prescription Form ------------------ #
    with col1:
        st.markdown("### Generate Prescription")
        with st.form("prescription_form"):
            medicine = st.text_input("Medicine Name")
            dosage = st.text_input("Dosage Instruction (e.g., 1x daily)")
            duration = st.number_input("Duration (days)", min_value=1)
            prescribed_date = st.date_input("Prescribed Date", value=datetime.date.today())
            submitted5 = st.form_submit_button("Generate Prescription")

        if submitted5:
            payload = {
                "appointment_id": st.session_state.appointment_id,
                "prescribed_date": str(prescribed_date),
                "medicine_name": medicine,
                "dosage": dosage,
                "duration_days": duration
            }
            res = requests.post(f"{BASE_URL}/prescriptions", json=payload)
            if res.status_code == 200:
                st.session_state.prescription_id = res.json()["prescription_id"]
                st.success(f"Prescription generated. ID: {st.session_state.prescription_id}")
                st.balloons()
            else:
                st.error(res.json()['detail'])

    # ------------------ Column 2: Patient Snapshot ------------------ #
    with col2:
        st.markdown("### Patient Snapshot")

        # Fetch patient details
        try:
            pat_res = requests.get(f"{BASE_URL}/patients/{st.session_state.patient_id}")
            if pat_res.status_code == 200:
                pdata = pat_res.json()
                patient = pdata["patient"]
                lifestyle = pdata["lifestyle"]

                st.markdown("**Basic Info**")
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Name: {patient['name']}", unsafe_allow_html=True)
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Age: {patient['age']}", unsafe_allow_html=True)
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Gender: {'Male' if patient['gender']==1 else 'Female'}", unsafe_allow_html=True)
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Height: {patient['height']} cm", unsafe_allow_html=True)
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Weight: {patient['weight']} kg", unsafe_allow_html=True)

                st.markdown("**Lifestyle**")
                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Smoker: {'Yes' if lifestyle['smoke'] else 'No'}")
                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Alcohol: {'Yes' if lifestyle['alco'] else 'No'}")
                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Active: {'Yes' if lifestyle['active'] else 'No'}")

            else:
                st.warning("Failed to load patient details.")

            # Fetch test details
            rec_res = requests.get(f"{BASE_URL}/records/{st.session_state.appointment_id}")
            if rec_res.status_code == 200:
                test = rec_res.json().get("test_details")
                if test:
                    st.markdown("**Test Results**")
                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Systolic BP: {test['ap_hi']}")
                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Diastolic BP: {test['ap_lo']}")
                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Cholesterol: {test['cholesterol']}")
                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Glucose: {test['gluc']}")
                else:
                    st.warning("No test data available.")
            else:
                st.warning("Failed to fetch test details.")

        except Exception as e:
            st.error(f"Error loading snapshot: {e}")

    # ------------------ Column 3: Health Charts ------------------ #
    with col3:
        st.markdown("### Test Result Trends by Age")

        try:
            response = requests.get(f"{BASE_URL}/get_analysis")
            if response.status_code == 200:
                df = pd.DataFrame(response.json())

                fig1, ax1 = plt.subplots()
                ax1.scatter(df["age"], df["ap_hi"], alpha=0.7)
                ax1.set_title("Age vs Systolic BP")
                st.pyplot(fig1, use_container_width=True)

                fig2, ax2 = plt.subplots()
                ax2.scatter(df["age"], df["ap_lo"], alpha=0.7)
                ax2.set_title("Age vs Diastolic BP")
                st.pyplot(fig2, use_container_width=True)

                fig3, ax3 = plt.subplots()
                ax3.scatter(df["age"], df["cholesterol"], alpha=0.7)
                ax3.set_title("Age vs Cholesterol")
                st.pyplot(fig3, use_container_width=True)

                fig4, ax4 = plt.subplots()
                ax4.scatter(df["age"], df["gluc"], alpha=0.7)
                ax4.set_title("Age vs Glucose")
                st.pyplot(fig4, use_container_width=True)

            else:
                st.error("Failed to fetch analysis data.")
        except Exception as e:
            st.error(f"Error loading charts: {e}")

# ------------------ EXISTING PATIENT FLOW ------------------ #
elif st.session_state.page == "existing_patient":
    st.subheader("Search Existing Patient")
    patient_id = st.text_input("Enter Patient ID")
    if st.button("Fetch Details"):
        res = requests.get(f"{BASE_URL}/patients/{patient_id}")
        if res.status_code == 200:
            data = res.json()
            patient = data["patient"]
            lifestyle = data["lifestyle"]

            st.markdown("## Patient Details")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Name:** {patient['name']}")
                st.markdown(f"**Patient ID:** {patient['patient_id']}")
                st.markdown(f"**Age:** {patient['age']}")
            with col2:
                st.markdown(f"**Gender:** {'Male' if patient['gender']==1 else 'Female' if patient['gender']==2 else 'Other'}")
                st.markdown(f"**Height:** {patient['height']} cm")
                st.markdown(f"**Weight:** {patient['weight']} kg")

            st.divider()

            st.markdown("## Lifestyle Info")
            col3, col4, col5 = st.columns(3)
            with col3:
                st.markdown(f"**Smoker:** {'Yes' if lifestyle['smoke'] else 'No'}")
            with col4:
                st.markdown(f"**Alcohol Use:** {'Yes' if lifestyle['alco'] else 'No'}")
            with col5:
                st.markdown(f"**Active:** {'Yes' if lifestyle['active'] else 'No'}")

            st.divider()

            st.markdown("## Appointments & Records")
            appt_res = requests.get(f"{BASE_URL}/appointments/{patient_id}")
            if appt_res.status_code == 200:
                appointments = appt_res.json()
                if not appointments:
                    st.info("No appointments found for this patient.")
                for i, appt in enumerate(appointments):
                    with st.expander(f"Appointment {i+1} - {appt['appointment_date']}"):
                        st.markdown(f"**Appointment ID:** {appt['appointment_id']}")
                        st.markdown(f"**Date:** {appt['appointment_date']}")
                        st.markdown(f"**Type:** {appt['appointment_type']}")

                        rec_res = requests.get(f"{BASE_URL}/records/{appt['appointment_id']}")
                        if rec_res.status_code == 200:
                            rec = rec_res.json()
                            test = rec["test_details"]
                            pres = rec["prescription"]

                            st.markdown("### Test Results")
                            if test:
                                t1, t2 = st.columns(2)
                                with t1:
                                    st.markdown(f"- **Test ID:** {test['test_id']}")
                                    st.markdown(f"- **Systolic BP (ap_hi):** {test['ap_hi']}")
                                    st.markdown(f"- **Diastolic BP (ap_lo):** {test['ap_lo']}")
                                with t2:
                                    st.markdown(f"- **Cholesterol:** {test['cholesterol']}")
                                    st.markdown(f"- **Glucose:** {test['gluc']}")
                            else:
                                st.warning("No test data found.")

                            st.markdown("### Prescription")
                            if pres:
                                st.markdown(f"- **Prescription ID:** {pres['prescription_id']}")
                                st.markdown(f"- **Medicine:** {pres['medicine_name']}")
                                st.markdown(f"- **Dosage:** {pres['dosage']}")
                                st.markdown(f"- **Duration:** {pres['duration_days']} days")
                                st.markdown(f"- **Prescribed Date:** {pres['prescribed_date']}")
                            else:
                                st.warning("No prescription found.")
                        else:
                            st.warning("No test/prescription record found.")
            else:
                st.warning("Unable to fetch appointments.")
        else:
            st.error(res.json()['detail'])

# ------------------ ANALYZE DATABASE PAGE ------------------ #
elif st.session_state.page == "analyze":
    st.header("Full Database Overview")
    st.markdown("Browse the latest records from each table in the healthcare database below:")

    table_endpoints = [
        ("Patient Details", "patient_details"),
        ("Patient Lifestyle", "patient_lifestyle"),
        ("Doctors", "doctors"),
        ("Appointments", "appointments"),
        ("Test Details", "test_details"),
        ("Prescriptions", "prescriptions"),
    ]

    for label, table in table_endpoints:
        st.subheader(label)
        try:
            response = requests.get(f"{BASE_URL}/fetch/{table}")
            if response.status_code == 200:
                records = response.json()
                if records:
                    df = pd.DataFrame(records)
                    st.dataframe(df, use_container_width=True, height=300)
                else:
                    st.info("No records found in this table.")
            else:
                st.error(f"Failed to fetch data for {label} (Status: {response.status_code})")
        except Exception as e:
            st.error(f"An error occurred while loading {label}: {str(e)}")


