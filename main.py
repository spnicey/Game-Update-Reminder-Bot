import discord
import requests
import asyncio
from discord.ext import tasks, commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

#Todo: modify to use a collection of IDs supplied by users
STEAM_APP_ID = 2073850 #App ID for THE FINALS

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def get_latest_update():
    #for steam:
    url = f"https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid={STEAM_APP_ID}&count=1"
    response = requests.get(url)
    data = response.json()
    latest = data['appnews']['newsitems'][0]
    return {
        "title": latest['title'],
        "url": latest['url'],
        "date": latest['date']
    }

@tasks.loop(minutes=10)
async def check_for_updates():
    channel = bot.get_channel(CHANNEL_ID)
    latest_update = get_latest_update()

    # Store last seen update in a file or DB
    try:
        with open("last_update.txt", "r") as f:
            last_seen_date = int(f.read().strip())
    except FileNotFoundError:
        last_seen_date = 0

    if latest_update['date'] > last_seen_date:
        await channel.send(f"**New update available!**\n{latest_update['title']}\n{latest_update['url']}")
        with open("last_update.txt", "w") as f:
            f.write(str(latest_update['date']))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    check_for_updates.start()

bot.run(TOKEN)