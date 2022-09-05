import discord
import help_commands
import os
from discord.ext    import commands
from dotenv         import load_dotenv

# Bot setup
load_dotenv("data/.env")
TOKEN = os.getenv("TOKEN")      # Your unique Bot Token
LOCAL_BANNER_PATH = "/banners/"
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

# Server validations
async def server_validation(ctx):
    if ctx.message.guild.premium_tier < 2:
        await ctx.send("This server does not have access to a banner (Need Nitro level 2).")
        await ctx.message.add_reaction("❌")
        return False
    return True

# Events
@BOT.event
async def on_ready():
    await BOT.change_presence(activity = discord.Game(name = "ggnosis-dev was here"))
    print("Logged in: ", BOT.user)

# Help commands
@BOT.group(name = "banner", invoke_without_command = True)
async def banners_commands(ctx, option : str = "help"):
    if option == "help":
        help_msg = discord.Embed(title = "▬▬ **__BANNER COMMANDS__** ▬▬", colour = 0x970A3D, description = help_commands.BANNER_DESC)
        help_msg.set_footer(text = help_commands.BANNER_HELP)
        await ctx.send(embed = help_msg)
