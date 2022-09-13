import aiohttp
import asyncio
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
LOCAL_DIR = os.path.curdir + "/banners/"
INTENTS = discord.Intents.all()
BOT = commands.Bot(command_prefix = ".", description = "ggnosis-dev was here", intents = INTENTS)     # change prefix for preference
BOT.remove_command("help")
running_loops = []
loop_timer = 20 * 60
current_index = 0

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
        #return False
    return True

# URL validations
# Expand on this
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
    if await server_validation(ctx):
        await ctx.send(ctx.message.guild.banner)
        await ctx.message.add_reaction("✅")

# Set server banner
@banner_cmds.command(name = "set")
async def set_banner(ctx, *args):
    if await user_validation(ctx) and await server_validation(ctx): 
        if args[0] == "--random" or args[0] == "-r": 
            await set_banner_random(ctx)
        elif await url_validation(ctx, args[0]): 
            await set_banner_url(ctx, args[0])

# Start banner cycle loop
@banner_cmds.command(name = "start")
async def start_banner_cycle(ctx):
    if await user_validation(ctx) and await server_validation(ctx):
        for task in running_loops:
            if task.get_name() == "looping":
                await ctx.send("Server is already cycling through banners.")
                return
        loop = asyncio.get_running_loop()
        new_loop = loop.create_task(random_banner_loop(ctx), name = "looping")
        running_loops.append(new_loop)

# Stop banner cycle loop
@banner_cmds.command(name = "stop")
async def stop_banner_cycle(ctx):
    if await user_validation(ctx) and await server_validation(ctx):
        for task in running_loops:
            if task.get_name() != "looping":
                continue
            elif not task.cancelled():
                try:
                    task.cancel()
                    running_loops.remove(task)
                except asyncio.CancelledError as e:
                    print(e)
                    await ctx.message.add_reaction("❌")
                    await ctx.send("Problem cancelling looped task. Try again, restart the bot or contact **@ggnosis#8888** for support.")
                    return
                print(f"Looping task has been cancelled")
                await ctx.message.add_reaction("✅")

@banner_cmds.command(name = "timer")
async def set_loop_timer(ctx, *args):
    global loop_timer
    if not args:
        await ctx.send(f"Timer is currently set to cycle in {int(loop_timer / 60)} minute intervals. You can change this by typing `.banner timer --set <number>`.")
        return
    if args[0] == "--set" or args[0] == "-s":
        if len(args) < 2 or int(args[1]) <= 0:
            await ctx.send("Please provide a number.")
            await ctx.message.add_reaction("❌")
            return
        loop_timer = int(args[1]) * 60
        #await restart_banner_loop()
        await ctx.send(f"Timer has been set to cycle in {args[1]} minute intervals.")
        await ctx.message.add_reaction("✅")

# Random Banner loop
async def random_banner_loop(ctx):
    while True:
        await BOT.wait_until_ready()
        print("Bot is ready for banner update.")
        next_cycle = loop_timer
        await set_banner_random(ctx)
        print(f"Banner updated for server: {ctx.message.guild}. Next update in {next_cycle}")
        await asyncio.sleep(next_cycle)

# Restart banner loop
async def restart_banner_loop():
    for task in running_loops:
        if task.get_name() != "looping":
            continue
        elif not task.cancelled():          # if running

            print("Restarted")

# Banner images cycle randomly
async def set_banner_random(ctx):
    if check_dir_exists(ctx):
        global current_index
        _dir_list = os.listdir(LOCAL_DIR) 
        _image_file = random.choice(_dir_list)
        _image_path = os.path.join(LOCAL_DIR, _image_file)
        current_index = _dir_list.index(_image_file)
        await set_banner_image(ctx, _image_path)

# Banner images cycle in ascending/descending order 
async def set_banner_ordered(ctx, asc : bool):
    if check_dir_exists(ctx):
        global current_index
        _dir_list = os.listdir(LOCAL_DIR)
        _image_path = os.path.join(LOCAL_DIR, _dir_list[current_index])

        if asc and len(_dir_list) < current_index:         # if there are still entries in the directory 
            current_index += 1
        elif not asc and len(_dir_list) > current_index:
            current_index -= 1
        else:
            current_index = 0
        await set_banner_image(ctx, _image_path)

# sets the provided image
async def set_banner_image(ctx, image_path):
    with open(image_path, "rb") as data:
        print(f"Setting banner for server: {ctx.message.guild} to: {image_path}")
        try:
            await ctx.message.guild.edit(icon = data.read())
        except Exception as e:
            print(e)
            await ctx.send("Problem setting banner. Try again, restart the bot or contact **@ggnosis#8888** for support.")
            await ctx.message.add_reaction("❌")
    await ctx.message.add_reaction("✅")

async def check_dir_exists(ctx):
    if not os.path.exists(LOCAL_DIR):
        await ctx.send("There is no gallery assigned to your server. Add the folder `banners` to the root of the bot's directory.")
        await ctx.message.add_reaction("❌")
        return False
    return True

# Set with link
async def set_banner_url(ctx, url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:                                      # if the response is not OK (200) response code
                await ctx.send("Failed to download the file.") 
                await ctx.message.add_reaction("❌")
                return

            data = io.BytesIO(await response.read())
            await ctx.message.guild.edit(icon = data.read())
            await ctx.message.add_reaction("✅")





BOT.run(TOKEN)