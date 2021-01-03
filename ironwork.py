import asyncio
from datetime import datetime

import discord
from discord.ext import commands


class IronWorks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='commission')
    async def commission(self, ctx, *args):
        wish = ' '.join(args)

        if not ctx.channel.id == 786758347818008626:
            return

        if len(wish) == 0:
            empty_wish_embed = discord.Embed(title="Cid needs you to format your request properly!",
                                             description="Please include what your request is with your command. i.e. "
                                                         ";wish Titanbronze Star Globe")
            empty_wish_embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/532380077896237061/786762838789849139/Cid_ARR.jpg")
            await ctx.channel.send(embed=empty_wish_embed)
            return

        wish = ' '.join(args)
        wish_embed = discord.Embed(title="{} has made a request!".format(ctx.message.author),
                                   description='{}'.format(wish), color=0xff0209)
        wish_embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/532380077896237061/786762838789849139/Cid_ARR.jpg")
        wish_embed.add_field(name="Created by:", value="{}".format(ctx.message.author.mention), inline=True)
        wish_embed.set_footer(
            text="Someone involved in the Ironworks production team will be in contact with you soon.")
        wish_embed.timestamp = datetime.utcnow()
        await ctx.channel.send(embed=wish_embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        user = await self.bot.fetch_user(message.author.id)
        if message.channel.id == 786758347818008626 and not user.bot:
            await discord.Message.delete(message)
        if message.channel.id == 786758347818008626 and user.bot:
            emoji = '\U0000274c'
            await discord.Message.add_reaction(message, emoji)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        user = await self.bot.fetch_user(payload.user_id)
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        embed = None
        if 786758347818008626 == message.channel.id:
            reaction = payload.emoji
            if message.embeds:
                embed = message.embeds[0].title

            if str(reaction) == '❌' and not user.bot:
                await discord.Message.delete(message)
            elif user.bot and str(embed) == 'Cid needs you to format your request properly!':
                await asyncio.sleep(5)
                await discord.Message.delete(message)


def setup(bot):
    bot.add_cog(IronWorks(bot))
