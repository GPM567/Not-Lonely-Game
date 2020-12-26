import discord
from discord.ext import commands
import customExceptions as ce
import db, ask, customUtils


emojiToMean = {'♂': '남', '♀': '여', '❔': '비공개/기타', '⭕': 'Yes', '❌': 'No'}
forDB = {'Yes': 1, 'No': 0}


class Register(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(name="가입")
    async def register(self, ctx: commands.Context):
        user = ctx.author
        if type(ctx.channel) is not discord.DMChannel:
            await ctx.send("DM 채널을 확인해주세요!")
        if {'discordID': user.id} in await db.read('users', f'SELECT discordID FROM "UserInfos"'):
            await user.send("이미 가입되어 있습니다. 정보 수정을 원하신다면 '!정보수정'을 이용해주세요.")
            return
        try:
            nickname = await ask.askText(self.bot, user, "이 서비스 내에서 사용할 닉네임")
            nickname = nickname.strip()
            if {'nickname': nickname} in await db.read('users', f'SELECT nickname FROM "UserInfos"'):
                await user.send("중복되는 닉네임입니다. '!가입'으로 다시 시도해주세요.")
                return
            letterN = customUtils.getLettersNum(nickname)
            if letterN > 16 or "\n" in nickname:
                await user.send("닉네임이 너무 깁니다. '!가입'으로 다시 시도해주세요.")
                return
            elif letterN < 4:
                await user.send("닉네임이 너무 짧습니다. '!가입'으로 다시 시도해주세요.")
            gender = emojiToMean[await ask.askReaction(self.bot, user, "성별", ['♂', '♀', '❔'])]
            age = await ask.askSelection(self.bot, user, "나이", ["10대", "20대", "30대", "40대 이상", "비공개"])
            canSpeak = emojiToMean[await ask.askReaction(self.bot, user, "보이스채팅 - 말하기 가능 여부", ['⭕', '❌'])]
            canListen = emojiToMean[await ask.askReaction(self.bot, user, "보이스채팅 - 듣기 가능 여부", ['⭕', '❌'])]
            embed = discord.Embed(title=f"{str(ctx.author)}님의 정보")
            embed.add_field(name="닉네임", value=nickname)
            embed.add_field(name="성별", value=gender)
            embed.add_field(name="나이", value=age)
            embed.add_field(name="보이스채팅 - 말하기 가능 여부", value=canSpeak)
            embed.add_field(name="보이스채팅 - 듣기 가능 여부", value=canListen)
            await user.send(embed=embed)
            if emojiToMean[await ask.askReaction(self.bot, user, "위 정보로 가입 여부", ['⭕', '❌'])] == "Yes":
                await db.run('users', f'INSERT INTO UserInfos VALUES (?, ?, ?, ?, ?, ?);', (user.id, nickname, age, gender, forDB[canSpeak], forDB[canListen]))
                await user.send("가입 완료!")
                if ctx.author.id not in [member.id for member in self.bot.get_guild(792311905020543027).members]:
                    embed = discord.Embed(title="공식 서버 초대 링크", description="[공식 서버](https://discord.gg/4ZXMF4XBZr)에 들어오세요!")
                    await user.send("공식 서버에 들어와 계시면 같이 플레이(n인큐) 글 작성/신청 시 유저를 만나기 더 쉬워집니다!", embed=embed)
            else:
                pass
        except ce.TimeoutError:
            return

    @commands.command(name="탈퇴")
    async def delete(self, ctx: commands.Context):
        if type(ctx.channel) is not discord.DMChannel:
            await ctx.send("DM 채널을 확인해주세요!")
        if emojiToMean[await ask.askReaction(self.bot, ctx.author, "정말로 탈퇴하시겠습니까? 탈퇴 여부", ['⭕', '❌'])] == "Yes":
            await db.run('users', "DELETE FROM UserInfos WHERE discordID = ?;", (ctx.author.id, ))
            await ctx.author.send("정상적으로 탈퇴되었습니다.")


def setup(bot: commands.Bot):
    bot.add_cog(Register(bot))