"""Main booking page for RelaxiTaxi rider interface."""

import os
import sys
import random
import streamlit as st
from streamlit_folium import st_folium
import folium
from ride_utils import get_coordinates, calculate_distance, calculate_fare
from shared_state import get_app_state

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
state = get_app_state()

# Hide sidebar
st.markdown(
    "<style>[data-testid='stSidebar']{display:none;}</style>",
    unsafe_allow_html=True
)

# Security
if st.session_state.get("role") != "customer":
    st.error("You must be logged in as a customer to access this page.")
    if st.button("Go to Login"):
        st.switch_page("app.py")
    st.stop()

# Header
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.title("🚕 RelaxiTaxi")
with col2:
    if st.button("Sign Out"):
        st.session_state.role = None
        st.switch_page("app.py")

# Inputs
start = st.text_input("Enter Start Location:", "PES University, Bangalore")
end = st.text_input("Enter End Location:", "MG Road, Bangalore")

# Search button
if st.button("Search Rides"):
    try:
        start_coords = get_coordinates(start)
        end_coords = get_coordinates(end)
        distance_km = calculate_distance(start_coords, end_coords)

        state["distance_data"] = {
            "start": start,
            "end": end,
            "start_coords": start_coords,
            "end_coords": end_coords,
            "distance_km": distance_km
        }
        state["booking"] = None
    except ValueError as e:
        st.error(str(e))

# Display result
if state["distance_data"]:
    data = state["distance_data"]
    distance = data["distance_km"]
    st.success(f"📏 Distance between {data['start']} and {data['end']}: {distance:.2f} km")

    m = folium.Map(location=data["start_coords"], zoom_start=13)
    folium.Marker(data["start_coords"], tooltip="Start", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(data["end_coords"], tooltip="End", icon=folium.Icon(color='red')).add_to(m)
    st_folium(m, width=700, height=500)

    # Fare
    total_ac = calculate_fare(distance, ac=True)
    total_non_ac = calculate_fare(distance, ac=False)

    st.markdown("### 🚗 Available Cabs")
    col1, col2 = st.columns(2)

    with col1:
        st.image("https://icon-library.com/images/cab-icon/cab-icon-16.jpg", width=120)
        st.markdown("**Non-AC Ride**")
        st.markdown(f"💰 Estimated Fare: **₹{total_non_ac:.2f}**")
        if st.button("Book Non-AC"):
            driver = random.choice(["Ravi Kumar", "Amit Sharma", "Karan Singh", "Rahul Das", "Deepak Mehta"])
            eta = random.randint(3, 10)
            state["booking"] = {"type": "Non-AC Ride", "fare": total_non_ac, "driver": driver, "eta": eta, "status": "pending"}
            state["ride_progress"] = 0.0

    with col2:
        st.image("https://images.vexels.com/media/users/3/128868/isolated/preview/b8dd4eaa0e285fcf4248b50916b0cef9-taxi-cab-icon-silhouette.png", width=120)
        st.markdown("**AC Ride**")
        st.markdown(f"💰 Estimated Fare: **₹{total_ac:.2f}**")
        if st.button("Book AC"):
            driver = random.choice(["Vikas Rao", "Arjun Patil", "Manoj Kumar", "Suresh Reddy", "Abhinav Singh"])
            eta = random.randint(3, 10)
            state["booking"] = {"type": "AC Ride", "fare": total_ac, "driver": driver, "eta": eta, "status": "pending"}
            state["ride_progress"] = 0.0

if state["booking"]:
    booking = state["booking"]
    st.markdown("---")
    if booking['status'] == 'pending':
        st.info("⏳ Waiting for a driver to accept your ride...")
        st.rerun()
    elif booking['status'] == 'accepted':
        st.success(f"✅ {booking['type']} booked!\n\n👨‍✈️ Driver: **{booking['driver']}**\n⏱ ETA: **{booking['eta']} mins**\n💰 Fare: **₹{booking['fare']:.2f}**")
        if st.button("📍 Track Your Ride"):
            st.switch_page("pages/track_ride.py")
