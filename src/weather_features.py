def process_weather_data(weather):
    """
    Process weather data to extract features from daily forecast data.
    
    Features extracted:
      - Current weather:
          - current_temp: The current temperature.
          - current_wind: The current wind speed.
          - temp_flag: A simple flag ("cold" or "warm") based on a temperature threshold.
      - Daily forecast aggregation (7-day forecast):
          - avg_temp: Average of daily max temperatures.
          - max_temp: Maximum temperature across the week.
          - min_temp: Minimum temperature across the week.
          - temp_variability: Difference between max and min temperature.
          - avg_humidity: Average relative humidity (if available).
          - max_wind: Maximum wind speed (if available).
          - adverse_weather: Binary flag if conditions might negatively impact foot traffic.
      - Weekly forecast:
          - A list of daily forecasts (for one week), including weather conditions,
            minimum and maximum temperatures, and date.
            Expects weather['daily'] to contain:
              - time: list of date strings,
              - temperature_2m_max: list of maximum temperatures,
              - temperature_2m_min: list of minimum temperatures,
              - precipitation_sum: list of precipitation amounts,
              - weathercode: list of weather codes.
    """
    current = weather.get('current', {})
    daily = weather.get('daily', {})
    
    # Current Weather Features
    current_temp = current.get('temperature_2m')
    current_wind = current.get('wind_speed_10m')
    
    # Define a threshold for temperature flag (example: below 10°C is "cold")
    temp_threshold = 10.0
    temp_flag = "cold" if current_temp is not None and current_temp < temp_threshold else "warm"
    
    # Daily Forecast Aggregation (7-day forecast)
    max_temps = daily.get('temperature_2m_max', [])
    min_temps = daily.get('temperature_2m_min', [])
    precipitation = daily.get('precipitation_sum', [])
    weathercodes = daily.get('weathercode', [])
    
    # Handle missing weather data gracefully
    if not max_temps:
        print("Warning: No daily temperature data available. Using default values.")
        # Return default weather features
        return {
            "current_temp": current_temp,
            "current_wind": current_wind,
            "temp_flag": temp_flag,
            "avg_temp": 20.0,  # Default average temperature
            "max_temp": 25.0,  # Default max temperature
            "min_temp": 15.0,  # Default min temperature
            "temp_variability": 10.0,  # Default variability
            "avg_humidity": None,
            "max_wind": None,
            "adverse_weather": False,
            "weekly_forecast": [],
            "avg_max_temp": 25.0,
            "avg_min_temp": 15.0,
            "total_precip": 0.0
        }
    
    # Calculate weekly statistics from daily data
    avg_temp = sum(max_temps) / len(max_temps) if max_temps else None
    max_temp = max(max_temps) if max_temps else None
    min_temp = min(min_temps) if min_temps else None
    temp_variability = max_temp - min_temp if max_temp is not None and min_temp is not None else None
    
    # Note: Humidity and wind speed might not be available in daily data
    # We'll set these to None for now
    avg_humidity = None
    max_wind = None
    
    # Define adverse weather conditions:
    # Example: adverse if min temperature is below 0°C or high precipitation
    adverse_weather = False
    if min_temp is not None and min_temp < 0:
        adverse_weather = True
    if precipitation and any(p > 10 for p in precipitation):  # More than 10mm precipitation
        adverse_weather = True
    
    # 7-day Daily Forecast
    weekly_forecast = []
    if daily:
        times = daily.get('time', [])
        for i in range(len(times)):
            forecast = {
                "date": times[i],
                "max_temp": max_temps[i] if i < len(max_temps) else None,
                "min_temp": min_temps[i] if i < len(min_temps) else None,
                "precipitation": precipitation[i] if i < len(precipitation) else None,
                "weathercode": weathercodes[i] if i < len(weathercodes) else None
            }
            weekly_forecast.append(forecast)
    else:
        weekly_forecast = None

    # Aggregate weekly stats
    if weekly_forecast and len(weekly_forecast) > 0:
        avg_max_temp = sum([d['max_temp'] for d in weekly_forecast if d['max_temp'] is not None]) / len(weekly_forecast)
        avg_min_temp = sum([d['min_temp'] for d in weekly_forecast if d['min_temp'] is not None]) / len(weekly_forecast)
        total_precip = sum([d['precipitation'] for d in weekly_forecast if d['precipitation'] is not None])
    else:
        avg_max_temp = avg_min_temp = total_precip = None
    
    return {
        "current_temp": current_temp,
        "current_wind": current_wind,
        "temp_flag": temp_flag,
        "avg_temp": avg_temp,
        "max_temp": max_temp,
        "min_temp": min_temp,
        "temp_variability": temp_variability,
        "avg_humidity": avg_humidity,
        "max_wind": max_wind,
        "adverse_weather": adverse_weather,
        "weekly_forecast": weekly_forecast,
        "avg_max_temp": avg_max_temp,
        "avg_min_temp": avg_min_temp,
        "total_precip": total_precip
    }

# Example usage if running this module directly:
if __name__ == '__main__':
    import json
    # Load your weather data (adjust the path as needed)
    with open('data/data.json', 'r') as f:
        data = json.load(f)
    weather = data.get('weather', {})
    
    features = process_weather_data(weather)
    print("Extracted Weather Features:")
    for key, value in features.items():
        print(f"{key}: {value}")
