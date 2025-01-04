import discord
from discord.ext import commands, tasks
import requests
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

# Bot setup with minimal required intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True  # Need this for changing nickname
bot = commands.Bot(command_prefix='!', intents=intents)

# URL for the API
API_URL = "https://2004scape.org/api/v1/worldlist"  # Replace with your actual API endpoint

async def fetch_total_players():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        total_players = sum(world["players"] for world in data)
        logger.info(f"Successfully fetched player count: {total_players}")
        return total_players
    except Exception as e:
        logger.error(f"Error fetching player count: {e}")
        return None

@bot.event
async def on_ready():
    logger.info(f'Bot {bot.user} (ID: {bot.user.id}) has connected to Discord!')
    logger.info(f'Connected to {len(bot.guilds)} guilds:')
    for guild in bot.guilds:
        logger.info(f'- {guild.name} (ID: {guild.id})')
    update_status.start()

@tasks.loop(minutes=5)
async def update_status():
    logger.info("Updating bot status...")
    total_players = await fetch_total_players()
    if total_players is not None:
        try:
            # Update nickname in all guilds
            for guild in bot.guilds:
                try:
                    await guild.me.edit(nick=f"Online: {total_players} ")
                    logger.info(f"Updated nickname in {guild.name}")
                except discord.Forbidden:
                    logger.warning(f"Cannot update nickname in {guild.name} - Missing permissions")
                except Exception as e:
                    logger.error(f"Error updating nickname in {guild.name}: {e}")
            
            # Also update the status for good measure
            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"otal players online..."
                )
            )
            logger.info("Successfully updated bot status")
        except Exception as e:
            logger.error(f"Error updating status: {e}")

@bot.command(name='players')
async def get_players(ctx):
    logger.info(f"Players command used by {ctx.author} in {ctx.guild}")
    total_players = await fetch_total_players()
    if total_players is not None:
        await ctx.send(f"Total players online: {total_players}")
    else:
        await ctx.send("Unable to fetch player count at this time.")

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error("No Discord token found!")
        raise ValueError("No Discord token found. Make sure to set the DISCORD_TOKEN environment variable.")
    
    logger.info("Starting bot...")
    try:
        bot.run(token)
    except discord.errors.LoginFailure as e:
        logger.error(f"Failed to login: Invalid token")
        raise
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise