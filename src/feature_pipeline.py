import datetime
from src.feature_extraction import process_store_data
from src.weather_features import process_weather_data

def build_feature_vector(data):
    """
    Build a composite feature vector from store and weather data for a recommendation engine.
    
    The feature vector includes:
      - Zipcode
      - Aggregated store metrics:
          - store_counts: counts per primary store type.
          - avg_ratings: average ratings per primary store type.
          - spatial_density: number of stores within a defined radius of the centroid.
          - centroid: computed average latitude and longitude.
      - Weather features:
          - current temperature, wind speed, temperature flag, and forecast aggregations.
      - Time features:
          - Hour of day and day of week derived from the current weather timestamp.
      - Campaign Suitability Score:
          - A composite metric based on weather (foot traffic potential) and store density.
    """
    # Process store data: we only need the aggregated metrics from stores
    stores = data.get("stores", [])
    _, aggregated_metrics = process_store_data(stores)
    
    # Process weather data to extract current and forecast features
    weather = data.get("weather", {})
    weather_features = process_weather_data(weather)
    
    # Build the initial feature vector
    feature_vector = {
        "zipcode": data.get("zipcode"),
        "store_counts": aggregated_metrics.get("store_counts"),
        "avg_ratings": aggregated_metrics.get("avg_ratings"),
        "spatial_density": aggregated_metrics.get("spatial_density"),
        "centroid": aggregated_metrics.get("centroid"),
        "weather": weather_features,
    }
    
    # Compute a Campaign Suitability Score (example logic):
    # If weather is not adverse, then the score is the product of spatial density and the overall average rating.
    weather_flag = 1 if not weather_features.get("adverse_weather", False) else 0
    spatial_density = aggregated_metrics.get("spatial_density", 0)
    avg_ratings = aggregated_metrics.get("avg_ratings", {})
    overall_avg_rating = (sum(avg_ratings.values()) / len(avg_ratings)) if avg_ratings else 0
    campaign_suitability_score = weather_flag * spatial_density * overall_avg_rating
    feature_vector["campaign_suitability_score"] = campaign_suitability_score
    
    # Extract time features from weather current time if available
    current_time_str = weather.get("current", {}).get("time")
    if current_time_str:
        try:
            dt = datetime.datetime.fromisoformat(current_time_str)
            feature_vector["hour_of_day"] = dt.hour
            feature_vector["day_of_week"] = dt.weekday()  # Monday=0, Sunday=6
        except Exception as e:
            feature_vector["hour_of_day"] = None
            feature_vector["day_of_week"] = None
    else:
        feature_vector["hour_of_day"] = None
        feature_vector["day_of_week"] = None
    
    return feature_vector

# Example usage if running this module directly:
if __name__ == '__main__':
    import json
    # Load your JSON data (adjust the path as needed)
    with open('data/data.json', 'r') as f:
        data = json.load(f)
    features = build_feature_vector(data)
    print("Composite Feature Vector:")
    print(json.dumps(features, indent=2))
