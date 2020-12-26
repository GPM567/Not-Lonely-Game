import math, asyncio, discord
from discord.ext import commands
import db

numEmojis = {'1️⃣': 1, '2️⃣': 2, '3️⃣': 3, '4️⃣': 4, '5️⃣': 5}


async def searchGame(name: str, bot: commands.Bot, sendTo):
    name = name.upper().strip()
    games = await db.read("games", "SELECT name FROM GameNames WHERE nickname like ?", (f"%{name}%",))
    pages = math.ceil(len(games) / 5)
    nowPage = 0
    embedPages = []
    for i in range(pages):
        embed = discord.Embed(title=f"게임 검색 결과", description=f"{i + 1} / {pages} 페이지")
        for j in range(5):
            try:
                embed.add_field(name=f"{tuple(numEmojis.keys())[j]}", value=games[i * 5 + j]["name"], inline=False)
            except IndexError:
                continue
        if i + 1 == pages:
            embed.add_field(name="마지막 페이지입니다.",
                            value="검색 결과가 없으시다면\n"
                                  "검색어의 수를 줄여보시거나\n"
                                  "더 대중적인 검색어로 검색해보세요.",
                            inline=False)
        embedPages.append(embed)
    if not embedPages:
        await sendTo.send("검색 결과가 없어요! 검색어의 수를 줄여보시거나 더 대중적인 검색어로 검색해보세요.")
        return None
    embedMessage = await sendTo.send(embed=embedPages[0])
    if len(games) < 5:
        for emoji in tuple(numEmojis.keys())[:len(games)]:
            await embedMessage.add_reaction(emoji)
    else:
        for emoji in tuple(numEmojis.keys()):
            await embedMessage.add_reaction(emoji)
        await embedMessage.add_reaction("⬅")
        await embedMessage.add_reaction("➡")

    def check(reaction, user):
        return (str(reaction) in tuple(numEmojis.keys()) or str(reaction) in ["⬅", "➡"]) and user == sendTo.author and reaction.message.id == embedMessage.id

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", check=check, timeout=15)
            if str(reaction) in tuple(numEmojis.keys()):
                return games[nowPage * 5 + numEmojis[str(reaction)] - 1]['name']
            elif str(reaction) == "⬅":
                if nowPage == 0:
                    await sendTo.send("첫 페이지입니다.")
                else:
                    nowPage -= 1
                    await embedMessage.edit(embed=embedPages[nowPage])
            else:
                if nowPage == pages - 1:
                    await sendTo.send("마지막 페이지입니다.")
                else:
                    nowPage += 1
                    await embedMessage.edit(embed=embedPages[nowPage])
        except asyncio.TimeoutError:
            await sendTo.send("시간이 초과되었습니다. 다시 시작해주세요.")
            return None