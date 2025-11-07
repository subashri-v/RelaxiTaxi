import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
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
if st.session_state.get("role") != "customer":
    st.error("You must be logged in as a customer to access this page.")
    if st.button("Go to Login"):
        st.switch_page("app.py")
    st.stop()

# --- Header with Sign Out ---
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.title("📍 Track Your Ride")
with col2:
    if st.button("Sign Out"):
        st.session_state.role = None
        st.switch_page("app.py")

# --- Check active booking ---
# --- MODIFIED ---
if state["booking"] is None:
# --- END MODIFIED ---
    st.warning("🚕 No active ride found. Please book a cab first from the main page.")
    if st.button("Go to Booking Page"):
        st.switch_page("pages/book_ride.py")
    st.stop()

# --- Booking & ride data ---
# --- MODIFIED ---
booking = state["booking"]
data = state["distance_data"]
# --- END MODIFIED ---
start = data["start_coords"]
end = data["end_coords"]

# --- Ride summary ---
if booking['status'] == 'pending':
    st.info("⏳ Waiting for a driver to accept your ride...")
    time.sleep(5) # Auto-refresh
    st.rerun()
    st.stop()

st.info(f"Tracking **{booking['type']}** driven by **{booking['driver']}** 🚘")
st.markdown(f"""
**🧭 Ride Details:**
- **Pickup:** {data['start']}
- **Destination:** {data['end']}
- **Current Fare:** ₹{booking['fare']:.2f}
""")

# --- Allow user to update source or destination ---
with st.expander("✏️ Change Destination"):
    new_start = st.text_input("Change Start Location:", data["start"])
    new_end = st.text_input("Change Destination:", data["end"])
    if st.button("Update Locations"):
        geolocator = Nominatim(user_agent="relaxitaxi_tracker", timeout=10)
        new_start_loc = geolocator.geocode(new_start)
        new_end_loc = geolocator.geocode(new_end)

        if new_start_loc and new_end_loc:
            start = (new_start_loc.latitude, new_start_loc.longitude)
            end = (new_end_loc.latitude, new_end_loc.longitude)
            new_distance = geodesic(start, end).kilometers

            if booking['type'] == "AC Ride":
                base_fare, per_km = 60, 20
            else:
                base_fare, per_km = 40, 15
            new_fare = base_fare + (per_km * new_distance)

            # --- MODIFIED ---
            # Save updated data to global state
            state["distance_data"].update({
                "start": new_start,
                "end": new_end,
                "start_coords": start,
                "end_coords": end,
                "distance_km": new_distance
            })
            state["booking"]['fare'] = new_fare
            # --- END MODIFIED ---
            st.success(f"✅ Route updated! New distance: {new_distance:.2f} km, New Fare: ₹{new_fare:.2f}")
            st.rerun()
        else:
            st.error("❌ Could not find one or both locations. Try again.")


# --- Simulate driver movement (PASSIVE) ---
# --- MODIFIED ---
progress = state["ride_progress"]
# --- END MODIFIED ---

if progress == 0.0:
    st.markdown("Your driver is on the way to pick you up!")
elif progress < 1.0:
    st.markdown("Ride in progress...")
else:
    st.success("🎉 Ride Completed! Thank you for choosing RelaxiTaxi.")
    st.balloons()
    # --- MODIFIED ---
    state["booking"] = None # Clear booking on completion
    state["distance_data"] = None
    state["ride_progress"] = 0.0
    # --- END MODIFIED ---
    st.stop()

st.progress(progress, text=f"Ride Progress: {progress*100:.0f}%")

if progress == 0.0: # Only allow cancelling before the ride starts
    if st.button("🚫 Cancel Ride"):
        # --- MODIFIED ---
        state["booking"] = None
        state["ride_progress"] = 0.0
        state["distance_data"] = None
        # --- END MODIFIED ---
        st.warning("❌ Ride cancelled successfully!")
        st.rerun()

# --- Simulated driver position ---
curr_lat = start[0] + progress * (end[0] - start[0])
curr_lon = start[1] + progress * (end[1] - start[1])
curr_location = (curr_lat, curr_lon)

# --- Map Display ---
m = folium.Map(location=curr_location, zoom_start=13)
folium.Marker(start, tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
folium.Marker(end, tooltip="Destination", icon=folium.Icon(color="red")).add_to(m)
folium.Marker(curr_location, tooltip="Driver", icon=folium.Icon(color="blue", icon="car", prefix="fa")).add_to(m)
st_folium(m, width=700, height=500)

# --- Auto-refresh the page to get driver updates ---
time.sleep(5) # Pause for 5 seconds
st.rerun()