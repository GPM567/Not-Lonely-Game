import discord, asyncio
from discord.ext import commands
import customExceptions as ce

async def askText(bot, toSend, whatToAsk: str, timeout: int = 30):
    askMessage = await toSend.send(f"{whatToAsk}을(를) {timeout}초 내에 입력해주세요.")

    def check(message):
        if type(toSend) is commands.Context:
            return message.channel == askMessage.channel and toSend.author == message.author and message
        elif type(toSend) is discord.User or type(toSend) is discord.Member:
            return message.channel == askMessage.channel and toSend.id == message.author.id

    try:
        message = await bot.wait_for('message', timeout=timeout, check=check)
        return message.content
    except asyncio.TimeoutError:
        await toSend.send("시간이 초과되었습니다. 다시 시작해 주세요.")
        raise ce.TimeoutError


async def askReaction(bot, toSend, whatToAsk: str, reactions: list, timeout: int = 30):
    askMessage = await toSend.send(f"{whatToAsk}을(를) {timeout}초 내에 선택해주세요.")
    for reaction in reactions:
        await askMessage.add_reaction(reaction)

    def check(reaction, user):
        if type(toSend) is commands.Context:
            return user.id == toSend.author.id and str(reaction.emoji) in reactions and \
                   reaction.message.channel == askMessage.channel and reaction.message.id == askMessage.id
        elif type(toSend) is discord.User or type(toSend) is discord.Member:
            return user.id == toSend.id and str(reaction.emoji) in reactions and \
                   reaction.message.channel == askMessage.channel and reaction.message.id == askMessage.id

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=timeout, check=check)
        return str(reaction)
    except asyncio.TimeoutError:
        await toSend.send("시간이 초과되었습니다. 다시 시작해 주세요.")
        raise ce.TimeoutError


async def askSelection(bot, toSend, whatToAsk: str, items: list, timeout: int = 30):
    n = '\n'
    numEmojis = {'1️⃣': 1, '2️⃣': 2, '3️⃣': 3, '4️⃣': 4, '5️⃣': 5}
    askMessage = await toSend.send(
        f"{whatToAsk}을(를) {timeout}초 내에 선택해주세요.\n{n.join([f'{i + 1}. {item}' for i, item in enumerate(items)])}")
    for reaction in list(numEmojis.keys()):
        await askMessage.add_reaction(reaction)

    def check(reaction, user):
        if type(toSend) is commands.Context:
            return user.id == toSend.author.id and str(reaction.emoji) in numEmojis.keys() and \
                   reaction.message.channel == askMessage.channel and reaction.message.id == askMessage.id
        elif type(toSend) is discord.User or type(toSend) is discord.Member:
            return user.id == toSend.id and str(reaction.emoji) in numEmojis.keys() and \
                   reaction.message.channel == askMessage.channel and reaction.message.id == askMessage.id

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=timeout, check=check)
        return items[numEmojis[str(reaction)] - 1]
    except asyncio.TimeoutError:
        await toSend.send("시간이 초과되었습니다. 다시 시작해 주세요.")
        raise ce.TimeoutError