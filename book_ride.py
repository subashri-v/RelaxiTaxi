import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium
import random
import webbrowser

st.set_page_config(page_title="RelaxiTaxi", layout="centered")

st.title("🚕 RelaxiTaxi")

# --- Session state ---
if "distance_data" not in st.session_state:
    st.session_state.distance_data = None
if "booking" not in st.session_state:
    st.session_state.booking = None

# --- Inputs ---
start = st.text_input("Enter Start Location:", "PES University, Bangalore")
end = st.text_input("Enter End Location:", "MG Road, Bangalore")

# --- Button ---
if st.button("Search Rides"):
    geolocator = Nominatim(user_agent="cab_aggregator")
    start_location = geolocator.geocode(start)
    end_location = geolocator.geocode(end)

    if start_location and end_location:
        start_coords = (start_location.latitude, start_location.longitude)
        end_coords = (end_location.latitude, end_location.longitude)
        distance_km = geodesic(start_coords, end_coords).kilometers

        st.session_state.distance_data = {
            "start": start,
            "end": end,
            "start_coords": start_coords,
            "end_coords": end_coords,
            "distance_km": distance_km
        }
        st.session_state.booking = None  # reset previous booking
    else:
        st.error("❌ Could not locate one or both addresses. Please try again.")

# --- Display result ---
if st.session_state.distance_data:
    data = st.session_state.distance_data
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
            st.session_state.booking = {
                "type": "Non-AC Ride",
                "fare": total_non_ac,
                "driver": driver,
                "eta": eta,
                "from": data['start'],
                "to": data['end']
            }

    # --- Cab AC ---
    with col2:
        st.image("https://images.vexels.com/media/users/3/128868/isolated/preview/b8dd4eaa0e285fcf4248b50916b0cef9-taxi-cab-icon-silhouette.png", width=120)
        st.markdown("**AC Ride**")
        st.markdown(f"💰 Estimated Fare: **₹{total_ac:.2f}**")
        if st.button("Book AC"):
            driver = random.choice(["Vikas Rao", "Arjun Patil", "Manoj Kumar", "Suresh Reddy", "Abhinav Singh"])
            eta = random.randint(3, 10)
            st.session_state.booking = {
                "type": "AC Ride",
                "fare": total_ac,
                "driver": driver,
                "eta": eta,
                "from": data['start'],
                "to": data['end']
            }

# --- Booking Confirmation ---
if st.session_state.booking:
    booking = st.session_state.booking
    st.markdown("---")
    st.success(
        f"✅ {booking['type']} booked successfully!\n\n"
        f"👨‍✈️ Driver: **{booking['driver']}**\n\n"
        f"⏱ ETA: **{booking['eta']} mins**\n\n"
        f"💰 Fare: **₹{booking['fare']:.2f}**"
    )

    # ✅ Show Track button only after booking
    if st.button("📍 Track Your Ride"):
        st.switch_page("pages/track_ride.py")
