import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import flask-cors
import json
import openai
from src.fetch_data import fetch_data
from src.cleaning import load_json_data, clean_store_data, clean_weather_data
from src.feature_extraction import process_store_data
from src.weather_features import process_weather_data
from src.feature_pipeline import build_feature_vector
from src.sentiment import compute_store_sentiment

# Set up logging
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.logger.setLevel(logging.INFO)

# Configure OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/', methods=['GET'])
def healthcheck():
    # You can include additional checks here if needed (e.g., database connectivity)
    return jsonify({"status": "healthy"}), 200

@app.route('/recommend', methods=['GET'])
def recommend_campaign():
    zipcode = request.args.get('zipcode')
    store_type = request.args.get('store_type')
    
    if not zipcode or not store_type:
        app.logger.error("Missing required parameters 'zipcode' and/or 'store_type'.")
        return jsonify({"error": "Missing required parameters 'zipcode' and/or 'store_type'."}), 400

    app.logger.info(f"Received request for zipcode: {zipcode}, store_type: {store_type}")
    
    data = fetch_data(zipcode, store_type)
    app.logger.info("Data fetched successfully.")

    stores = data.get('stores', [])
    cleaned_stores = clean_store_data(stores)
    processed_stores, aggregated_metrics = process_store_data(stores)
    app.logger.info("Store data processed.")

    weather = data.get('weather', {})
    cleaned_weather = clean_weather_data(weather)
    weather_features = process_weather_data(weather)
    app.logger.info("Weather data processed.")

    feature_vector = build_feature_vector(data)
    store_sentiment = compute_store_sentiment(stores)
    feature_vector['store_sentiment'] = store_sentiment
    app.logger.info("Feature vector built.")

    # Save intermediate data (optional)
    os.makedirs('data', exist_ok=True)
    cleaned_stores.to_json('data/cleaned_stores.json', orient='records', indent=2)
    cleaned_weather.to_json('data/cleaned_weather.json', orient='records', indent=2)
    processed_stores.to_json('data/processed_stores.json', orient='records', indent=2)
    with open('data/aggregated_metrics.json', 'w') as f:
        json.dump(aggregated_metrics, f, indent=2)
    with open('data/weather_features.json', 'w') as f:
        json.dump(weather_features, f, indent=2)
    with open('data/feature_vector.json', 'w') as f:
        json.dump(feature_vector, f, indent=2)

    # Use your original prompt exactly
    marketing_prompt = f"""
You are a strategic marketing consultant with deep insights into local market dynamics. Your task is to generate a concise, poster-ready marketing campaign recommendation for a local store based on the provided JSON data. The recommendation should be visually appealing, succinct, and output in valid JSON format only (without any additional text).

Consider the following text-based poster example for inspiration:
----------------------------------------
Campaign Title: Square Sale Bonanza  
Campaign Description: Experience unbeatable deals during our limited-time sale event. Leverage a competitive landscape with 8 clothing stores and an average rating of 4.4 to stand out in the market.  
Campaign Duration: April 1, 2025 - April 3, 2025  
Discount/Promo: Up to 50% off on selected items  
Insight: Data reveals a high competitor density (8 clothing stores) and strong customer ratings (avg. 4.4), indicating a prime opportunity for an aggressive, targeted sale to capture market share.
----------------------------------------

The JSON data you will use includes:
- "store_counts": Number of nearby competitor stores by category (e.g., clothing_store, book_store, grocery_store, etc.).
- "avg_ratings": Average customer ratings for each store category.
- "spatial_density": Indicator of how clustered competitor stores are.
- "centroid": Geographic center coordinates for the market.
- "weather": Current and forecasted weather conditions (temperature, wind, humidity, adverse weather flag, etc.).
- "hour_of_day" and "day_of_week": The current temporal context for time-sensitive promotions.
- "store_sentiment": Customer sentiment analysis and scores for each store category.
- "campaign_suitability_score": A metric indicating overall campaign readiness.

Output your recommendation using the following JSON structure exactly and give output in json format without any additional text:

{
    {
  "Insights": [
    "Insight 1: Based on weather information",
    "Insight 2: Based on local competitions",
    "Insight 3: Based on local density",
    "Insight 4: Based on ratings and reviews",
    "Insight 5: Based on consumer behavior and demographics"
  ],
  "Campaigns": [
    {
      "Campaign Title": "your first campaign title here",
      "Campaign Description": "your first campaign description here",
      "Campaign Duration": "your first campaign duration (using dates)",
      "Discount/Promo": "your first discount or promotional offer"
    },
    {
      "Campaign Title": "your second campaign title here",
      "Campaign Description": "your second campaign description here",
      "Campaign Duration": "your second campaign duration (using dates)",
      "Discount/Promo": "your second discount or promotional offer"
    }
  ]
}
}

Generate at least two campaign recommendation in JSON Format as above with distinct insights based on the provided JSON data.

JSON Data:
{json.dumps(feature_vector, indent=2)}
"""

    app.logger.info("Sending prompt to OpenAI with JSON response format.")

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that only responds in valid JSON."},
                {"role": "user", "content": marketing_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}  # Enforce JSON-only output
        )
        
        campaign_content = response.choices[0].message.content

        try:
            campaign_data = json.loads(campaign_content)
        except json.JSONDecodeError as e:
            app.logger.error(f"Failed to parse JSON: {e}")
            return jsonify({"error": "Invalid JSON format from OpenAI", "details": str(e)}), 500

        # Return the parsed dictionary as a clean JSON response
        return jsonify(campaign_data)

    except Exception as e:
        app.logger.error(f"OpenAI API request failed: {e}")
        return jsonify({"error": "OpenAI API request failed", "details": str(e)}), 500

# Run the Flask development server locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
