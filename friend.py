import discord
from discord.ext import commands


class FriendCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='nomean')
    async def nomean(self, ctx):
        """Sends a nice message to a friend who is being mean to themselves"""
        embed = discord.Embed(color=0x00ff00)
        embed.title = "Don't be mean to yourself"
        embed.description = 'This is because we love you'
        embed.set_image(
            url='https://cdn.discordapp.com/attachments/532380077896237061/791855065111592970/20200928_123113.jpg')
        await ctx.channel.send(embed=embed)

    @commands.command(name='nosuck')
    async def nosuck(self, ctx):
        """Sends a nice message to a friend who tells themselves that they suck"""
        embed = discord.Embed(color=0x00ff00)
        embed.title = "Don't be mean to yourself"
        embed.description = 'This is because we love you'
        embed.set_image(
            url='https://cdn.discordapp.com/attachments/532380077896237061/791855064804753418/fql8g0wcp1o51.jpg')
        await ctx.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(FriendCog(bot))