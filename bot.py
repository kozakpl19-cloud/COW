import os
import discord
from discord.ext import tasks
import requests
from bs4 import BeautifulSoup
import re

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1566768794129403914

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_game = None

flags = {
    "PL": "🇵🇱",
    "TR": "🇹🇷",
    "EN": "🇬🇧",
    "DE": "🇩🇪",
    "FR": "🇫🇷",
    "RU": "🇷🇺",
    "NL": "🇳🇱",
    "CZ": "🇨🇿",
    "ES": "🇪🇸",
    "IT": "🇮🇹"
}

@tasks.loop(minutes=1)
async def check_maps():
    global last_game

    try:
        html = requests.get(
            "https://kr-cowstats.com/games_list",
            timeout=10
        ).text

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()

        match = re.search(
            r'(\d{8}).*?server:\s*([A-Z]{2}).*?Scenario:\s*(.*?)\.\s*Start Date.*?Opens Slots:\s*(\d+)',
            text,
            re.S
        )

        if not match:
            print("Nie znaleziono mapy")
            return

        game_id = match.group(1)
        server = match.group(2)
        scenario = match.group(3).strip()
        slots = match.group(4)

        print("Aktualne ID:", game_id)

        if last_game is None:
            last_game = game_id
            print("Pierwsze ID zapisane:", game_id)
            return

        if game_id != last_game:

            flag = flags.get(server, "🌍")

            channel = await client.fetch_channel(CHANNEL_ID)

            await channel.send(
f"""🚀 **NOWA MAPA CALL OF WAR!**

🆔 **ID:** {game_id}
🌍 **Serwer:** {server} {flag}
🎮 **Mapa:** {scenario}
👥 **Wolne miejsca:** {slots}

🔗 https://kr-cowstats.com/{game_id}
"""
            )

            print("Wysłano nową mapę:", game_id)

            last_game = game_id

    except Exception as e:
        print("Błąd:", e)

@client.event
async def on_ready():
    print(f"Zalogowano jako {client.user}")
    check_maps.start()

client.run(TOKEN)