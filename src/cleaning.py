import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler

def load_json_data(filepath):
    """Load JSON data from a file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

def normalize_numeric(series, method='minmax'):
    """
    Normalize a pandas Series using the specified method.
    
    Parameters:
    - series: pd.Series containing numerical values.
    - method: 'minmax' for MinMax scaling or 'standard' for Standard scaling.
    
    Returns:
    - Scaled numpy array.
    """
    # Handle empty series
    if series.empty or len(series) == 0:
        print("Warning: Empty series provided for normalization. Returning empty array.")
        return np.array([])
    
    series = series.astype(float)
    
    # Handle series with all NaN values
    if series.isna().all():
        print("Warning: Series contains only NaN values. Returning array of zeros.")
        return np.zeros(len(series))
    
    # Handle series with single value (no variation)
    if series.nunique() <= 1:
        print("Warning: Series has no variation. Returning array of zeros.")
        return np.zeros(len(series))
    
    if method == 'minmax':
        scaler = MinMaxScaler()
    elif method == 'standard':
        scaler = StandardScaler()
    else:
        raise ValueError("Method must be either 'minmax' or 'standard'")
    
    # Reshape required for scaler (n_samples, n_features)
    scaled = scaler.fit_transform(series.values.reshape(-1, 1))
    return scaled.flatten()

def clean_store_data(stores):
    """
    Clean and normalize store data.
    
    - Converts store data to a DataFrame.
    - Normalizes the 'rating' column.
    - Checks for missing ratings.
    - You can add address normalization and coordinate consistency here.
    """
    # Handle empty stores list
    if not stores:
        print("Warning: No stores found. Returning empty DataFrame.")
        return pd.DataFrame()
    
    # Convert list of store dicts to DataFrame
    df = pd.json_normalize(stores)
    
    # Handle empty DataFrame
    if df.empty:
        print("Warning: Empty DataFrame after normalization. Returning empty DataFrame.")
        return df
    
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
        # Normalize the ratings (example: min-max scaling)
        df['rating_normalized'] = normalize_numeric(df['rating'], method='minmax')
        
        # Optionally, normalize geographical coordinates if needed.
        # For instance, ensure latitude and longitude are floats.
        if 'location.latitude' in df.columns:
            df['location.latitude'] = df['location.latitude'].astype(float)
        if 'location.longitude' in df.columns:
            df['location.longitude'] = df['location.longitude'].astype(float)
    else:
        print("Warning: No valid data to normalize. Skipping normalization.")
        df['rating_normalized'] = df['rating']
    
    # Parsing and normalizing addresses can be done using regex or a library like usaddress.
    # For example:
    # df['street'], df['city'], df['state'], df['zip'] = zip(*df['formattedAddress'].apply(parse_address))
    
    return df

def clean_weather_data(weather):
    """
    Clean and ensure consistency in weather data.
    Now only processes daily data if hourly is not present.
    """
    if 'hourly' in weather and weather['hourly']:
        hourly = weather['hourly']
        keys = ['time', 'temperature_2m', 'relative_humidity_2m', 'wind_speed_10m']
        lengths = {key: len(hourly.get(key, [])) for key in keys}
        if len(set(lengths.values())) != 1:
            raise ValueError("Hourly weather arrays are not aligned. Found lengths: " + str(lengths))
        df_hourly = pd.DataFrame({
            'time': hourly['time'],
            'temperature_2m': hourly['temperature_2m'],
            'relative_humidity_2m': hourly['relative_humidity_2m'],
            'wind_speed_10m': hourly['wind_speed_10m']
        })
        if df_hourly.isnull().any().any():
            print("Missing values found in hourly weather data. Consider imputing or dropping these rows.")
            df_hourly.fillna(method='ffill', inplace=True)
        df_hourly['temperature_norm'] = normalize_numeric(df_hourly['temperature_2m'], method='minmax')
        df_hourly['wind_speed_norm'] = normalize_numeric(df_hourly['wind_speed_10m'], method='minmax')
        return df_hourly
    elif 'daily' in weather and weather['daily']:
        # Just return the daily data as a DataFrame for inspection if needed
        return pd.DataFrame(weather['daily'])
    else:
        print("No hourly or daily weather data found. Returning empty DataFrame.")
        return pd.DataFrame()
