import discord
from discord.ext import commands
import customExceptions as ce
import db, ask

emojiToMean = {'♂': '남', '♀': '여', '❔': '비공개/기타', '⭕': 'Yes', '❌': 'No'}
forDB = {'Yes': 1, 'No': 0}

class Register(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(name="가입")
    async def register(self, ctx: commands.Context):
        user = ctx.author
        if {'discordID': user.id} in await db.read('users', f'SELECT discordID FROM "UserInfos"'):
            await ctx.send("이미 가입되어 있습니다. 정보 수정을 원하신다면 '!정보수정'을 이용해주세요.")
            return
        if type(ctx.channel) is not discord.DMChannel:
            await ctx.send("DM 채널을 확인해주세요!")
        try:
            nickname = await ask.askText(self, user, "이 서비스 내에서 사용할 닉네임")
            nickname = nickname.strip()
            if {'nickname': nickname} in await db.read('users', f'SELECT nickname FROM "UserInfos"'):
                await ctx.send("중복되는 닉네임입니다. '!가입'으로 다시 시도해주세요.")
                return
            gender = emojiToMean[await ask.askReaction(self, user, "성별", ['♂', '♀', '❔'])]
            age = await ask.askSelection(self, user, "나이", ["10대", "20대", "30대", "40대 이상", "비공개"])
            canSpeak = emojiToMean[await ask.askReaction(self, user, "보이스채팅 - 말하기 가능 여부", ['⭕', '❌'])]
            canListen = emojiToMean[await ask.askReaction(self, user, "보이스채팅 - 듣기 가능 여부", ['⭕', '❌'])]
            embed = discord.Embed(title=f"{str(ctx.author)}님의 정보")
            embed.add_field(name="닉네임", value=nickname)
            embed.add_field(name="성별", value=gender)
            embed.add_field(name="나이", value=age)
            embed.add_field(name="보이스채팅 - 말하기 가능 여부", value=canSpeak)
            embed.add_field(name="보이스채팅 - 듣기 가능 여부", value=canListen)
            await user.send(embed=embed)
            if emojiToMean[await ask.askReaction(self, user, "위 정보로 가입 여부", ['⭕', '❌'])] == "Yes":
                await db.run('users', f'INSERT INTO UserInfos VALUES (?, ?, ?, ?, ?, ?);', (user.id, nickname, age, gender, forDB[canSpeak], forDB[canListen]))
                await ctx.send("가입 완료!")
            else:
                pass
        except ce.TimeoutError:
            return




def setup(bot: commands.Bot):
    bot.add_cog(Register(bot))