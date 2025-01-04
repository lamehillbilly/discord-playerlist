import discord
from discord.ext import commands, tasks
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# URL for the API
API_URL = "https://2004scape.org/api/v1/worldlist"  # Replace with your actual API endpoint

async def fetch_total_players():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        # Sum up all player counts
        total_players = sum(world["players"] for world in data)
        return total_players
    except Exception as e:
        print(f"Error fetching player count: {e}")
        return None

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    update_status.start()

@tasks.loop(minutes=5)  # Updates every 5 minutes
async def update_status():
    total_players = await fetch_total_players()
    if total_players is not None:
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{total_players} total players online"
            )
        )

@bot.command(name='players')
async def get_players(ctx):
    total_players = await fetch_total_players()
    if total_players is not None:
        await ctx.send(f"Total players online: {total_players}")
    else:
        await ctx.send("Unable to fetch player count at this time.")

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))