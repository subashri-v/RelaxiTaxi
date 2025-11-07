import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium
import random
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
    st.title("🚕 RelaxiTaxi")
with col2:
    if st.button("Sign Out"):
        st.session_state.role = None
        st.switch_page("app.py")

# --- Inputs ---
start = st.text_input("Enter Start Location:", "PES University, Bangalore")
end = st.text_input("Enter End Location:", "MG Road, Bangalore")

# --- Button ---
if st.button("Search Rides"):
    geolocator = Nominatim(user_agent="cab_aggregator", timeout=10)
    start_location = geolocator.geocode(start)
    end_location = geolocator.geocode(end)

    if start_location and end_location:
        start_coords = (start_location.latitude, start_location.longitude)
        end_coords = (end_location.latitude, end_location.longitude)
        distance_km = geodesic(start_coords, end_coords).kilometers

        # --- MODIFIED ---
        # Save to global state instead of session state
        state["distance_data"] = {
            "start": start,
            "end": end,
            "start_coords": start_coords,
            "end_coords": end_coords,
            "distance_km": distance_km
        }
        state["booking"] = None  # reset previous booking
        # --- END MODIFIED ---
    else:
        st.error("❌ Could not locate one or both addresses. Please try again.")

# --- Display result ---
# --- MODIFIED ---
if state["distance_data"]:
    data = state["distance_data"]
    # --- END MODIFIED ---
    distance = data['distance_km']

    st.success(f"📏 Distance between {data['start']} and {data['end']}: {distance:.2f} km")

    # --- Show Map ---
    m = folium.Map(location=data["start_coords"], zoom_start=13)
    folium.Marker(data["start_coords"], tooltip="Start", popup=data["start"], icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(data["end_coords"], tooltip="End", popup=data["end"], icon=folium.Icon(color='red')).add_to(m)
    st_folium(m, width=700, height=500)

    # --- Fare Calculation ---
    base_fare_ac = 60
    base_fare_non_ac = 40
    per_km_ac = 20
    per_km_non_ac = 15

    total_ac = base_fare_ac + (per_km_ac * distance)
    total_non_ac = base_fare_non_ac + (per_km_non_ac * distance)

    st.markdown("### 🚗 Available Cabs")

    col1, col2 = st.columns(2)

    # --- Cab Non-AC ---
    with col1:
        st.image("https://icon-library.com/images/cab-icon/cab-icon-16.jpg", width=120)
        st.markdown("**Non-AC Ride**")
        st.markdown(f"💰 Estimated Fare: **₹{total_non_ac:.2f}**")
        if st.button("Book Non-AC"):
            driver = random.choice(["Ravi Kumar", "Amit Sharma", "Karan Singh", "Rahul Das", "Deepak Mehta"])
            eta = random.randint(3, 10)
            # --- MODIFIED ---
            state["booking"] = {
                "type": "Non-AC Ride",
                "fare": total_non_ac,
                "driver": driver, 
                "eta": eta,
                "status": "pending" 
            }
            state["ride_progress"] = 0.0 
            # --- END MODIFIED ---

    # --- Cab AC ---
    with col2:
        st.image("https://images.vexels.com/media/users/3/128868/isolated/preview/b8dd4eaa0e285fcf4248b50916b0cef9-taxi-cab-icon-silhouette.png", width=120)
        st.markdown("**AC Ride**")
        st.markdown(f"💰 Estimated Fare: **₹{total_ac:.2f}**")
        if st.button("Book AC"):
            driver = random.choice(["Vikas Rao", "Arjun Patil", "Manoj Kumar", "Suresh Reddy", "Abhinav Singh"])
            eta = random.randint(3, 10)
            # --- MODIFIED ---
            state["booking"] = {
                "type": "AC Ride",
                "fare": total_ac,
                "driver": driver,
                "eta": eta,
                "status": "pending" 
            }
            state["ride_progress"] = 0.0 
            # --- END MODIFIED ---

# --- Booking Confirmation ---
# --- MODIFIED ---
if state["booking"]:
    booking = state["booking"]
    # --- END MODIFIED ---
    st.markdown("---")
    
    if booking['status'] == 'pending':
        st.info("⏳ Waiting for a driver to accept your ride...")
        st.rerun() # Auto-refresh to check if driver accepted
    
    elif booking['status'] == 'accepted':
        st.success(
            f"✅ {booking['type']} booked successfully!\n\n"
            f"👨‍✈️ Driver: **{booking['driver']}**\n\n"
            f"⏱ ETA: **{booking['eta']} mins**\n\n"
            f"💰 Fare: **₹{booking['fare']:.2f}**"
        )
        # ✅ Show Track button only after booking is accepted
        if st.button("📍 Track Your Ride"):
            st.switch_page("pages/track_ride.py")