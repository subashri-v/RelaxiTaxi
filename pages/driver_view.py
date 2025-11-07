import streamlit as st
import folium
from streamlit_folium import st_folium
import time
from shared_state import get_app_state  
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Get the shared state dictionary
state = get_app_state()

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

# --- Security Check ---
if st.session_state.get("role") != "driver":
    st.error("You must be logged in as a driver to access this page.")
    if st.button("Go to Login"):
        st.switch_page("app.py")
    st.stop()

# --- Header with Sign Out ---
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.title("👨‍✈️ Driver Portal")
with col2:
    if st.button("Sign Out"):
        st.session_state.role = None
        st.switch_page("app.py")

# --- MODIFIED ---
# Check global state for a booking
if state["booking"] is None:
    st.info("No active ride requests. Waiting for a customer...")
    time.sleep(5) # Wait 5 seconds and check again
    st.rerun()
    st.stop()
# --- END MODIFIED ---


# --- MODIFIED ---
# Get data from global state
booking = state["booking"]
data = state["distance_data"]
# --- END MODIFIED ---
start = data["start_coords"]
end = data["end_coords"]


# --- View 1: Ride Request (Pending) ---
if booking['status'] == 'pending':
    st.subheader("New Ride Request!")
    st.markdown(f"**From:** {data['start']}")
    st.markdown(f"**To:** {data['end']}")
    st.markdown(f"**Fare:** ₹{booking['fare']:.2f}")

    if st.button("✅ Accept Ride"):
        # --- MODIFIED ---
        state["booking"]['status'] = 'accepted'
        state["booking"]['driver'] = "You (Driver)" # Assign driver
        # --- END MODIFIED ---
        st.rerun()

# --- View 2: Active Ride (Accepted) ---
elif booking['status'] == 'accepted':
    st.subheader(f"On-going Ride to {data['end']}")
    st.success(f"Pickup: {data['start']} | Dropoff: {data['end']}")

    # --- MODIFIED ---
    progress = state["ride_progress"]
    # --- END MODIFIED ---

    # --- Driver Controls ---
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚗 Move Forward"):
            progress = min(1.0, progress + 0.25) # Move 25%
            # --- MODIFIED ---
            state["ride_progress"] = progress
            # --- END MODIFIED ---
            st.rerun()
    
    with col2:
        if progress > 0.0: # Can only complete after starting
            if st.button("🏁 Complete Ride"):
                st.balloons()
                st.success("Ride Completed!")
                # --- MODIFIED ---
                state["booking"] = None # Clear the booking
                state["ride_progress"] = 0.0
                state["distance_data"] = None
                # --- END MODIFIED ---
                time.sleep(2)
                st.rerun()

    with col3:
        if progress == 0.0:
            if st.button("🚫 Cancel Ride"):
                # Store a flag in session state to show the cancel message temporarily
                st.session_state["cancelled"] = True
                st.session_state["cancel_time"] = time.time()
                st.rerun()

    # --- Separate handling for cancellation message ---
    if st.session_state.get("cancelled"):
        st.warning("❌ Ride cancelled successfully!")
        if time.time() - st.session_state["cancel_time"] > 5:
            # After 5 seconds, clear booking + reset state
            state.update({
                "booking": None,
                "ride_progress": 0.0,
                "distance_data": None
            })
            st.session_state.pop("cancelled")
            st.session_state.pop("cancel_time")
            st.rerun()
        st.stop()  # Prevents rest of UI from showing


    

    # --- Progress Bar ---
    if progress == 0.0:
        st.info("On the way to pickup...")
    elif progress < 1.0:
        st.info("Ride in progress...")
    
    st.progress(progress)

    # --- Map Display ---
    curr_lat = start[0] + progress * (end[0] - start[0])
    curr_lon = start[1] + progress * (end[1] - start[1])
    curr_location = (curr_lat, curr_lon)

    m = folium.Map(location=curr_location, zoom_start=13)
    folium.Marker(start, tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(end, tooltip="Destination", icon=folium.Icon(color="red")).add_to(m)
    folium.Marker(curr_location, tooltip="Driver (You)", icon=folium.Icon(color="blue", icon="car", prefix="fa")).add_to(m)
    
    st_folium(m, width=700, height=400)