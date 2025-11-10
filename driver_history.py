import streamlit as st
from db_utils import get_driver_history
from shared_state import get_app_state
import pandas as pd
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Shared state ---
state = get_app_state()

# --- Security check ---
if st.session_state.get("role") != "driver":
    st.error("You must be logged in as a driver to view ride history.")
    if st.button("Go to Login"):
        st.switch_page("pages/driver_login.py")
    st.stop()

st.title("👨‍✈️ Driver Ride History")

# --- Sign out ---
if st.button("Sign Out"):
    st.session_state.role = None
    st.switch_page("app.py")

# --- Fetch driver history ---
driver_id = int(st.session_state.user_id)
rides = get_driver_history(driver_id)

if not rides:
    st.info("No rides found yet.")
else:
    # Prepare DataFrame
    df = pd.DataFrame(rides)

    # Ensure ac exists
    if "ac" in df.columns:
        df["ac"] = df["ac"].apply(lambda x: "AC" if x else "Non-AC")
    else:
        df["ac"] = "Unknown"

    # Select relevant columns
    df_display = df[[
        "id", "rider_id", "start_location", "end_location",
        "distance_km", "fare", "ac", "status", "ride_time"
    ]]

    df_display = df_display.rename(columns={
        "id": "Ride ID",
        "rider_id": "Rider ID",
        "start_location": "Start",
        "end_location": "End",
        "distance_km": "Distance (km)",
        "fare": "Fare (₹)",
        "ac": "Type",
        "status": "Status",
        "ride_time": "Booked At"
    })

    st.dataframe(df_display, use_container_width=True)
