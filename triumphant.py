import discord
from discord.ext import commands


class TriumphantCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await self.bot.fetch_user(payload.user_id)
        emoji = payload.emoji
        embed_from_message = [message.embeds]

        print(embed_from_message)

        if str(user) != "Gigi Bot#0489" and str(emoji) == '👍':
            await message.add_reaction(emoji)
            channel_id = open("triumphant_channel.txt", "r").readline()

            posting_channel = await self.bot.fetch_channel(int(channel_id))
            await posting_channel.send(message)

    @commands.command(name='embed')
    async def embed(self, ctx):
        embed = discord.Embed(title='test', color=0x00ff00)
        embed.description = 'This is a test'
        await ctx.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(TriumphantCog(bot))
