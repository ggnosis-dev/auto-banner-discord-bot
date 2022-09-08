import aiohttp
import discord
import io
import help_commands
import os
import random
from discord.ext    import commands
from dotenv         import load_dotenv

# Bot setup
load_dotenv("data/.env")
TOKEN = os.getenv("TOKEN")      # Your unique Bot Token
LOCAL_BANNER_PATH = "/banners/"
INTENTS = discord.Intents.all()
BOT = commands.Bot(command_prefix = ".", description = "ggnosis-dev was here", intents = INTENTS)     # change prefix for preference
BOT.remove_command("help")

# User validations
async def user_validation(ctx):
    author_perms = ctx.message.author.guild_permissions.administrator
    
    if not author_perms:
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

# URL validations
async def url_validation(ctx, url):
    if not url.startswith('https'):
        await ctx.send("Please input a valid URL.")
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
async def banner_cmds(ctx, option : str = "help"):
    if option == "help":
        help_msg = discord.Embed(title = "▬▬ **__BANNER COMMANDS__** ▬▬", colour = 0x970A3D, description = help_commands.BANNER_DESC)
        help_msg.set_footer(text = help_commands.BANNER_HELP)
        await ctx.send(embed = help_msg)

# Commands
# Get server banner
@banner_cmds.command(name = "get")
async def get_banner(ctx):
    if await server_validation(ctx) == False:
        return

    await ctx.send(ctx.message.guild.banner_url)
    await ctx.message.add_reaction("✅")

# Set server banner
@banner_cmds.command(name = "set")
async def set_banner(ctx, *args):
    if await user_validation(ctx) and await server_validation(ctx): 
        if args[0] == "--random" or "-r": 
            await set_banner_random(ctx)
        elif await url_validation(ctx, args[0]): 
            set_banner_url(ctx, args[0])

# Set random
async def set_banner_random(ctx):
    if await user_validation() and await server_validation():
        return
    
    dir = os.path.curdir + "/banners/"
    if not os.path.exists(dir):
        await ctx.send("There is no gallery assigned to your server. Add the folder `banners` to the root of the bot's directory.")
        return
    
    image_file = random.choice(os.listdir(dir))
    image_path = os.path.join(dir, image_file)
    with open(image_path, "rb") as data:
        print(f"Setting banner for server: {ctx.message.guild} to: {image_path}")
        try:
            await ctx.message.guild.edit(banner = data.read())
        except Exception as e:
            print(e)
    await ctx.message.add_reaction("✅")

# Set with link
async def set_banner_url(ctx, url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:                                      # if the response is not OK (200) response code
                await ctx.send("Failed to download the file.") 
                await ctx.message.add_reaction("❌")
                return

            data = io.BytesIO(await response.read())
            await ctx.message.guild.edit(banner = data.read())
            await ctx.message.add_reaction("✅")






BOT.run(TOKEN)