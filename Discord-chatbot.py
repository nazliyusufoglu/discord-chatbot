import discord
import os
from dotenv import load_dotenv
import requests
import pathlib
import textwrap

import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# Set up Discord intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# Load OpenWeatherMap API key from environment variables
OWM_API_KEY = os.getenv('OWM_API_KEY')

# Function to get weather information for a given city
def get_weather(city_name):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city_name}&appid={OWM_API_KEY}&units=metric"

    # Send request to OpenWeatherMap API
    response = requests.get(complete_url)
    print(response.status_code)
    if response.status_code == 200:
        data = response.json()
        main = data['main']
        weather = data['weather'][0]
        wind = data['wind']

        # Format the weather information
        weather_report = (
            f"Weather forecast for {city_name}:\n"
            f"Temperature: {main['temp']}°C\n"
            f"Humidity: {main['humidity']}%\n"
            f"Pressure: {main['pressure']} hPa\n"
            f"Weather: {weather['description']}\n"
            f"Wind Speed: {wind['speed']} m/s"
        )
        return weather_report
    else:
        return "Weather data could not be received. Example command: !weather for city name"

# Event triggered when the bot is ready
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

# Event triggered when a message is received
@client.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    # Handle messages starting with '$' for generative AI responses
    if message.content.startswith('$'):
        response = model.generate_content(message.content[1:])
        print(message.content[1:])
        await message.channel.send(response.text)

    # Handle messages starting with '!weather' for weather information
    if message.content.startswith('!weather for'):
        city_name = message.content[len('!weather for'):].strip()
        if city_name:
            weather_report = get_weather(city_name)
            await message.channel.send(weather_report)
        else:
            await message.channel.send("Please enter a city name")

# Run the bot with the token loaded from environment variables
client.run(os.getenv('YOUR_DISCORD_BOT_TOKEN'))
