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
        weather.append({
            "date": date,
            "temp": temp,
            "rain": rain,
            "humidity": humidity
        })

    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(weather)

    # Group by date to get daily average temperature and total rain
    df = df.groupby("date").agg({
        "temp": "mean",  # Calculate the mean temperature for each day
        "rain": "sum",   # Calculate the total rainfall for each day
        "humidity": "mean"  # Calculate the average humidity for each day
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

# Streamlit UI
st.title(f"Weather Forecast and Air Pollution Data for {CITY}")
st.write(f"Displaying 5-day weather forecast and air pollution data for **{CITY}**.")

# Weather Data Section
st.header("Weather Data")
st.write(f"**Average Temperature for the Week**: {avg_temp:.2f}°C")

# Display the weather data in a table
st.subheader("Weather Data (Temperature, Rainfall, Humidity)")
st.write(weather_df)

# Calculate if the temperature is above normal
if avg_temp > NORMALS["April"]["temp"] + 2:
    st.warning("⚠️ Temperatures are unusually high!")
else:
    st.success("✅ Temperatures are within normal range.")

# Optionally, you can visualize the data with a line plot or bar chart
st.subheader("Temperature Over the Week")
plt.figure(figsize=(10, 5))
plt.plot(weather_df.index, weather_df["temp"], marker='o', label="Temperature (°C)")
plt.xlabel("Date")
plt.ylabel("Temperature (°C)")
plt.title("Temperature Forecast")
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
st.pyplot()

# Air Pollution Data Section
st.header("Air Pollution Data")

if pollution_response.status_code == 200:
    st.write(f"**PM2.5**: {pollution_data['list'][0]['components']['pm2_5']} µg/m³")
    st.write(f"**PM10**: {pollution_data['list'][0]['components']['pm10']} µg/m³")
    st.write(f"**NO2**: {pollution_data['list'][0]['components']['no2']} µg/m³")
    st.write(f"**SO2**: {pollution_data['list'][0]['components']['so2']} µg/m³")
    st.write(f"**Ozone**: {pollution_data['list'][0]['components']['o3']} µg/m³")
else:
    st.error("Failed to retrieve air pollution data.")
