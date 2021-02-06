import random

import discord
from discord.ext import commands


class Friend(commands.Cog):
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

    @commands.command(aliases = ['hornyjail','nohorny','horny'])
    async def horny_jail(self, ctx):
        """Sends a nice message to a friend who tells themselves that they suck"""
        images = ["https://media.tenor.com/images/f781d9b1bbc4839dff9ad763c28deb46/tenor.gif",
                  "https://media1.tenor.com/images/6493bee2be7ae168a5ef7a68cf751868/tenor.gif?itemid=17298755"]
        url = random.choice(images)
        embed = discord.Embed(color=0x00ff00)
        embed.title = "You're gross."
        embed.description = 'This is because we love you'
        embed.set_image(url=url)
        await ctx.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Friend(bot))