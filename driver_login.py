# pages/driver_login.py
import streamlit as st
from db_utils import authenticate_user, init_db

st.set_page_config(page_title="Driver Login", layout="centered")

init_db()

st.title("🧑‍✈️ Driver Login - RelaxiTaxi")

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

if submitted:
    if email and password:
        user = authenticate_user("drivers", email, password)
        driver = authenticate_user("drivers", email, password)
        if driver:
            st.session_state["user_id"] = driver["id"]
            st.session_state["user_name"] = driver["name"]
            st.session_state["role"] = "driver"
            st.success("Logged in successfully!")
            st.switch_page("pages/driver_view.py")
            st.session_state["_rerun"] = True
            st.stop()

        if user:
            st.session_state["role"] = "driver"
            st.session_state["driver_id"] = user["id"]
            st.session_state["driver_name"] = user["name"]
            st.session_state["role"] = "driver"
            st.success(f"Welcome, {user['name']}!")
            st.switch_page("pages/driver_view.py")
        else:
            st.error("Invalid credentials. Please try again.")
    else:
        st.warning("Please enter both email and password.")

if st.button("Don't have an account? Register"):
    st.switch_page("pages/driver_register.py")
