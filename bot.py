import discord
from discord.ext import tasks
import requests
import random
import os
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))


intents = discord.Intents.default()

intents.message_content = True 
client = discord.Client(intents=intents)

def get_random_content():
    try:
      
        options = [
            lambda: f" Advice: {requests.get('https://api.adviceslip.com/advice').json()['slip']['advice']}",
            lambda: f" Joke: {requests.get('https://official-joke-api.appspot.com/random_joke').json()['setup']}... {requests.get('https://official-joke-api.appspot.com/random_joke').json()['punchline']}",
            lambda: " Keep the grind going, Bitscord!"
        ]
        return random.choice(options)()
    except:
        return "I'm feeling random, but the APIs are shy today!"

@tasks.loop(minutes=20) 
async def random_ping():
  
    if random.random() < 0.33:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            content = get_random_content()
            await channel.send(f"@everyone  hi \n{content}")

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')
    if not random_ping.is_running():
        random_ping.start()

client.run(TOKEN)