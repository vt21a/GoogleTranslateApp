# Additional Aviation-Oriented Info Section
st.header("🛫 Aviation Weather Briefing")

# Simulate basic ceiling/floor guidance based on wind and rain
st.subheader("Wind Speed Summary (Avg by Day)")
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
daily_wind = wind_df.groupby("date").agg({"wind_speed": "mean"})

st.write("**Average Wind Speeds (m/s) by Date:**")
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
