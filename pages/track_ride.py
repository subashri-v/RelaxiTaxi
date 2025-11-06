import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

st.title("📍 Track Your Ride - RelaxiTaxi")

# --- Check active booking ---
if "booking" not in st.session_state or st.session_state.booking is None:
    st.warning("🚕 No active ride found. Please book a cab first from the main page.")
    st.stop()

# --- Booking & ride data ---
booking = st.session_state.booking
data = st.session_state.distance_data
start = data["start_coords"]
end = data["end_coords"]

# --- Ride summary ---
st.info(f"Tracking **{booking['type']}** driven by **{booking['driver']}** 🚘")
st.markdown(f"""
**🧭 Ride Details:**
- **Pickup:** {data['start']}
- **Destination:** {data['end']}
- **Current Fare:** ₹{booking['fare']:.2f}
- **ETA:** {booking['eta']} mins
""")

# --- Allow user to update source or destination ---
with st.expander("✏️ Change Source or Destination"):
    new_start = st.text_input("Change Start Location:", data["start"])
    new_end = st.text_input("Change Destination:", data["end"])
    if st.button("Update Locations"):
        geolocator = Nominatim(user_agent="relaxitaxi_tracker")
        new_start_loc = geolocator.geocode(new_start)
        new_end_loc = geolocator.geocode(new_end)

        if new_start_loc and new_end_loc:
            start = (new_start_loc.latitude, new_start_loc.longitude)
            end = (new_end_loc.latitude, new_end_loc.longitude)

            # Calculate new distance
            new_distance = geodesic(start, end).kilometers

            # Recalculate fare based on ride type
            if booking['type'] == "AC Ride":
                base_fare, per_km = 60, 20
            else:
                base_fare, per_km = 40, 15
            new_fare = base_fare + (per_km * new_distance)


            # Save updated data
            st.session_state.distance_data.update({
                "start": new_start,
                "end": new_end,
                "start_coords": start,
                "end_coords": end,
                "distance_km": new_distance
            })
            booking['fare'] = new_fare

            st.success(f"✅ Route updated! New distance: {new_distance:.2f} km, New Fare: ₹{new_fare:.2f}")
        else:
            st.error("❌ Could not find one or both locations. Try again.")

# --- Simulate driver movement ---
progress = st.session_state.get("ride_progress", 0.0)

col1, col2 = st.columns(2)
with col1:
    if progress < 1.0:
        if st.button("🚗 Update Driver Location"):
            progress = min(1.0, progress + 0.2)
            st.session_state.ride_progress = progress
    else:
        st.success("🎉 Ride Completed! Thank you for choosing RelaxiTaxi.")
        st.session_state.ride_progress = 1.0

with col2:
    if st.button("🚫 Cancel Ride"):
        st.session_state.booking = None
        st.session_state.ride_progress = 0.0
        st.warning("❌ Ride cancelled successfully!")
        st.stop()

# --- Simulated driver position ---
curr_lat = start[0] + progress * (end[0] - start[0])
curr_lon = start[1] + progress * (end[1] - start[1])
curr_location = (curr_lat, curr_lon)

# --- Map Display ---
m = folium.Map(location=curr_location, zoom_start=13)
folium.Marker(start, tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
folium.Marker(end, tooltip="Destination", icon=folium.Icon(color="red")).add_to(m)
folium.Marker(curr_location, tooltip="Driver", icon=folium.Icon(color="blue")).add_to(m)
st_folium(m, width=700, height=500)


# --- Fare & status section ---
st.markdown("---")
st.subheader("💸 Ride Summary")
st.markdown(f"""
- **Ride Type:** {booking['type']}
- **Driver:** {booking['driver']}
- **Updated Fare:** ₹{booking['fare']:.2f}
- **Estimated Distance:** {st.session_state.distance_data['distance_km']:.2f} km
""")
