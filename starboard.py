import discord
from discord.ext import commands


class StarboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reaction = payload.emoji
        user = await self.bot.fetch_user(payload.user_id)
        starboard_embed = discord.Embed

        if str(reaction) == '👍' and str(user) != "Gigi Bot#0489":
            await message.add_reaction(reaction)
            channel_id = open("triumphant_channel.txt", "r").readline()
            posting_channel = await self.bot.fetch_channel(int(channel_id))

            starboard_embed.title = "{} in {}".format(user, channel)
            starboard_embed.description = "{}".format(message.content)
            await posting_channel.send(embed=starboard_embed)

    @commands.command(name='embed')
    async def embed(self, ctx):
        embed = discord.Embed(color=0x00ff00)
        embed.title = 'Test'
        embed.description = 'This is a test'
        await ctx.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(StarboardCog(bot))
