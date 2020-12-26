import discord, asyncio, math
from discord.ext import commands
import customExceptions as ce
import db, ask

numEmojis = {'1️⃣': 1, '2️⃣': 2, '3️⃣': 3, '4️⃣': 4, '5️⃣': 5}
emojiToMean = {'⭕': 'Yes', '❌': 'No'}


class Find(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(name="검색")
    async def search(self, ctx: commands.Context, name: str):
        name = name.upper().strip()
        games = await db.read("games", "SELECT name FROM GameNames WHERE nickname like ?", (f"%{name}%", ))
        pages = math.ceil(len(games) / 5)
        nowPage = 0
        embedPages = []
        for i in range(pages):
            embed = discord.Embed(title=f"게임 검색 결과", description=f"{i+1} / {pages} 페이지")
            for j in range(5):
                try:
                    embed.add_field(name=f"{tuple(numEmojis.keys())[j]}", value=games[i*5+j]["name"], inline=False)
                except IndexError:
                    continue
            if i+1 == pages:
                embed.add_field(name="마지막 페이지입니다.",
                                value="검색 결과가 없으시다면\n"
                                      "검색어의 수를 줄여보시거나\n"
                                      "더 대중적인 검색어로 검색해보세요.",
                                inline=False)
            embedPages.append(embed)
        embedMessage = await ctx.send(embed=embedPages[0])
        if len(games) < 5:
            for emoji in tuple(numEmojis.keys())[:len(games)]:
                await embedMessage.add_reaction(emoji)
        else:
            for emoji in tuple(numEmojis.keys()):
                await embedMessage.add_reaction(emoji)
            await embedMessage.add_reaction("⬅")
            await embedMessage.add_reaction("➡")
        def check(reaction, user):
            return str(reaction) in tuple(numEmojis.keys()) or str(reaction) in ["⬅", "➡"] and user == ctx.author
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=15)
                if str(reaction) in tuple(numEmojis.keys()):
                    gameName = games[nowPage*5+numEmojis[str(reaction)]-1]['name']
                    break
                elif str(reaction) == "⬅":
                    if nowPage == 0:
                        await ctx.send("첫 페이지입니다.")
                    else:
                        nowPage -= 1
                        await embedMessage.edit(embed=embedPages[nowPage])
                else:
                    if nowPage == pages-1:
                        await ctx.send("마지막 페이지입니다.")
                    else:
                        nowPage += 1
                        await embedMessage.edit(embed=embedPages[nowPage])
            except asyncio.TimeoutError:
                await ctx.send("시간이 초과되었습니다. 다시 시작해주세요.")
                return

        requests = await db.read("games", f'SELECT * FROM "{gameName}"')
        pages = math.ceil(len(games) / 5)
        nowPage = 0
        embedPages = []
        for i in range(pages):
            embed = discord.Embed(title=f"{gameName} 검색 결과", description=f"{i + 1} / {pages} 페이지")
            for j in range(5):
                try:
                    nowReq = requests[i * 5 + j]
                    await db.read("games", "SELECT * FROM UserInfos")
                    authorID = nowReq["authorID"]

                    embed.add_field(name=f"{tuple(numEmojis.keys())[j]} - {nowReq['title']}",
                                    value=f"작성 유저 - {nowReq['au']}({})\n{nowReq['content']}", inline=False)
                except IndexError:
                    continue
            if i + 1 == pages:
                embed.add_field(name="마지막 페이지입니다.",
                                value="선호하는 유저분이 계시지 않으신가요?\n"
                                      "'!작성'으로 새로운 글을 올려보세요!",
                                inline=False)
            embedPages.append(embed)
        embedMessage = await ctx.send(embed=embedPages[0])
        if len(requests) < 5:
            for emoji in tuple(numEmojis.keys())[:len(games)]:
                await embedMessage.add_reaction(emoji)
        else:
            for emoji in tuple(numEmojis.keys()):
                await embedMessage.add_reaction(emoji)
            await embedMessage.add_reaction("⬅")
            await embedMessage.add_reaction("➡")

        def check(reaction, user):
            return str(reaction) in numEmojis.keys() or str(reaction) in ["⬅", "➡"] and user == ctx.author

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=30)
                if str(reaction) in numEmojis.keys():
                    if emojiToMean[await ask.askReaction(self, user,
                                                         f"{games[nowPage*5+numEmojis[str(reaction)]]['nickname']}님께 메시지 전송 여부", ['⭕', '❌'])] == "Yes":
                        break
                    else:
                        continue
                elif str(reaction) == "⬅":
                    if nowPage == 0:
                        await ctx.send("첫 페이지입니다.")
                    else:
                        nowPage -= 1
                        await embedMessage.edit(embed=embedPages[nowPage])
                else:
                    if nowPage == pages - 1:
                        await ctx.send("마지막 페이지입니다.")
                    else:
                        nowPage += 1
                        await embedMessage.edit(embed=embedPages[nowPage])
            except asyncio.TimeoutError:
                await ctx.send("시간이 초과되었습니다. 다시 시작해주세요.")
                return

    @commands.command(name="작성", aliases=("글작성",))
    async def write(self, ctx: commands.Context):

def setup(bot: commands.Bot):
    bot.add_cog(Find(bot))