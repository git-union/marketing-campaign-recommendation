import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler

def process_store_data(stores, centroid=None, radius=0.01):
    """
    Process store data for feature extraction.
    
    Parameters:
    - stores: list of store dictionaries.
    - centroid: Optional tuple (latitude, longitude) to calculate distances from.
                If not provided, the centroid is computed as the mean of the store coordinates.
    - radius: Radius (in the same coordinate units) to compute spatial density.
    
    Returns:
    - df: DataFrame with one-hot encoded store types, normalized ratings, and distance from centroid.
    - aggregated_metrics: Dictionary with store counts per primary type, average ratings, spatial density, and centroid.
    """
    # Handle empty stores list
    if not stores:
        print("Warning: No stores found. Returning empty DataFrame and default metrics.")
        return pd.DataFrame(), {
            'store_counts': {},
            'avg_ratings': {},
            'spatial_density': 0,
            'centroid': (0, 0)
        }
    
    # Convert list of stores into a DataFrame
    df = pd.json_normalize(stores)
    
    # Handle empty DataFrame
    if df.empty:
        print("Warning: Empty DataFrame after normalization. Returning empty DataFrame and default metrics.")
        return df, {
            'store_counts': {},
            'avg_ratings': {},
            'spatial_density': 0,
            'centroid': (0, 0)
        }
    
    # Handle missing 'types' column
    if 'types' not in df.columns:
        print("Warning: No 'types' column found. Creating empty types list.")
        df['types'] = [[] for _ in range(len(df))]
    
    # One-Hot Encoding for the "types" column using MultiLabelBinarizer
    mlb = MultiLabelBinarizer()
    types_encoded = mlb.fit_transform(df['types'])
    types_df = pd.DataFrame(types_encoded, columns=mlb.classes_, index=df.index)
    df = pd.concat([df, types_df], axis=1)
    
    # Handle missing 'primaryType' column
    if 'primaryType' not in df.columns:
        print("Warning: No 'primaryType' column found. Creating default primaryType.")
        df['primaryType'] = 'unknown'
    
    # Retain primaryType as a categorical feature (you can further encode this if needed)
    df['primaryType'] = df['primaryType'].astype('category')
    
    # Handle missing rating column - check if it exists and handle missing values
    if 'rating' not in df.columns:
        print("Warning: No 'rating' column found. Creating default ratings of 3.0.")
        df['rating'] = 3.0
    else:
        # Check for missing ratings and impute with default value
        if df['rating'].isnull().any():
            print("Missing ratings found. Filling with default value of 3.0.")
            df['rating'] = df['rating'].fillna(3.0)
    
    # Ensure rating is numeric
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(3.0)
    
    # Only normalize if we have data to normalize
    if len(df) > 0:
        # Normalize ratings using MinMaxScaler
        scaler = MinMaxScaler()
        df['rating_normalized'] = scaler.fit_transform(df[['rating']])
    else:
        df['rating_normalized'] = df['rating']
    
    # Handle missing location columns
    if 'location.latitude' not in df.columns or 'location.longitude' not in df.columns:
        print("Warning: Missing location columns. Using default coordinates.")
        df['location.latitude'] = 0.0
        df['location.longitude'] = 0.0
    
    # Geographical Location: ensure latitudes and longitudes are numeric
    df['location.latitude'] = df['location.latitude'].astype(float)
    df['location.longitude'] = df['location.longitude'].astype(float)
    
    # Calculate centroid if not provided (average latitude and longitude)
    if centroid is None:
        centroid_lat = df['location.latitude'].mean()
        centroid_lon = df['location.longitude'].mean()
        centroid = (centroid_lat, centroid_lon)
    
    # Compute Euclidean distance from each store to the centroid.
    # Note: For small areas, Euclidean distance is a simple approximation.
    df['distance_from_centroid'] = np.sqrt(
        (df['location.latitude'] - centroid[0])**2 + (df['location.longitude'] - centroid[1])**2
    )
    
    # Aggregated Store Metrics:
    # 1. Store Count per Primary Type
    store_counts = df['primaryType'].value_counts().to_dict()
    
    # 2. Average Rating by Primary Type
    avg_ratings = df.groupby('primaryType')['rating'].mean().to_dict()
    
    # 3. Spatial Density: count of stores within the specified radius from the centroid
    spatial_density = df[df['distance_from_centroid'] <= radius].shape[0]
    
    aggregated_metrics = {
        'store_counts': store_counts,
        'avg_ratings': avg_ratings,
        'spatial_density': spatial_density,
        'centroid': centroid
    }
    
    return df, aggregated_metrics

# Example usage (if you run this module directly):
if __name__ == '__main__':
    import json
    # Load your JSON data (ensure the file path is correct)
    with open('data/data.json', 'r') as f:
        data = json.load(f)
    stores = data.get('stores', [])
    
    df_stores, metrics = process_store_data(stores)
    print("Processed Store Data:")
    print(df_stores.head())
    print("\nAggregated Store Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value}")
