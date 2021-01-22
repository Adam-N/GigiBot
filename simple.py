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

    @commands.command(name='repeat', aliases=['copy', 'mimic'])
    async def do_repeat(self, ctx, *, our_input: str):
        """A simple command which repeats our input.
        In rewrite Context is automatically passed to our commands as the first argument after self."""

        await ctx.send(our_input)

    @commands.command(name='add', aliases=['plus'])
    @commands.guild_only()
    async def do_addition(self, ctx, first: int, second: int):
        """A simple command which does addition on two integer values."""

        total = first + second
        await ctx.send(f'The sum of **{first}** and **{second}**  is  **{total}**')

def setup(bot):
    bot.add_cog(SimpleCog(bot))
