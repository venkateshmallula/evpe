import streamlit as st
import numpy as np
import pickle
import pandas as pd
import requests
import random

# Load the model
model_path = 'sav'
with open(model_path, 'rb') as file:
    model = pickle.load(file)

# API key for weather data
api_key = 'd6dc6c7fb512f7742550fa86607b2ae4'

# Function to get weather data from an API
def get_weather_data(api_key, lat, lon):
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={lat},{lon}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return None

def estimate_humidity(temperature):
    if temperature is not None and temperature > 30:
        return random.uniform(70, 90)  # High humidity
    elif temperature is not None and temperature > 20:
        return random.uniform(50, 70)  # Moderate humidity
    else:
        return random.uniform(30, 50)  # Low humidity

def categorize_weather(temperature, humidity):
    if temperature is None or humidity is None:
        return 'Unknown'
    if temperature > 25 and humidity <= 70:
        return 2
    elif temperature <= 25 and temperature > 15 and humidity <= 70:
        return 0
    elif humidity > 70:
        return 1
    else:
        return 0

# Define the Streamlit app
def main():
    st.title("Predicting Battery Swap Station Utilization Using Real-Time Weather Data")

    st.write("""
    ## Input Data
    Provide the input data for the prediction:
    """)
    
    # Define input fields
    latitude = st.number_input("Latitude (e.g., 12.873800155645254)", value=12.873800155645254)
    longitude = st.number_input("Longitude (e.g., 80.07849378133422)", value=80.07849378133422)
    status = 0
    station_capacity = st.number_input("Station capacity (e.g., 1)", value=1)

    if 'weather_data' not in st.session_state:
        st.session_state.weather_data = None
    
    if st.button("Fetch Weather Data"):
        weather = get_weather_data(api_key, latitude, longitude)
        if weather is not None:
            locality_weather = weather.get('current', {})
            temperature = locality_weather.get('temp_c', None)
            if temperature is None:
                temperature = random.uniform(25, 30)
            humidity = estimate_humidity(temperature)
            weather_category = categorize_weather(temperature, humidity)

            st.session_state.weather_data = {
                'temperature': temperature,
                'humidity': humidity,
                'weather_category': weather_category
            }
        else:
            temperature = random.uniform(25, 30)
            humidity = estimate_humidity(temperature)
            weather_category = categorize_weather(temperature, humidity)
            st.session_state.weather_data = {
                'temperature': temperature,
                'humidity': humidity,
                'weather_category': weather_category
            }

    if st.session_state.weather_data:
        st.write(f"Temperature: {st.session_state.weather_data['temperature']}")
        st.write(f"Humidity: {st.session_state.weather_data['humidity']}")
        
        # Create input data tuple
        input_data = (latitude, longitude, status, station_capacity,
                      st.session_state.weather_data['temperature'],
                      st.session_state.weather_data['humidity'],
                      st.session_state.weather_data['weather_category'])
        
        # Convert input data to numpy array
        input_data_as_nparray = np.array(input_data)
        
        # Reshape the input data
        input_data_std = input_data_as_nparray.reshape(1, -1)
        print(input_data_std)
        
        if st.button("Predict"):
            # Make a prediction
            prediction = model.predict(input_data_std)
            
            # Store prediction in session state
            st.session_state.prediction = prediction[0]

    if 'prediction' in st.session_state:
        st.write(f"Number of Active Swaps: {st.session_state.prediction}")

if __name__ == '__main__':
    main()
