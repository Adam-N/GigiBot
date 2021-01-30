import discord
from discord.ext import commands
import random


class SimpleCog(commands.Cog, name='simple'):
    """SimpleCog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def numgen(self, ctx, number: int):
        if number > 25:
            await ctx.send("Too big...")
            return
        i = 0
        list = []
        while i < number:
            list.append(random.randint(0, 9))
            i += 1

        numlist = "".join(str(list)).strip("[]")
        await ctx.send(numlist)

def setup(bot):
    bot.add_cog(SimpleCog(bot))
