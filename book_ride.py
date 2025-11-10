import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium
import random
from shared_state import get_app_state
from db_utils import add_ride

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Shared state
state = get_app_state()

# --- CSS to hide sidebar ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# --- Security check ---
if st.session_state.get("role") != "customer":
    st.error("You must be logged in as a customer to book a ride.")
    if st.button("Go to Login"):
        st.switch_page("pages/rider_login.py")
    st.stop()

# --- Header ---
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.title("🚕 RelaxiTaxi")
with col2:
    if st.button("Sign Out"):
        st.session_state.role = None
        st.switch_page("app.py")

# Rider History
if st.button("History"):
    st.switch_page("pages/rider_history.py")

# --- Inputs ---
start_input = st.text_input("Enter Start Location:", "PES University, Bangalore")
end_input = st.text_input("Enter End Location:", "MG Road, Bangalore")

if st.button("Search Rides"):
    geolocator = Nominatim(user_agent="cab_aggregator")
    start_loc = geolocator.geocode(start_input)
    end_loc = geolocator.geocode(end_input)

    if start_loc and end_loc:
        start_coords = (start_loc.latitude, start_loc.longitude)
        end_coords = (end_loc.latitude, end_loc.longitude)
        distance_km = geodesic(start_coords, end_coords).kilometers

        state["distance_data"] = {
            "start": start_input,
            "end": end_input,
            "start_coords": start_coords,
            "end_coords": end_coords,
            "distance_km": distance_km
        }
        state["booking"] = None
    else:
        st.error("❌ Could not locate one or both addresses.")

# --- Show results if distance_data exists ---
if state.get("distance_data"):
    data = state["distance_data"]
    distance = data['distance_km']
    st.success(f"📏 Distance: {distance:.2f} km")

    # Map
    m = folium.Map(location=data["start_coords"], zoom_start=13)
    folium.Marker(data["start_coords"], tooltip="Start", popup=data["start"], icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(data["end_coords"], tooltip="End", popup=data["end"], icon=folium.Icon(color='red')).add_to(m)
    st_folium(m, width=700, height=500)

    # Fare calculation
    base_fare_ac, base_fare_non_ac = 60, 40
    per_km_ac, per_km_non_ac = 20, 15
    fare_ac = base_fare_ac + per_km_ac * distance
    fare_non_ac = base_fare_non_ac + per_km_non_ac * distance

    st.markdown("### 🚗 Available Cabs")
    col1, col2 = st.columns(2)

    # NON-AC RIDE
    with col1:
        st.image("https://icon-library.com/images/cab-icon/cab-icon-16.jpg", width=120)
        st.markdown("**Non-AC Ride**")
        st.markdown(f"💰 Fare: ₹{fare_non_ac:.2f}")

        if st.button("Book Non-AC"):
            driver = random.choice(["Ravi Kumar", "Amit Sharma", "Karan Singh"])
            eta = random.randint(3, 10)

            ride_id = add_ride(
                rider_id=st.session_state.user_id,
                start=data["start"],
                end=data["end"],
                start_coords=data["start_coords"],
                end_coords=data["end_coords"],
                distance_km=distance,
                fare=fare_non_ac,
                ac=False
            )

            state["booking"] = {
                "ride_id": ride_id,
                "type": "Non-AC Ride",
                "fare": fare_non_ac,
                "driver": driver,
                "driver_id": None,
                "eta": eta,
                "status": "pending"
            }

    # AC RIDE
    with col2:
        st.image("https://images.vexels.com/media/users/3/128868/isolated/preview/b8dd4eaa0e285fcf4248b50916b0cef9-taxi-cab-icon-silhouette.png", width=120)
        st.markdown("**AC Ride**")
        st.markdown(f"💰 Fare: ₹{fare_ac:.2f}")

        if st.button("Book AC"):
            driver = random.choice(["Vikas Rao", "Arjun Patil", "Manoj Kumar"])
            eta = random.randint(3, 10)

            ride_id = add_ride(
                rider_id=st.session_state.user_id,
                start=data["start"],
                end=data["end"],
                start_coords=data["start_coords"],
                end_coords=data["end_coords"],
                distance_km=distance,
                fare=fare_ac,
                ac=True
            )

            state["booking"] = {
                "ride_id": ride_id,
                "type": "AC Ride",
                "fare": fare_ac,
                "driver": driver,
                "driver_id": None,
                "eta": eta,
                "status": "pending"
            }

# --- Show booking info ---
if state.get("booking"):
    booking = state["booking"]
    if booking["status"] == "pending":
        st.info("⏳ Waiting for a driver to accept your ride...")
    elif booking["status"] == "accepted":
        st.success(f"✅ {booking['type']} booked! Driver: {booking['driver']} | Fare: ₹{booking['fare']:.2f}")
        if st.button("📍 Track Your Ride"):
            st.switch_page("pages/track_ride.py")
