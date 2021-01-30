import asyncio
import json
from datetime import datetime

import discord
from discord.ext import commands


class IronWorks(commands.Cog, name='Ironworks'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='commission')
    async def commission(self, ctx, *args):
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        commission = ' '.join(args)
        if str(ctx.channel.id) == config[str(ctx.guild.id)]['ironwork']:
            if len(commission) == 0:
                new_embed = discord.Embed(title="Error",
                                          description=f"*Please include a full description of your request.*\n"
                                                      f"***{ctx.prefix}commission <commission>***",
                                          color=0xff0209)
            else:
                if ctx.message.author.nick:
                    comm_author = str(ctx.message.author.nick)
                else:
                    comm_author = str(ctx.message.author)[:-5]
                new_embed = discord.Embed(title="__**{}**__ *has made a new commission!*".format(comm_author),
                                          description="{}".format(commission),
                                          color=0xff0209)
                new_embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/532380077896237061/786762838789849139/Cid_ARR.jpg")
                new_embed.add_field(name="**Accepted by:**",
                                    value="N/A",
                                    inline=True)
                new_embed.set_footer(text="Created by: {}".format(ctx.message.author))
                new_embed.timestamp = datetime.utcnow()
            await ctx.channel.send(embed=new_embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        user = await self.bot.fetch_user(message.author.id)
        if str(message.channel.id) in config[str(message.guild.id)]['ironwork']:
            if str(user.id) in config[str(message.guild.id)]['gigiid']:
                try:
                    if 'Error' in str(message.embeds[0].title):
                        await asyncio.sleep(3)
                        await discord.Message.delete(message)
                    else:
                        reactions = ['\U00002705', '\U0000274E']
                        for emoji in reactions:
                            await discord.Message.add_reaction(message, emoji)
                except Exception:
                    pass
            elif 'commission' in str(message.content[:12]):
                await discord.Message.delete(message)
        elif str(message.channel.id) == config[str(message.guild.id)]['ironwork']:
            await discord.Message.delete(message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        channel = await self.bot.fetch_channel(payload.channel_id)
        member = channel.guild.get_member(payload.user_id)
        message = await channel.fetch_message(payload.message_id)
        iron_channel = await self.bot.fetch_channel(int(config[str(payload.guild_id)]['ironwork']))

        try:
            old_embed = message.embeds[0]
        except IndexError:
            old_embed = discord.Embed()
        if old_embed.footer:
            comm_owner = old_embed.footer.text[12:]
        if str(channel.id) in config[str(payload.guild_id)]['ironwork'] and not member.bot:
            if payload.emoji.name == '✅':
                if not (member.name + '#' + member.discriminator) == comm_owner:
                    for i, field in enumerate(old_embed.fields):
                        new_embed = discord.Embed(title=old_embed.title,
                                                  description=old_embed.description,
                                                  color=old_embed.color,
                                                  timestamp=old_embed.timestamp)
                        new_embed.set_thumbnail(
                            url="https://cdn.discordapp.com/attachments/532380077896237061/786762838789849139/Cid_ARR.jpg")
                        new_embed.set_footer(text=old_embed.footer.text)
                        for react in message.reactions:
                            async for user in react.users():
                                if react.emoji == '✅' and not user.bot:
                                    if field.value == 'N/A':
                                        field.value = str(user.mention) + '\n'
                                    elif user.mention not in field.value:
                                        field.value = field.value + '\n' + str(user.mention)
                                    else:
                                        new_embed = discord.Embed(title="Error",
                                                                  description="*You already accepted this commission.*",
                                                                  color=0xff0209)
                                        await channel.send(embed=new_embed)
                        new_embed.add_field(name=field.name,
                                            value=field.value,
                                            inline=True)
                    await message.edit(embed=new_embed)
                else:
                    new_embed = discord.Embed(title="Error",
                                              description="*You cannot accept your own commission.*",
                                              color=0xff0209)
                    await channel.send(embed=new_embed)
            elif payload.emoji.name == '❎':
                if str(member.name) in comm_owner:
                    await discord.Message.delete(message)
                else:
                    if member.permissions_in(iron_channel).manage_messages and not member.bot:
                        await discord.Message.delete(message)
                        return

                    for i, field in enumerate(old_embed.fields):
                        new_embed = discord.Embed(title=old_embed.title,
                                                  description=old_embed.description,
                                                  color=old_embed.color,
                                                  timestamp=old_embed.timestamp)
                        field.value = field.value.replace(str(member.mention), '')
                        try:
                            field.value = field.value.replace('\n\n', '\n')
                        finally:
                            if field.value == '':
                                field.value = 'N/A'
                            new_embed.add_field(name=field.name,
                                                value=field.value,
                                                inline=True)
                            new_embed.set_thumbnail(
                                url="https://cdn.discordapp.com/attachments/532380077896237061/786762838789849139/Cid_ARR.jpg")
                            new_embed.set_footer(text=old_embed.footer.text)
                            await message.edit(embed=new_embed)
        try:
            for react in message.reactions:
                async for user in react.users():
                    if not user.bot:
                        await react.remove(user)
        finally:
            return


def setup(bot):
    bot.add_cog(IronWorks(bot))
