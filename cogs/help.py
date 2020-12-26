import discord, json
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(name="도움", aliases=["help"])
    async def helpC(self, ctx: commands.Context):
        embed = discord.Embed(title="외롭지 않은 게임 명령어 목록")
        embed.add_field(name="!가입", value="이 서비스에 가입합니다.", inline=False)
        embed.add_field(name="!탈퇴", value="이 서비스를 탈퇴합니다.", inline=False)
        embed.add_field(name="!글검색 (게임명) / !검색 (게임명)", value="해당 게임의 같이 플레이(n인큐) 모집 글을 검색합니다.", inline=False)
        embed.add_field(name="!글작성 (게임명) / !작성 (게임명)", value="해당 게임의 같이 플레이(n인큐) 모집 글을 작성합니다.", inline=False)
        embed.add_field(name="!내글목록 (게임명) / !목록 (게임명)", value="내가 작성한 해당 게임의 모집 글 목록을 보거나 글을 삭제합니다.", inline=False)
        embed.add_field(name="!도움", value="이 도움말을 출력합니다.", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="게임신청", aliases=["게임추가"])
    async def addGame(self, ctx: commands.Context, *, name: str):
        with open("../data/addGames.json", 'r') as f:
            data = json.load(f)
        if name in data.keys():
            data[name] += 1
        else:
            data[name] = 1


def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))