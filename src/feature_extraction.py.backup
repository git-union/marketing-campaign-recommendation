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
    # Convert list of stores into a DataFrame
    df = pd.json_normalize(stores)
    
    # One-Hot Encoding for the "types" column using MultiLabelBinarizer
    mlb = MultiLabelBinarizer()
    types_encoded = mlb.fit_transform(df['types'])
    types_df = pd.DataFrame(types_encoded, columns=mlb.classes_, index=df.index)
    df = pd.concat([df, types_df], axis=1)
    
    # Retain primaryType as a categorical feature (you can further encode this if needed)
    df['primaryType'] = df['primaryType'].astype('category')
    
    # Normalize ratings using MinMaxScaler (if not already normalized)
    scaler = MinMaxScaler()
    df['rating_normalized'] = scaler.fit_transform(df[['rating']])
    
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
