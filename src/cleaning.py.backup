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
    series = series.astype(float)
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
    # Convert list of store dicts to DataFrame
    df = pd.json_normalize(stores)
    
    # Check for missing ratings and impute or drop (here we drop missing ratings)
    if df['rating'].isnull().any():
        print("Missing ratings found. Dropping these records.")
        df = df.dropna(subset=['rating'])
    
    # Normalize the ratings (example: min-max scaling)
    df['rating_normalized'] = normalize_numeric(df['rating'], method='minmax')
    
    # Optionally, normalize geographical coordinates if needed.
    # For instance, ensure latitude and longitude are floats.
    df['location.latitude'] = df['location.latitude'].astype(float)
    df['location.longitude'] = df['location.longitude'].astype(float)
    
    # Parsing and normalizing addresses can be done using regex or a library like usaddress.
    # For example:
    # df['street'], df['city'], df['state'], df['zip'] = zip(*df['formattedAddress'].apply(parse_address))
    
    return df

def clean_weather_data(weather):
    """
    Clean and ensure consistency in weather data.
    
    - Check for missing values in 'current' and 'hourly' data.
    - Ensure hourly arrays (time, temperature, relative humidity, wind speed) have equal lengths.
    - Normalize numerical weather arrays if needed.
    """
    # Check if all hourly arrays have the same length.
    hourly = weather.get('hourly', {})
    keys = ['time', 'temperature_2m', 'relative_humidity_2m', 'wind_speed_10m']
    lengths = {key: len(hourly.get(key, [])) for key in keys}
    if len(set(lengths.values())) != 1:
        raise ValueError("Hourly weather arrays are not aligned. Found lengths: " + str(lengths))
    
    # Convert hourly data into a DataFrame for easier manipulation.
    df_hourly = pd.DataFrame({
        'time': hourly['time'],
        'temperature_2m': hourly['temperature_2m'],
        'relative_humidity_2m': hourly['relative_humidity_2m'],
        'wind_speed_10m': hourly['wind_speed_10m']
    })
    
    # Check for missing values in the weather data.
    if df_hourly.isnull().any().any():
        print("Missing values found in hourly weather data. Consider imputing or dropping these rows.")
        # For example, you could fill missing values with forward fill:
        df_hourly.fillna(method='ffill', inplace=True)
    
    # Normalize numerical values if needed (using min-max scaling as an example)
    df_hourly['temperature_norm'] = normalize_numeric(df_hourly['temperature_2m'], method='minmax')
    df_hourly['wind_speed_norm'] = normalize_numeric(df_hourly['wind_speed_10m'], method='minmax')
    
    return df_hourly
