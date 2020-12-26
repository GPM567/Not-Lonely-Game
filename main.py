import discord, os
from discord.ext import commands

bot = commands.Bot(help_command=None, command_prefix="!")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(f"!도움 | 같이 플레이(n인큐) 모집 글 정리"))

for filename in os.listdir("cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run("token")
