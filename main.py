import discord, os
from discord.ext import commands

bot = commands.Bot(help_command=None, command_prefix="!")

for filename in os.listdir("cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run("NzkxODk0NjAwNDI3ODk2ODUz.X-VzUQ.iVDIBokYoPAmKtji6FpEQ7OBREU")