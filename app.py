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

if pollution_response.status_code == 200:
    st.write(f"**PM2.5**: {pollution_data['list'][0]['components']['pm2_5']} µg/m³")
    st.write(f"**PM10**: {pollution_data['list'][0]['components']['pm10']} µg/m³")
    st.write(f"**NO2**: {pollution_data['list'][0]['components']['no2']} µg/m³")
    st.write(f"**SO2**: {pollution_data['list'][0]['components']['so2']} µg/m³")
    st.write(f"**Ozone**: {pollution_data['list'][0]['components']['o3']} µg/m³")
else:
    st.error("Failed to retrieve air pollution data.")
