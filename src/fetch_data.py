import os
import json
import requests

# Replace with your actual API key
GOOGLE_API_KEY = os.getenv("OPENAI_API_KEY")

def get_lat_lon(zipcode):
    """Fetches latitude and longitude for a given ZIP code using Google Geocoding API."""
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={zipcode}&key={GOOGLE_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        response_json = response.json()
        if response_json["status"] == "OK":
            location = response_json["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            print(f"Geocoding failed: {response_json['status']}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching geocoding data: {e}")
        return None, None

def get_google_places(zipcode, store_type):
    """Fetches nearby stores and their details from Google Places API (New Text Search)."""
    lat, lon = get_lat_lon(zipcode)
    if lat is None or lon is None:
        return {"error": "Could not fetch location data."}
    
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.primaryType,places.types,places.rating,places.reviews"
    }
    data = {
        "textQuery": f"{store_type} in {zipcode}"
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_weather_data(zipcode):
    """Fetches real-time weather data from Open-Meteo API based on latitude & longitude."""
    lat, lon = get_lat_lon(zipcode)
    if lat is None or lon is None:
        return {"error": "Could not fetch location data."}
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    try:
        response = requests.get(url)
        response.raise_for_status()
        response_json = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return {"error": f"Error fetching weather data: {e}"}
    return response_json

def fetch_data(zipcode, store_type):
    """Fetches data for a given ZIP code and combines results."""
    print(f"Fetching data for ZIP Code: {zipcode} and store type: {store_type}...")
    
    places_data = get_google_places(zipcode, store_type)
    if "error" in places_data:
        return places_data

    stores = []
    for place in places_data.get("places", []):
        stores.append(place)  # Append the place dictionary directly

    weather_data = get_weather_data(zipcode)

    result = {
        "zipcode": zipcode,
        "stores": stores,
        "weather": weather_data
    }
    return result




