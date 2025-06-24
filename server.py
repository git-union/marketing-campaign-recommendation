import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import flask-cors
import json
import google.generativeai as genai
from datetime import datetime, timedelta
from src.fetch_data import fetch_data
from src.cleaning import load_json_data, clean_store_data, clean_weather_data
from src.feature_extraction import process_store_data
from src.weather_features import process_weather_data
from src.feature_pipeline import build_feature_vector
from src.sentiment import compute_store_sentiment

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

# Set up logging
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.logger.setLevel(logging.INFO)

# Configure Gemini API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_current_context():
    """Get current date, time, and contextual information for real-time campaigns."""
    now = datetime.now()
    
    # Get current date and time
    current_date = now.strftime("%B %d, %Y")
    current_time = now.strftime("%I:%M %p")
    current_day = now.strftime("%A")
    
    # Calculate upcoming dates for campaign planning
    tomorrow = (now + timedelta(days=1)).strftime("%B %d, %Y")
    this_weekend_start = (now + timedelta(days=(5 - now.weekday()) % 7)).strftime("%B %d, %Y")
    this_weekend_end = (now + timedelta(days=(7 - now.weekday()) % 7)).strftime("%B %d, %Y")
    next_week_start = (now + timedelta(days=7)).strftime("%B %d, %Y")
    
    # Determine time context
    if now.hour < 12:
        time_context = "morning"
    elif now.hour < 17:
        time_context = "afternoon"
    else:
        time_context = "evening"
    
    # Determine day context
    if now.weekday() < 5:
        day_context = "weekday"
    else:
        day_context = "weekend"
    
    return {
        "current_date": current_date,
        "current_time": current_time,
        "current_day": current_day,
        "tomorrow": tomorrow,
        "this_weekend_start": this_weekend_start,
        "this_weekend_end": this_weekend_end,
        "next_week_start": next_week_start,
        "time_context": time_context,
        "day_context": day_context
    }

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
    
    # Get current context for real-time campaigns
    context = get_current_context()
    
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

    # Enhanced prompt with real-time context and 7-day forecast
    marketing_prompt = f"""
You are a strategic marketing consultant with deep insights into local market dynamics. Your task is to generate a concise, poster-ready marketing campaign recommendation for a local store based on the provided JSON data and current real-time context. The recommendation should be visually appealing, succinct, and output in valid JSON format only (without any additional text).

CURRENT REAL-TIME CONTEXT:
- Current Date: {context['current_date']}
- Current Time: {context['current_time']}
- Current Day: {context['current_day']}
- Time Context: {context['time_context']}
- Day Context: {context['day_context']}
- Tomorrow: {context['tomorrow']}
- This Weekend: {context['this_weekend_start']} - {context['this_weekend_end']}
- Next Week Start: {context['next_week_start']}

IMPORTANT: Use these current dates for your campaign durations. Do NOT use past dates or hardcoded dates like "November 2024". Use the current date context provided above.

The JSON data you will use includes:
- "store_counts": Number of nearby competitor stores by category (e.g., clothing_store, book_store, grocery_store, etc.).
- "avg_ratings": Average customer ratings for each store category.
- "spatial_density": Indicator of how clustered competitor stores are.
- "centroid": Geographic center coordinates for the market.
- "weather": 7-day daily forecast (max/min temp, precipitation, weather code) and summary stats (avg_max_temp, avg_min_temp, total_precip).
- "hour_of_day" and "day_of_week": The current temporal context for time-sensitive promotions.
- "store_sentiment": Customer sentiment analysis and scores for each store category.
- "campaign_suitability_score": A metric indicating overall campaign readiness.

Output your recommendation using the following JSON structure exactly and give output in json format without any additional text:

{{
  "Insights": [
    "Insight 1: Based on the 7-day weather forecast and time context",
    "Insight 2: Based on local competition analysis",
    "Insight 3: Based on spatial density and market saturation",
    "Insight 4: Based on customer ratings and sentiment analysis",
    "Insight 5: Based on consumer behavior patterns for the week"
  ],
  "Campaigns": [
    {{
      "Campaign Title": "Create a compelling, time-relevant campaign title for a specific day or period in the next 7 days",
      "Campaign Description": "Write a 2-3 sentence description that leverages the 7-day weather forecast, time, and market conditions",
      "Campaign Duration": "Use dates from the next 7 days (e.g., 'June 22, 2024 - June 28, 2024')",
      "Discount/Promo": "Create a relevant promotional offer based on the 7-day forecast and market context"
    }},
    {{
      "Campaign Title": "Create a second compelling campaign title for another day or period in the next 7 days",
      "Campaign Description": "Write a 2-3 sentence description targeting another aspect of the 7-day forecast and market conditions",
      "Campaign Duration": "Use dates from the next 7 days",
      "Discount/Promo": "Create another relevant promotional offer"
    }}
  ]
}}

CRITICAL REQUIREMENTS:
1. Use ONLY dates from the next 7 days for campaign durations
2. Make campaigns relevant to the weather and market context for specific days in the upcoming week
3. Consider the 7-day weather forecast in your recommendations
4. Base insights on the actual data provided
5. Ensure all dates are current and realistic
6. Keep campaign descriptions to 2-3 sentences maximum

Generate at least two campaign recommendations in JSON Format as above with distinct insights based on the provided JSON data and 7-day context.

JSON Data:
{json.dumps(feature_vector, indent=2)}
"""

    app.logger.info("Sending prompt to Gemini with JSON response format.")

    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # First Gemini call - Generate initial recommendations
        response = model.generate_content(
            marketing_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7
            )
        )
        
        initial_campaign_content = response.text
        app.logger.error(f"Raw Gemini response (initial): {initial_campaign_content}")

        # Last-resort: extract substring between first '{' and last '}'
        start = initial_campaign_content.find('{')
        end = initial_campaign_content.rfind('}')
        if start != -1 and end != -1 and end > start:
            json_str = initial_campaign_content[start:end+1]
            app.logger.error(f"Extracted JSON substring (manual): {repr(json_str)[:200]}")
        else:
            app.logger.error("Could not find JSON object in Gemini response.")
            return jsonify({"error": "Could not find JSON object in Gemini response."}), 500

        try:
            initial_campaign_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            app.logger.error(f"Failed to parse JSON from initial Gemini call: {e}")
            app.logger.error(f"Raw response: {json_str}")
            return jsonify({"error": "Invalid JSON format from initial Gemini call", "details": str(e)}), 500

        # Second Gemini call - Marketing expert validation and improvement
        marketing_expert_prompt = f"""
You are a senior marketing expert with 15+ years of experience in retail marketing, consumer psychology, and campaign optimization. Your role is to analyze and improve marketing campaign recommendations to make them more realistic, compelling, and effective.

CURRENT CONTEXT:
- Current Date: {context['current_date']}
- Store Type: {store_type}
- Location: {zipcode}

RAW CLEANED DATA FOR ANALYSIS:
Store Data: {json.dumps(aggregated_metrics, indent=2)}
Weather Data: {json.dumps(weather_features, indent=2)}
Store Sentiment: {json.dumps(store_sentiment, indent=2)}

ANALYZE THE FOLLOWING INITIAL CAMPAIGN RECOMMENDATIONS:
{json.dumps(initial_campaign_data, indent=2)}

MARKETING EXPERT TASK:
1. **Realism Check**: Ensure campaigns are realistic for the store type and market conditions
2. **Consumer Psychology**: Make recommendations more psychologically compelling
3. **Competitive Edge**: Ensure campaigns stand out from typical local promotions
4. **Actionability**: Make campaigns more actionable and measurable
5. **Seasonal Relevance**: Ensure weather and seasonal factors are properly leveraged
6. **Local Market Fit**: Adapt to local consumer behavior patterns

IMPROVEMENT GUIDELINES:
- Make campaign titles more catchy and memorable
- Ensure promotional offers are realistic and profitable
- Add specific timing strategies based on weather patterns
- Include psychological triggers (urgency, scarcity, social proof)
- Make descriptions more compelling and benefit-focused (2-3 sentences maximum)
- Ensure insights are actionable and data-driven based on the provided raw data
- Use actual data from the raw cleaned data to create specific, actionable insights

OUTPUT FORMAT:
Return the improved campaign recommendations in the same JSON structure, but with enhanced content that addresses the above criteria. Focus on making the campaigns more realistic, compelling, and effective for real-world implementation.

CRITICAL: Use the actual data provided above to create specific insights. Do not mention "data needed" - use the real data available.

Return only valid JSON without any additional text.
"""

        # Second Gemini call for marketing expert validation
        expert_response = model.generate_content(
            marketing_expert_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8
            )
        )
        
        final_campaign_content = expert_response.text

        try:
            final_campaign_data = json.loads(final_campaign_content)
        except json.JSONDecodeError as e:
            app.logger.error(f"Failed to parse JSON from marketing expert call: {e}")
            app.logger.error(f"Raw response: {final_campaign_content}")
            # Fallback to initial recommendations if expert validation fails
            app.logger.warning("Falling back to initial recommendations due to expert validation failure")
            final_campaign_data = initial_campaign_data

        # Return the final improved recommendations
        return jsonify(final_campaign_data)

    except Exception as e:
        app.logger.error(f"Gemini API request failed: {e}")
        return jsonify({"error": "Gemini API request failed", "details": str(e)}), 500

# Run the Flask development server locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
