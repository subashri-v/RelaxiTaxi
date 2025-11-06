import streamlit as st

st.set_page_config(
    page_title="Welcome to RelaxiTaxi",
    layout="centered",
)

# --- CSS to hide the sidebar ---
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

def set_role(role):
    st.session_state.role = role

st.title("🚕 Welcome to RelaxiTaxi")
st.markdown("Please select your role to continue.")

col1, col2 = st.columns(2)

with col1:
    st.image("https://icon-library.com/images/user-icon-png/user-icon-png-13.jpg", width=150)
    if st.button("I'm a Customer", use_container_width=True):
        set_role("customer")
        st.switch_page("pages/book_ride.py")

with col2:
    st.image("https://cdn-icons-png.flaticon.com/512/1378/1378645.png", width=150)
    if st.button("I'm a Driver", use_container_width=True):
        set_role("driver")
        st.switch_page("pages/driver_view.py")