import requests
import pandas as pd
from datetime import datetime
import streamlit as st
import matplotlib.pyplot as plt

# Replace with your actual OpenWeatherMap API key
API_KEY = "e385526633ef0d977d36b7055e7b765a"
CITY = "Plovdiv"

# URL to get forecast data (5 days / 3-hour intervals)
URL = f"https://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={API_KEY}&units=metric"

# Coordinates for Plovdiv (for air pollution data)
LAT = 42.1354
LON = 24.7453

# URL for air pollution data
POLLUTION_URL = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={LAT}&lon={LON}&appid={API_KEY}"

# Fetch weather data from the API
weather_response = requests.get(URL)
weather_data = weather_response.json()

# Fetch air pollution data from the API
pollution_response = requests.get(POLLUTION_URL)
pollution_data = pollution_response.json()

# Function to get and process weather data
def get_weather_data():
    weather = []

    for entry in weather_data["list"]:
        date = datetime.fromtimestamp(entry["dt"]).date()
        temp = entry["main"]["temp"]
        rain = entry.get("rain", {}).get("3h", 0)
        humidity = entry["main"]["humidity"]
        wind_speed = entry["wind"]["speed"]
        weather.append({
            "date": date,
            "temp": temp,
            "rain": rain,
            "humidity": humidity,
            "wind_speed": wind_speed
        })

    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(weather)

    # Group by date to get daily average temperature, total rain, wind speed
    df = df.groupby("date").agg({
        "temp": "mean",  # Calculate the mean temperature for each day
        "rain": "sum",   # Calculate the total rainfall for each day
        "humidity": "mean",  # Calculate the average humidity for each day
        "wind_speed": "mean"  # Calculate the average wind speed
    })

    return df

# Get the weather data
weather_df = get_weather_data()

# Calculate the average temperature of the week
avg_temp = weather_df["temp"].mean()

# Set the normal temperature values (e.g., average for April)
NORMALS = {
    "April": {"temp": 14, "rain_days": 7},
    "May": {"temp": 18, "rain_days": 9}
}

# Streamlit UI for Pilots
st.title(f"Weather and Air Pollution Data for Pilots in {CITY}")
st.write(f"Displaying a 5-day weather forecast and air pollution data for **{CITY}**.")

# Weather Data Section
st.header("Weather Data (Flight Planning)")
st.write(f"**Average Temperature for the Week**: {avg_temp:.2f}°C")

# Display the weather data in a table
st.subheader("Weather Data (Temperature, Rainfall, Humidity, Wind Speed)")
st.write(weather_df)

# Warnings related to temperature and wind speed
if avg_temp > NORMALS["April"]["temp"] + 2:
    st.warning("⚠️ Temperatures are unusually high! Flight performance might be impacted.")
else:
    st.success("✅ Temperatures are within normal range for safe flight planning.")

if weather_df["wind_speed"].max() > 20:
    st.warning("⚠️ High wind speeds detected! Check for possible turbulence or changes in flight plan.")
else:
    st.success("✅ Wind speeds are within safe levels for flight.")

# Visualizing the temperature trend and wind speed
st.subheader("Temperature and Wind Speed Over the Week")
fig, ax1 = plt.subplots(figsize=(10, 5))

ax1.plot(weather_df.index, weather_df["temp"], marker='o', color='tab:red', label="Temperature (°C)")
ax1.set_xlabel("Date")
ax1.set_ylabel("Temperature (°C)", color='tab:red')
ax1.tick_params(axis="y", labelcolor='tab:red')

ax2 = ax1.twinx()
ax2.plot(weather_df.index, weather_df["wind_speed"], marker='s', color='tab:blue', label="Wind Speed (m/s)")
ax2.set_ylabel("Wind Speed (m/s)", color='tab:blue')
ax2.tick_params(axis="y", labelcolor='tab:blue')

fig.tight_layout()  # Adjust layout for better readability
st.pyplot(fig)


