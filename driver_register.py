import streamlit as st
from db_utils import register_user, init_db

st.set_page_config(page_title="Driver Registration", layout="centered")

# Initialize DB
init_db()

st.title("🚖 Driver Registration - RelaxiTaxi")

with st.form("register_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    vehicle_no = st.text_input("Vehicle Number")
    license_no = st.text_input("License Number")

    submitted = st.form_submit_button("Register")

    if submitted:
        if name and email and password and vehicle_no and license_no:
            try:
                register_user("drivers", name, email, password, vehicle_no=vehicle_no, license_no=license_no)
                st.success("✅ Registration successful! Please log in now.")
                st.button("Go to Login", on_click=lambda: st.experimental_set_query_params(page="driver_login.py"))
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please fill in all fields.")
