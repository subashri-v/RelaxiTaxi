import streamlit as st
import folium
from streamlit_folium import st_folium
import time
from shared_state import get_app_state
from db_utils import update_ride_status, accept_ride, get_driver_history

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Shared state
state = get_app_state()

# --- CSS hide sidebar ---
st.markdown("""
<style>
[data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# Security check
if st.session_state.get("role") != "driver":
    st.error("You must be logged in as a driver.")
    if st.button("Go to Login"):
        st.switch_page("pages/driver_login.py")
    st.stop()

# Header
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.title("👨‍✈️ Driver Portal")
with col2:
    if st.button("Sign Out"):
        st.session_state.role = None
        st.switch_page("app.py")



# Driver History
if st.button("History"):
    st.switch_page("pages/driver_history.py")


# --- Check booking ---
if not state.get("booking"):
    st.info("No active ride requests. Waiting...")
    time.sleep(5)
    st.rerun()

booking = state["booking"]
ride_id = booking["ride_id"]
start = state["distance_data"]["start_coords"]
end = state["distance_data"]["end_coords"]

# Pending ride
if booking["status"] == "pending":
    st.subheader("New Ride Request!")
    st.markdown(f"**From:** {state['distance_data']['start']}")
    st.markdown(f"**To:** {state['distance_data']['end']}")
    st.markdown(f"**Fare:** ₹{booking['fare']:.2f}")

    if st.button("✅ Accept Ride"):
        # Update state
        booking["status"] = "accepted"
        booking["driver_id"] = st.session_state.user_id
        booking["driver"] = st.session_state.user_name
        # Update DB
        accept_ride(ride_id, st.session_state.user_id)

        st.rerun()

# Active ride
elif booking["status"] == "accepted":
    st.subheader(f"On-going Ride to {state['distance_data']['end']}")
    st.success(f"Pickup: {state['distance_data']['start']} | Dropoff: {state['distance_data']['end']}")

    progress = state.get("ride_progress", 0.0)

    # Driver controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚗 Move Forward"):
            progress = min(1.0, progress + 0.25)
            state["ride_progress"] = progress
            st.rerun()
    with col2:
        if progress > 0.0:
            if st.button("🏁 Complete Ride"):
                st.success("Ride Completed! 🎉")
                state["booking"] = None
                state["ride_progress"] = 0.0
                state["distance_data"] = None
                st.rerun()
    with col3:
        if progress == 0.0:
            if st.button("🚫 Cancel Ride"):
                state["booking"] = None
                state["ride_progress"] = 0.0
                state["distance_data"] = None
                st.warning("Ride Cancelled")
                st.rerun()

    # Progress info
    if progress == 0.0:
        st.info("On the way to pickup...")
    elif progress < 1.0:
        st.info("Ride in progress...")
    st.progress(progress)

    # Map
    curr_lat = start[0] + progress * (end[0] - start[0])
    curr_lon = start[1] + progress * (end[1] - start[1])
    curr_location = (curr_lat, curr_lon)

    m = folium.Map(location=curr_location, zoom_start=13)
    folium.Marker(start, tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(end, tooltip="Destination", icon=folium.Icon(color="red")).add_to(m)
    folium.Marker(curr_location, tooltip="Driver (You)", icon=folium.Icon(color="blue", icon="car", prefix="fa")).add_to(m)
    st_folium(m, width=700, height=400)