# Air Pollution Data Section
st.header("Air Pollution Data (Impact on Visibility)")

# Check if the pollution data was successfully retrieved
if pollution_response.status_code == 200:
    pm2_5 = pollution_data['list'][0]['components']['pm2_5']
    pm10 = pollution_data['list'][0]['components']['pm10']
    no2 = pollution_data['list'][0]['components']['no2']
    so2 = pollution_data['list'][0]['components']['so2']
    ozone = pollution_data['list'][0]['components']['o3']

    # Display the pollution data
    st.write(f"**PM2.5**: {pm2_5} µg/m³")
    st.write(f"**PM10**: {pm10} µg/m³")
    st.write(f"**NO2**: {no2} µg/m³")
    st.write(f"**SO2**: {so2} µg/m³")
    st.write(f"**Ozone**: {ozone} µg/m³")

    # Define the safety thresholds for each component
    safe_pm2_5 = 35  # µg/m³ - above this value, expect visibility issues (fog)
    safe_pm10 = 50    # µg/m³ - above this value, poor visibility
    safe_ozone = 100  # µg/m³ - above this is dangerous for breathing, affects visibility
 
    # Determine visibility and air quality impact
    if pm2_5 > safe_pm2_5 or pm10 > safe_pm10 or ozone > safe_ozone:
        st.warning("⚠️ **Visibility may be reduced!** Possible fog or haze, not ideal for flight.")
    else:
        st.success("✅ **Air quality is good!** Visibility is clear, safe for flight.")
# Additional notes on weather conditions like fog (мъгла)
    if pm2_5 > safe_pm2_5 or pm10 > safe_pm10:
        st.write("⚠️ **Potential hazard:** Reduced visibility due to haze or fog (мъгла) may affect flying conditions.")
    else:
        st.write("🌤️ **Weather Update:** Visibility is good, with no fog expected.
   ")

else:
    st.error("Failed to retrieve air pollution data.")

#--------=-=-=--=-=---------------

# Additional Aviation-Oriented Info Section
st.header("🛫 Aviation Weather Briefing")

# Simulate basic ceiling/floor guidance based on wind and rain
st.subheader("Maximum Wind Speeds by Day")
wind_df = []

for entry in weather_data["list"]:
    date = datetime.fromtimestamp(entry["dt"]).date()
    wind_speed = entry["wind"]["speed"]
    wind_df.append({
        "date": date,
        "wind_speed": wind_speed
    })

# Convert to DataFrame and group by day
wind_df = pd.DataFrame(wind_df)
daily_wind = wind_df.groupby("date").agg({"wind_speed": "max"})

st.write("**Peak Wind Gusts (m/s) — Highest Recorded Each Day:**")
st.dataframe(daily_wind.style.format("{:.1f}"))

# Add general guidance based on wind speeds
st.subheader("Wind-Based Safety Notes:")
for date, row in daily_wind.iterrows():
    speed = row["wind_speed"]
    if speed < 5:
        st.info(f"{date}: ✅ Calm conditions — optimal for VFR (Visual Flight Rules) flight.")
    elif speed < 10:
        st.warning(f"{date}: ⚠️ Moderate wind — suitable for experienced pilots.")
    else:
        st.error(f"{date}: ❌ Strong winds — caution advised, consider delaying flights.")

# Estimate a simple 'ceiling' report based on rain (heavy rain => low ceiling)
st.subheader("Estimated Flight Ceiling Conditions (Based on Rainfall):")
for index, row in weather_df.iterrows():
    rain = row["rain"]
    if rain == 0:
        st.success(f"{index}: Clear skies or light clouds — high ceiling (>3000 ft).")
    elif rain < 5:
        st.warning(f"{index}: Light rain — moderate ceiling (~1500–3000 ft).")
    else:
        st.error(f"{index}: Heavy rain — low ceiling (<1000 ft), IFR conditions likely.")
