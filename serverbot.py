import subprocess
import discord
from discord.ext import commands
from discord import app_commands

import json
import os
import re
import time
import aiohttp
from typing import Optional, Literal
import shutil

##################################################################################################################
# Bot Code
##################################################################################################################

OWNER_ROLE_ID = 1437183305266106558
ADMIN_ROLE_ID = 1437182763093463101
GUILD_ID = 1437180858367868950

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
print("Loaded commands at startup:", bot.tree.get_commands())

WHITELIST_FILE = "/home/noahshinar/minecraft_servers/server1/whitelist.json"

# HELPER FUNCTIONS
def is_whitelisted(username: str):
    if not os.path.exists(WHITELIST_FILE):
        return False
    try:
        with open(WHITELIST_FILE, "r") as f:
            data = json.load(f)
        for entry in data:
            if entry.get("name", "").lower() == username.lower():
                return True
    except:
        pass
    return False

async def get_uuid(username: str):
    """Returns UUID string if username exists, otherwise None."""
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("id")  # Mojang UUID
            return None

def send_to_server(cmd: str):
    subprocess.run(["mcrcon", "-H", "127.0.0.1", "-P", "25575", "-p", "4630", f"{cmd}"])

# WHITELIST ADD COMMAND
@bot.tree.command(name="whitelist", description="Add a Minecraft username to the whitelist")
@app_commands.describe(username="Whitelist username")
async def whitelist(interaction: discord.Interaction, username: str):
    user_role_ids = [role.id for role in interaction.user.roles]
    if OWNER_ROLE_ID not in user_role_ids and ADMIN_ROLE_ID not in user_role_ids:
        return await interaction.response.send_message("You are not allowed to use this command.", ephemeral=True)

    # Check if username exists on Mojang
    uuid = await get_uuid(username)
    if uuid is None:
        return await interaction.response.send_message(f"Couldn't find a profile with the name: **{username}**", ephemeral=True)

    # Check if username is already whitelisted
    if is_whitelisted(username):
        return await interaction.response.send_message(f"**{username}** is already whitelisted.", ephemeral=True)

    # Send add command to Minecraft server
    send_to_server(f"whitelist add {username}")
    await interaction.response.send_message(f"Added **{username}** to the whitelist.")

# START SERVER COMMAND
@bot.tree.command(name="start", description="Start the Minecraft server")
async def start(interaction: discord.Interaction):
    user_role_ids = [role.id for role in interaction.user.roles]
    if OWNER_ROLE_ID not in user_role_ids:
        await interaction.response.send_message("You are not allowed to use this command.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send("Starting server...", ephemeral=True)
    subprocess.Popen(["/bin/bash", "./start.sh"], cwd="/home/noahshinar/minecraft_servers/server1")


# SAY COMMAND
@bot.tree.command(name="say", description="/say command to say stuff as server cause it funi")
@app_commands.describe(message="Text to send to server")
async def say(interaction: discord.Interaction, message: str):
    user_role_ids = [role.id for role in interaction.user.roles]
    if OWNER_ROLE_ID not in user_role_ids:
        await interaction.response.send_message("You are not allowed to use this command.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    send_to_server(f"say {message}")
    await interaction.followup.send(f"Sent to server: `{message}`", ephemeral=True)


# STARTUP EVENTS
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    print("Auto-starting Minecraft server...")
    # subprocess.Popen(["/bin/bash", "./start.sh"], cwd="/home/noahshinar/minecraft_servers/server1")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands globally.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

##################################################################################################################
# BOT TOKEN
##################################################################################################################
with open("/home/noahs/Documents/DiscToServerBot/server1/DiscToServerBot/token.txt", "r") as f:
    TOKEN = f.read().strip()
bot.run(TOKEN)
##################################################################################################################
# BOT TOKEN
##################################################################################################################

'''
#-TO DO LIST!!!-#

- edit channel to show server status (Server On) (Server Off) (Server Starting)
- remove server on off starting from appearing in chat
- deaths leaderboard on discord server
- playtime leaderboard on discord server
- add bedrock players username and floodgate-UUID into json file from discord command
- scheduled auto restarts when zero players are online
- /say command to say stuff as server from discord
'''
