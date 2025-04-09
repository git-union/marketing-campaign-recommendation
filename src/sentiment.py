import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Ensure required NLTK data is downloaded
nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt')

def compute_store_sentiment(stores):
    """
    Groups stores by their primaryType, computes sentiment on their reviews,
    and returns a dictionary in the following format:
    
      {
         "grocery_store": {
             "sentiment": "positive",   # or "neutral" / "negative"
             "sentiment_score": 0.7654
         },
         ...
      }
    """
    sia = SentimentIntensityAnalyzer()
    
    # Group stores by primaryType.
    store_groups = {}
    for store in stores:
        primary_type = store.get("primaryType", "unknown")
        if primary_type not in store_groups:
            store_groups[primary_type] = []
        store_groups[primary_type].append(store)
    
    # Compute sentiment for each group.
    store_sentiment = {}
    for primary_type, group in store_groups.items():
        review_texts = []
        for store in group:
            # Use the "reviews" field as provided in your data.json
            reviews = store.get("reviews", [])
            for review in reviews:
                # Extract the review text from the nested "text" dictionary.
                text = review.get("text", {}).get("text", "")
                if not text:
                    text = review.get("originalText", {}).get("text", "")
                if text:
                    review_texts.append(text)
        
        if review_texts:
            # Compute compound sentiment scores for each review.
            scores = [sia.polarity_scores(text)['compound'] for text in review_texts]
            avg_sentiment = sum(scores) / len(scores)
            # Determine sentiment label based on the average compound score.
            if avg_sentiment >= 0.05:
                sentiment_label = "positive"
            elif avg_sentiment <= -0.05:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
        else:
            avg_sentiment = 0
            sentiment_label = "neutral"
        
        store_sentiment[primary_type] = {
            "sentiment": sentiment_label,
            "sentiment_score": avg_sentiment
        }
    
    return store_sentiment
