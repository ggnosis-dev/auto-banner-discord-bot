import discord
import os
from discord.ext    import commands
from dotenv         import load_dotenv

# Bot setup
load_dotenv("data/.env")
TOKEN = os.getenv("TOKEN")      # Your unique Bot Token
BOT = commands.Bot(command_prefix = ".", description = "ggnosis-dev was here")     # change prefix for preference
BOT.remove_command("help")

# User validations
async def user_validation(ctx):
    author_perms = ctx.message.author.permissions_in(ctx.channel)
    
    if not author_perms.administrator:
        await ctx.send("User does not have the required permissions to change the icon. Must have administrator permissions.")
        await ctx.message.add_reaction("❌")
        return False
    return True

@BOT.event
async def on_ready():
    await BOT.change_presence(activity = discord.Game(name = "ggnosis-dev was here"))
    print("Logged in: ", BOT.user)

