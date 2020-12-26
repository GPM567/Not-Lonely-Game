import discord, asyncio, math, uuid
from discord.ext import commands
import customExceptions as ce
import db, ask, findGame, customUtils

numEmojis = {'1️⃣': 1, '2️⃣': 2, '3️⃣': 3, '4️⃣': 4, '5️⃣': 5}
emojiToMean = {'⭕': 'Yes', '❌': 'No'}
forDB = {1: '가능', 0: '불가능'}

class Find(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(name="검색", aliases=["글검색"])
    async def search(self, ctx: commands.Context, *, name: str):
        gameName = await findGame.searchGame(name, self.bot, ctx)
        if gameName is None:
            return
        requests = await db.read("games", f'SELECT * FROM "{gameName}"')
        requests.reverse()
        pages = math.ceil(len(requests) / 5)
        nowPage = 0
        if len(requests) == 0:
            await ctx.send("해당 게임의 모집 글이 없어요! \n`!작성`으로 새로운 글을 올려보세요!")
        embedPages = []
        for i in range(pages):
            embed = discord.Embed(title=f"{gameName} 검색 결과", description=f"{i + 1} / {pages} 페이지\n"
                                                                         f"원하시는 번호의 이모지를 눌러 작성 유저분께 참가 신청을 보내주세요!")
            for j in range(5):
                try:
                    nowReq = requests[i * 5 + j]
                    authorID = nowReq["authorID"]
                    authorData = (await db.read("users", "SELECT * FROM UserInfos WHERE discordID is ?", (authorID, )))[0]
                    try:
                        if self.bot.get_guild(792311905020543027).get_member(authorID).status == discord.Status.offline:
                            statusText = "⚪오프라인"
                        else:
                            statusText = "🟢온라인"
                    except AttributeError:
                        statusText = "⚪알 수 없음"
                    embed.add_field(name=f"{tuple(numEmojis.keys())[j]} - {nowReq['title']} - {nowReq['count']}명 모집",
                                    value=f"작성 유저 - {authorData['nickname']}({statusText})(연령대: {authorData['age']} / 성별: {authorData['gender']}"
                                          f" / 보이스채팅(말하기/듣기): {forDB[authorData['canSpeak']]} / {forDB[authorData['canListen']]})"
                                          f"\n{nowReq['content']}", inline=False)
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
            for emoji in tuple(numEmojis.keys())[:len(requests)]:
                await embedMessage.add_reaction(emoji)
        else:
            for emoji in tuple(numEmojis.keys()):
                await embedMessage.add_reaction(emoji)
            await embedMessage.add_reaction("⬅")
            await embedMessage.add_reaction("➡")

        def check(reaction, user):
            return (str(reaction) in numEmojis.keys() or str(reaction) in ["⬅", "➡"]) and user == ctx.author and reaction.message.id == embedMessage.id

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=30)
                if str(reaction) in numEmojis.keys():
                    request = requests[nowPage * 5 + numEmojis[str(reaction)] - 1]
                    nickname = (await db.read("users", f"SELECT nickname FROM UserInfos WHERE discordID is {request['authorID']}"))[0]['nickname']
                    if emojiToMean[await ask.askReaction(self.bot, ctx,
                                                         f'{nickname}님께 메시지 전송 여부',
                                                         ['⭕', '❌'])] == "Yes":
                        userData = (await db.read("users",
                                       f"SELECT * FROM UserInfos WHERE discordID is {user.id}"))[0]
                        await self.bot.get_user(request['authorID']).send(
                            f"{(await db.read('users', f'SELECT nickname FROM UserInfos WHERE discordID is {user.id}'))[0]['nickname']}"
                            f"({self.bot.get_user(user.id).mention} - `{str(self.bot.get_user(user.id))}`)\n"
                            f"(연령대: {userData['age']} / 성별: {userData['gender']} / 보이스채팅(말하기/듣기): {forDB[userData['canSpeak']]} / {forDB[userData['canListen']]})"
                            f"님이\n{request['title']} 글에 같이 플레이(n인큐) 참가 신청을 보내셨어요!\n"
                            f"DM을 통해 신청자분께 연락해주세요. 같이 플레이(n인큐) 모집 인원이 전부 채워진 경우 `!목록 (게임명)` 명령어로 글을 삭제해주세요."
                        )
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
    async def write(self, ctx: commands.Context, *, name: str):
        gameName = await findGame.searchGame(name, self.bot, ctx)
        if gameName is None:
            return
        count = await ask.askText(self.bot, ctx, "같이 플레이(n인큐) 모집 인원수")
        if not count.isdecimal():
            await ctx.send("정확한 수를 입력해주세요. '!작성'으로 다시 시도해주세요.")
            return
        elif int(count) > 99:
            await ctx.send("수가 너무 큽니다. '!작성'으로 다시 시도해주세요.")
            return
        elif int(count) < 1:
            await ctx.send("수가 너무 작습니다. `!작성`으로 다시 시도해주세요.")
        count = int(count)
        title = await ask.askText(self.bot, ctx, "제목(2자 이상 20자 이내)")
        letterN = customUtils.getLettersNum(title)
        if letterN < 4:
            await ctx.send("제목이 너무 짧습니다. '!작성'으로 다시 시도해주세요.")
            return
        elif letterN > 40 or "\n" in title:
            await ctx.send("제목이 너무 깁니다. '!작성'으로 다시 시도해주세요.")
            return
        content = await ask.askText(self.bot, ctx, "본문(50자 이내, 6줄 이내)", timeout=90)
        letterN = customUtils.getLettersNum(content)
        if letterN > 100 or content.count("\n") > 5:
            await ctx.send("본문이 너무 길거나 줄이 너무 많습니다. '!작성'으로 다시 시도해주세요.")
            return
        await db.run("games", f"""INSERT INTO "{gameName}" VALUES
  (?, ?, ?, ?, ?)
;""", (str(uuid.uuid4()), ctx.author.id, count, title, content))
        await ctx.send("글 등록 완료!")

    @commands.command(name="목록", aliases=["내글목록"])
    async def reqList(self, ctx: commands.Context, name: str):
        gameName = await findGame.searchGame(name, self.bot, ctx)
        if gameName is None:
            return
        myRequests = await db.read("games", f'SELECT * FROM "{gameName}" WHERE authorID is ?', (ctx.author.id, ))
        pages = math.ceil(len(myRequests) / 5)
        nowPage = 0
        embedPages = []
        if len(myRequests) == 0:
            await ctx.send("글을 보내지 않으셨어요!")
            return
        for i in range(pages):
            embed = discord.Embed(title=f"{gameName}의 작성하신 글 검색 결과", description=f"{i + 1} / {pages} 페이지\n"
                                                                                 f"원하시는 번호의 이모지를 눌러 글을 삭제하실 수 있습니다.")
            for j in range(5):
                try:
                    embed.add_field(name=f"{tuple(numEmojis.keys())[j]} - {myRequests[i * 5 + j]['title']}", value=myRequests[i * 5 + j]['content'], inline=False)
                except IndexError:
                    continue
            if i + 1 == pages:
                embed.add_field(name="마지막 페이지입니다.",
                                value="같이 플레이(n인큐) 모집 인원이 모두 채워졌다면 꼭 글을 삭제해주세요!",
                                inline=False)
            embedPages.append(embed)
        embedMessage = await ctx.send(embed=embedPages[0])
        if len(myRequests) < 5:
            for emoji in tuple(numEmojis.keys())[:len(myRequests)]:
                await embedMessage.add_reaction(emoji)
        else:
            for emoji in tuple(numEmojis.keys()):
                await embedMessage.add_reaction(emoji)
            await embedMessage.add_reaction("⬅")
            await embedMessage.add_reaction("➡")

        def check(reaction, user):
            return (str(reaction) in tuple(numEmojis.keys()) or str(reaction) in ["⬅", "➡"]) and user == ctx.author and reaction.message.id == embedMessage.id

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=15)
                if str(reaction) in tuple(numEmojis.keys()):
                    willDel = myRequests[nowPage * 5 + numEmojis[str(reaction)] - 1]
                    if emojiToMean[await ask.askReaction(self.bot, ctx,
                                                         f'{willDel["title"]} 모집 글 삭제 여부',
                                                         ['⭕', '❌'])] == "Yes":
                        await db.run("games", f'DELETE FROM "{gameName}" WHERE requestID is "{willDel["requestID"]}"')
                        await ctx.send("정상적으로 삭제되었습니다.")
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
                return None


def setup(bot: commands.Bot):
    bot.add_cog(Find(bot))