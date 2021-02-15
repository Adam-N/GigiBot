import random

import discord
from discord.ext import commands


class Friend(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='nomean', description="For a friend who's being mean to themself!")
    async def nomean(self, ctx):
        """This command is for a friend who is being mean to themselves.
        Show them who's boss and cheer them up!"""
        embed = discord.Embed(color=0x00ff00)
        embed.title = "Don't be mean to yourself"
        embed.description = 'This is because we love you'
        embed.set_image(
            url='https://cdn.discordapp.com/attachments/532380077896237061/791855065111592970/20200928_123113.jpg')
        await ctx.channel.send(embed=embed)

    @commands.command(name='nosuck', description= "For friend's who think they suck.")
    async def nosuck(self, ctx):
        """This command will make your friend think twice about saying that they suck! (In a good way!"""
        embed = discord.Embed(color=0x00ff00)
        embed.title = "Don't be mean to yourself"
        embed.description = 'This is because we love you'
        embed.set_image(
            url='https://cdn.discordapp.com/attachments/532380077896237061/791855064804753418/fql8g0wcp1o51.jpg')
        await ctx.channel.send(embed=embed)

    @commands.command(aliases = ['hornyjail','nohorny','horny'], description="For someone who's getting a little lewd.")
    async def horny_jail(self, ctx):
        """This command is meant for that certain friend who's started themselves down the path of sin. UwU"""
        images = ["https://media.tenor.com/images/f781d9b1bbc4839dff9ad763c28deb46/tenor.gif",
                  "https://media1.tenor.com/images/6493bee2be7ae168a5ef7a68cf751868/tenor.gif?itemid=17298755",
                  "https://media.discordapp.net/attachments/767568459939708950/807751886278492170/no_horny.gif"]
        url = random.choice(images)
        embed = discord.Embed(color=0x00ff00)
        embed.title = "You're gross."
        embed.description = 'This is for your own good'
        embed.set_image(url=url)
        await ctx.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Friend(bot))