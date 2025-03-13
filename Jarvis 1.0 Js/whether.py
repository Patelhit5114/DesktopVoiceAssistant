import requests

def fetch_weather(city):
    # OpenWeatherMap API endpoint
    api_key = 'c4548dc1a45307d4956f41f860958373'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    # Make the request
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON 
        
        weather_data = response.json()
        
        # Extract relevant information
        temperature = weather_data['main']['temp']
        weather_description = weather_data['weather'][0]['description']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']
        
        # Print the weather information
        print(f"Weather in {city}:")
        print(f"Temperature: {temperature}°C")
        print(f"Description: {weather_description}")
        print(f"Humidity: {humidity}%")
        print(f"Wind Speed: {wind_speed} m/s")
    else:
        print(f"Failed to fetch weather data. Status code: {response.status_code}")

# Replace 'your_api_key_here' with your actual OpenWeatherMap API key
# city = 'gandhinagar'  # Replace with the city you want to check

# fetch_weather(city)