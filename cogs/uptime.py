import datetime
from time import time

import discord
from discord.ext import commands


class UptimeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    start_time = time()

    @commands.command(pass_context=True)
    async def uptime(self, ctx):
        """Shows the uptime for the bot."""
        current_time = time()
        difference = int(round(current_time - self.start_time))
        time_converted = datetime.timedelta(seconds=difference)
        hours, remainder = divmod(time_converted.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        embed = discord.Embed()
        embed.add_field(name="Uptime", value='{} hours, {} minutes, {} seconds'.format(hours, minutes, seconds),
                        inline=True)

        embed.set_thumbnail(url='https://media.discordapp.net/attachments/742389103890268281/746419792000319580'
                                '/shiinabat_by_erickiwi_de3oa60-pre.png?width=653&height=672')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(UptimeCog(bot))