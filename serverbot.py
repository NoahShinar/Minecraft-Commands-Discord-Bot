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
import time

##################################################################################################################
# Bot Code
##################################################################################################################
#
# Change to role ID assigned to owner
OWNER_ROLE_ID = 1437183305266106558 
#
# Change to role ID assigned to admins
ADMIN_ROLE_ID = 1437182763093463101 
#
# Change to your discord server's ID
GUILD_ID = 1437180858367868950 
#
# Change path to your own whitelist file
WHITELIST_FILE = "/home/noahshinar/minecraft_servers/server1/whitelist.json"
#
# Change path to your own bot token file
TOKEN_FILE = "/home/noahs/Documents/DiscToServerBot/server1/DiscToServerBot/token.txt" 
#
#

#
#--DO NOT CHANGE BOT WILL BREAK--#
#
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
print("Loaded commands at startup:", bot.tree.get_commands())
#
#--DO NOT CHANGE BOT WILL BREAK--#
#

##################################################################################################################
# PRE-CONDITIONS
##################################################################################################################
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
                return data.get("id") 
            return None

def send_to_server(cmd: str):
    subprocess.run(["mcrcon", "-H", "127.0.0.1", "-P", "25575", "-p", "4630", f"{cmd}"])

async def is_owner(interaction: discord.Interaction):
    user_role_ids = [role.id for role in interaction.user.roles]
    if OWNER_ROLE_ID not in user_role_ids:
        await interaction.response.send_message("You are not allowed to use this command.", ephemeral=True)
        return

async def is_owner_and_admin(interaction: discord.Interaction):
    user_role_ids = [role.id for role in interaction.user.roles]
    if OWNER_ROLE_ID not in user_role_ids and ADMIN_ROLE_ID not in user_role_ids:
        await interaction.response.send_message("You are not allowed to use this command.", ephemeral=True)
        return

##################################################################################################################
# SLASH COMMANDS
##################################################################################################################
# WHITELIST ADD COMMAND
@bot.tree.command(name="whitelist", description="Add a Minecraft username to the whitelist")
@app_commands.describe(username="Whitelist username")
async def whitelist(interaction: discord.Interaction, username: str):
    is_owner_and_admin()
    # is_owner()

    uuid = await get_uuid(username)
    if uuid is None:
        return await interaction.response.send_message(f"Couldn't find a profile with the name: **{username}**", ephemeral=True)

    if is_whitelisted(username):
        return await interaction.response.send_message(f"**{username}** is already whitelisted.", ephemeral=True)

    send_to_server(f"whitelist add {username}")
    await interaction.response.send_message(f"Added **{username}** to the whitelist.")

# START SERVER COMMAND
@bot.tree.command(name="start", description="Start the Minecraft server")
async def start(interaction: discord.Interaction):
    # is_owner_and_admin()
    is_owner()

    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send("Starting server...", ephemeral=True)
    subprocess.Popen(["/bin/bash", "./start.sh"], cwd="/home/noahshinar/minecraft_servers/server1")

# SAY COMMAND
@bot.tree.command(name="say", description="/say command to say stuff as server cause it funi")
@app_commands.describe(message="Text to send to server")
async def say(interaction: discord.Interaction, message: str):
    # is_owner_and_admin()
    is_owner()

    await interaction.response.defer(ephemeral=True)
    send_to_server(f"say {message}")
    await interaction.followup.send(f"Sent to server: `{message}`", ephemeral=True)

# RESTART COMMAND
@bot.tree.command(name="restart", description="restarts the server")
async def restart(interaction: discord.Integration):
    # is_owner_and_admin()
    is_owner()

    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send("Stopping server...", ephemeral=True)
    send_to_server(f"stop")
    await interaction.followup.send("Starting server...", ephemeral=True)
    subprocess.Popen(["/bin/bash", "./start.sh"], cwd="/home/noahshinar/minecraft_servers/server1")

# SET SERVER STATUS CHANNEL COMMAND
@bot.tree.command(name="statusChannel", description="Changes name of custom channel to server status")
@app_commands.describe(channelID="Input channel ID")
async def statusChannel(interaction: discord.Integration):
    # is_owner_and_admin()
    is_owner()
    


##################################################################################################################
# STARTUP EVENTS
##################################################################################################################
@bot.event
async def on_ready():
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
with open(TOKEN_FILE, "r") as f:
    TOKEN = f.read().strip()
bot.run(TOKEN)
##################################################################################################################
# BOT TOKEN
##################################################################################################################


