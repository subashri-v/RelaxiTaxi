"""Handles ride booking logic for RelaxiTaxi — includes location lookup, 
distance calculation, fare estimation, and booking confirmation for customers.
"""

import os
import sys
import random

import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium

# Ensure shared_state is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared_state import get_app_state  # pylint: disable=wrong-import-position

# --- Constants ---
BASE_FARE_AC = 60
BASE_FARE_NON_AC = 40
PER_KM_AC = 20
PER_KM_NON_AC = 15

# --- Initialize shared state ---
STATE = get_app_state()

# --- Hide the sidebar ---
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
COL1, COL2 = st.columns([0.8, 0.2])
with COL1:
    st.title("🚕 RelaxiTaxi")
with COL2:
    if st.button("Sign Out"):
        st.session_state.role = None
        st.switch_page("app.py")

# --- Inputs ---
START = st.text_input("Enter Start Location:", "PES University, Bangalore")
END = st.text_input("Enter End Location:", "MG Road, Bangalore")

# --- Search Rides ---
if st.button("Search Rides"):
    geolocator = Nominatim(user_agent="cab_aggregator", timeout=10)
    start_location = geolocator.geocode(START)
    end_location = geolocator.geocode(END)

    if start_location and end_location:
        start_coords = (start_location.latitude, start_location.longitude)
        end_coords = (end_location.latitude, end_location.longitude)
        distance_km = geodesic(start_coords, end_coords).kilometers

        STATE["distance_data"] = {
            "start": START,
            "end": END,
            "start_coords": start_coords,
            "end_coords": end_coords,
            "distance_km": distance_km,
        }
        STATE["booking"] = None
    else:
        st.error("❌ Could not locate one or both addresses. Please try again.")

# --- Display Result ---
if STATE["distance_data"]:
    data = STATE["distance_data"]
    distance = data["distance_km"]

    st.success(
        f"📏 Distance between {data['start']} and {data['end']}: {distance:.2f} km"
    )

    # --- Show Map ---
    map_obj = folium.Map(location=data["start_coords"], zoom_start=13)
    folium.Marker(
        data["start_coords"],
        tooltip="Start",
        popup=data["start"],
        icon=folium.Icon(color="green"),
    ).add_to(map_obj)
    folium.Marker(
        data["end_coords"],
        tooltip="End",
        popup=data["end"],
        icon=folium.Icon(color="red"),
    ).add_to(map_obj)
    st_folium(map_obj, width=700, height=500)

    # --- Fare Calculation ---
    total_ac = BASE_FARE_AC + (PER_KM_AC * distance)
    total_non_ac = BASE_FARE_NON_AC + (PER_KM_NON_AC * distance)

    st.markdown("### 🚗 Available Cabs")

    col1, col2 = st.columns(2)

    # --- Cab Non-AC ---
    with col1:
        st.image(
            "https://icon-library.com/images/cab-icon/cab-icon-16.jpg",
            width=120,
        )
        st.markdown("**Non-AC Ride**")
        st.markdown(f"💰 Estimated Fare: **₹{total_non_ac:.2f}**")
        if st.button("Book Non-AC"):
            driver = random.choice(
                ["Ravi Kumar", "Amit Sharma", "Karan Singh", "Rahul Das", "Deepak Mehta"]
            )
            eta = random.randint(3, 10)
            STATE["booking"] = {
                "type": "Non-AC Ride",
                "fare": total_non_ac,
                "driver": driver,
                "eta": eta,
                "status": "pending",
            }
            STATE["ride_progress"] = 0.0

    # --- Cab AC ---
    with col2:
        st.image(
            "https://images.vexels.com/media/users/3/128868/isolated/"
            "preview/b8dd4eaa0e285fcf4248b50916b0cef9-taxi-cab-icon-silhouette.png",
            width=120,
        )
        st.markdown("**AC Ride**")
        st.markdown(f"💰 Estimated Fare: **₹{total_ac:.2f}**")
        if st.button("Book AC"):
            driver = random.choice(
                ["Vikas Rao", "Arjun Patil", "Manoj Kumar", "Suresh Reddy", "Abhinav Singh"]
            )
            eta = random.randint(3, 10)
            STATE["booking"] = {
                "type": "AC Ride",
                "fare": total_ac,
                "driver": driver,
                "eta": eta,
                "status": "pending",
            }
            STATE["ride_progress"] = 0.0

# --- Booking Confirmation ---
if STATE["booking"]:
    booking = STATE["booking"]
    st.markdown("---")

    if booking["status"] == "pending":
        st.info("⏳ Waiting for a driver to accept your ride...")
        st.rerun()
    elif booking["status"] == "accepted":
        st.success(
            f"✅ {booking['type']} booked successfully!\n\n"
            f"👨‍✈️ Driver: **{booking['driver']}**\n\n"
            f"⏱ ETA: **{booking['eta']} mins**\n\n"
            f"💰 Fare: **₹{booking['fare']:.2f}**"
        )
        if st.button("📍 Track Your Ride"):
            st.switch_page("pages/track_ride.py")

