# pages/rider_login.py
import streamlit as st
from db_utils import authenticate_user, init_db

# Initialize DB
init_db()

# --- CSS to hide sidebar ---
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state for role
if "role" not in st.session_state:
    st.session_state.role = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None

st.title("🚕 Rider Login")

# Login form
with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

    if submitted:
        user = authenticate_user("riders", email, password)
        if user:
            # Set session state
            st.session_state.role = "customer"
            st.session_state.user_id = user["id"]
            st.session_state.user_name = user["name"]

            st.success(f"Welcome, {user['name']}!")
            # Redirect to Book Ride page
            st.switch_page("pages/book_ride.py")  # <-- page name as in 'pages/book_ride.py'
        else:
            st.error("Invalid credentials. Please try again.")

# Switch to registration page
if st.button("Don't have an account? Register"):
    st.switch_page("pages/rider_register.py")  # <-- page name as in 'pages/rider_register.py'
