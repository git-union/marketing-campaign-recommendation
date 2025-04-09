def process_weather_data(weather):
    """
    Process weather data to extract features.
    
    Features extracted:
      - Current weather:
          - current_temp: The current temperature.
          - current_wind: The current wind speed.
          - temp_flag: A simple flag ("cold" or "warm") based on a temperature threshold.
      - Hourly forecast aggregation (first 24 hours):
          - avg_temp: Average temperature.
          - max_temp: Maximum temperature.
          - min_temp: Minimum temperature.
          - temp_variability: Difference between max and min temperature.
          - avg_humidity: Average relative humidity.
          - max_wind: Maximum wind speed.
          - adverse_weather: Binary flag if conditions might negatively impact foot traffic.
      - Weekly forecast:
          - A list of daily forecasts (for one week), including weather conditions (e.g., sunny, rainy),
            minimum and maximum temperatures, and date.
            Expects weather['daily'] to contain:
              - time: list of date strings,
              - weather_condition: list of strings,
              - temperature_min: list of minimum temperatures,
              - temperature_max: list of maximum temperatures.
    """
    current = weather.get('current', {})
    hourly = weather.get('hourly', {})
    
    # Current Weather Features
    current_temp = current.get('temperature_2m')
    current_wind = current.get('wind_speed_10m')
    
    # Define a threshold for temperature flag (example: below 10°C is "cold")
    temp_threshold = 10.0
    temp_flag = "cold" if current_temp is not None and current_temp < temp_threshold else "warm"
    
    # Forecast Aggregation (first 24 hours)
    temps = hourly.get('temperature_2m', [])[:24]
    wind_speeds = hourly.get('wind_speed_10m', [])[:24]
    humidities = hourly.get('relative_humidity_2m', [])[:24]
    
    if not temps:
        raise ValueError("No hourly temperature data available.")
    
    avg_temp = sum(temps) / len(temps)
    max_temp = max(temps)
    min_temp = min(temps)
    temp_variability = max_temp - min_temp
    
    # Compute average humidity if available
    avg_humidity = sum(humidities) / len(humidities) if humidities else None
    max_wind = max(wind_speeds) if wind_speeds else None
    
    # Define adverse weather conditions:
    # Example: adverse if min temperature is below 0°C or maximum wind speed exceeds 25 km/h.
    adverse_weather = (min_temp < 0) or (max_wind is not None and max_wind > 25)
    
    # Weekly Forecast Extraction:
    # Expecting a 'daily' key in the weather dict with the necessary information.
    weekly_forecast = []
    daily = weather.get('daily', None)
    if daily:
        times = daily.get('time', [])
        conditions = daily.get('weather_condition', [])
        min_temps = daily.get('temperature_min', [])
        max_temps = daily.get('temperature_max', [])
        
        # Loop through the available daily data (assume same length for each list)
        for i in range(len(times)):
            forecast = {
                "date": times[i],
                "weather_condition": conditions[i] if i < len(conditions) else None,
                "min_temp": min_temps[i] if i < len(min_temps) else None,
                "max_temp": max_temps[i] if i < len(max_temps) else None,
            }
            weekly_forecast.append(forecast)
    else:
        weekly_forecast = None  # or you can choose to return an empty list []
    
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
        "weekly_forecast": weekly_forecast
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
