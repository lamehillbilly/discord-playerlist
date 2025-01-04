import discord
from discord.ext import commands, tasks
import requests
import os

# Bot setup with minimal required intents
intents = discord.Intents.default()
intents.message_content = True  # We need this for the !players command
bot = commands.Bot(command_prefix='!', intents=intents)

# URL for the API
API_URL = "YOUR_API_ENDPOINT_HERE"  # Replace with your actual API endpoint

async def fetch_total_players():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
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
    print(f'Bot is in {len(bot.guilds)} guilds')
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

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        raise ValueError("No Discord token found. Make sure to set the DISCORD_TOKEN environment variable.")
    
    print("Starting bot...")
    bot.run(token)