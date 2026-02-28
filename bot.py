import discord
from discord.ext import tasks
from discord import app_commands
import requests
import random
import os
import re # Added for the time parser
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.tree = app_commands.CommandTree(self)
        
        self.is_active = False 
        self.target_mention = "@everyone"
        self.interval_seconds = 1200 

    async def setup_hook(self):
        self.random_ping_loop.start()

    @tasks.loop(seconds=1200)
    async def random_ping_loop(self):
        if self.is_active and random.random() < 0.33:
            channel = self.get_channel(CHANNEL_ID)
            if channel:
                content = self.get_random_content()
                await channel.send(f"{self.target_mention} {content}")

    def get_random_content(self):
        try:
            roll = random.random()
            if roll < 0.33:
                data = requests.get("https://api.adviceslip.com/advice").json()
                return f" {data['slip']['advice']} - Drake Singh"
            elif roll < 0.66:
                data = requests.get("https://official-joke-api.appspot.com/random_joke").json()
                return f" {data['setup']} ... {data['punchline']} - Drake Singh"
            else:
                return " Keep the grind going, Bitscord!"
        except:
            return " API is a bit sleepy!"

# Helper function to turn "1s" into 1, "1m" into 60, etc.
def parse_time(time_str: str):
    time_str = time_str.lower().strip()
    match = re.match(r"(\d+)([smh])", time_str)
    if not match:
        return None
    
    amount = int(match.group(1))
    unit = match.group(2)
    
    if unit == 's': return amount
    if unit == 'm': return amount * 60
    if unit == 'h': return amount * 3600
    return None

client = MyBot()

@client.event
async def on_ready():
    await client.tree.sync()
    print(f' {client.user} is ONLINE (Waiting for /start)')

@client.tree.command(name="start", description="Enable the random pings")
@app_commands.checks.has_permissions(manage_messages=True)
async def start_pings(interaction: discord.Interaction):
    client.is_active = True
    await interaction.response.send_message("hi")

@client.tree.command(name="stop", description="Disable all random pings")
@app_commands.checks.has_permissions(manage_messages=True)
async def stop_pings(interaction: discord.Interaction):
    client.is_active = False
    await interaction.response.send_message("bye")

@client.tree.command(name="set", description="Set interval (e.g. 10s, 5m, 1h)")
@app_commands.checks.has_permissions(manage_messages=True)
async def set_timer(interaction: discord.Interaction, time: str):
    seconds = parse_time(time)
    
    if seconds is None:
        await interaction.response.send_message(" Invalid format! Use `10s`, `5m`, or `1h`.", ephemeral=True)
        return

    if seconds < 1:
        await interaction.response.send_message("Time must be at least 1 second!", ephemeral=True)
        return

    client.random_ping_loop.change_interval(seconds=seconds)
    await interaction.response.send_message(f" Interval set to **{time}**.")

@client.tree.command(name="ping_user", description="Pick a specific user to ping randomly")
@app_commands.checks.has_permissions(manage_messages=True)
async def target_user(interaction: discord.Interaction, member: discord.Member):
    client.target_mention = member.mention
    await interaction.response.send_message(f" Target set to **{member.mention}**.")

@client.tree.command(name="ping_everyone", description="Set target back to @everyone")
@app_commands.checks.has_permissions(manage_messages=True)
async def target_everyone(interaction: discord.Interaction):
    client.target_mention = "@everyone"
    await interaction.response.send_message(" Target set to **@everyone**.")

@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this fuck off!", ephemeral=True)

client.run(TOKEN)
