import asyncio
import json
from datetime import datetime

import discord
from discord.ext import commands
from discord.utils import get


class WishWall(commands.Cog, name='Wishwall'):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def remove_reacts(message):
        try:
            for react in message.reactions:
                async for user in react.users():
                    if not user.bot:
                        await react.remove(user)
        finally:
            return

    @commands.command(name='wish')
    async def wish(self, ctx, platform: str = None, *args):
        """Use this in the WishWall channel to make a wish!"""
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        wish_channel = await self.bot.fetch_channel(int(config[str(ctx.message.guild.id)]['wishwall']))
        ps_emote = get(ctx.message.guild.emojis, name='ps4')
        xb_emote = get(ctx.message.guild.emojis, name='xbox')
        pc_emote = get(ctx.message.guild.emojis, name='pc')
        alias_list = {f'{ps_emote} Playstation': {'playstation', 'ps'},
                      f'{xb_emote} Xbox': {'xbox', 'xb'},
                      f'{pc_emote} PC': {'pc', 'steam'}}
        wish = ' '.join(args)
        platform = platform.lower()
        if platform is not None:
            for i in alias_list:
                if platform in alias_list[i]:
                    platform = i
                    break
            if platform not in alias_list.keys():
                platform = None
        if ctx.channel.id == wish_channel.id:
            if not platform:
                new_embed = discord.Embed(title="Error",
                                          description=f"*Please specify your platform.*\n"
                                          f"***{ctx.prefix}wish __<platform>__ <wish>***",
                                          color=0xff0209)
            elif len(wish) == 0:
                new_embed = discord.Embed(title="Error",
                                          description=f"*Please include a full description of you wish.*\n"
                                          f"***{ctx.prefix}wish <platform> __<wish>__***",
                                          color=0xff0209)
            else:
                if ctx.message.author.nick:
                    comm_author = str(ctx.message.author.nick)
                else:
                    comm_author = str(ctx.message.author)[:-5]
                new_embed = discord.Embed(title="__***{}***__ *has made a new wish!*".format(comm_author),
                                          description="{}".format(wish),
                                          color=0xff0209)
                new_embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/767568459939708950/800966534956318720/destiny_icon_grey.png")
                new_embed.add_field(name="**Platform:**",
                                    value=platform,
                                    inline=True)
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
        wish_channel = await self.bot.fetch_channel(int(config[str(message.guild.id)]['wishwall']))
        user = await self.bot.fetch_user(message.author.id)
        if message.channel.id == wish_channel.id:
            if user.bot and str(user.id) in config[str(message.guild.id)]['gigiid']:
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
            elif 'wish' in str(message.content[:6]):
                await discord.Message.delete(message)
        elif message.channel.id == wish_channel.id:
            await discord.Message.delete(message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        wish_channel = await self.bot.fetch_channel(int(config[str(payload.guild_id)]['wishwall']))
        channel = await self.bot.fetch_channel(payload.channel_id)
        member = channel.guild.get_member(payload.user_id)
        message = await channel.fetch_message(payload.message_id)
        try:
            old_embed = message.embeds[0]
        except IndexError:
            old_embed = discord.Embed()
        if old_embed.footer:
            comm_owner = old_embed.footer.text[12:]
        if channel.id == wish_channel.id and not member.bot:
            if payload.emoji.name == '✅':
                if not (member.name + '#' + member.discriminator) == comm_owner:
                    new_embed = discord.Embed(title=old_embed.title,
                                              description=old_embed.description,
                                              color=old_embed.color,
                                              timestamp=old_embed.timestamp)
                    new_embed.set_thumbnail(
                        url="https://cdn.discordapp.com/attachments/767568459939708950/800966534956318720/destiny_icon_grey.png")
                    new_embed.set_footer(text=old_embed.footer.text)
                    for i, field in enumerate(old_embed.fields):
                        for react in message.reactions:
                            async for user in react.users():
                                if str(react.emoji) == '✅' and not user.bot and not (
                                                                                            member.name + '#' + member.discriminator) == comm_owner:
                                    if field.name == '**Accepted by:**':
                                        if field.value == 'N/A':
                                            field.value = str(user.mention) + '\n'
                                        elif user.mention not in field.value:
                                            field.value = field.value + '\n' + str(user.mention)
                                        else:
                                            new_embed = discord.Embed(title="Error",
                                                                      description="*You already accepted this wish.*",
                                                                      color=0xff0209)
                                            await channel.send(embed=new_embed)
                                            await self.remove_reacts(message)
                                            return
                        new_embed.add_field(name=field.name,
                                            value=field.value,
                                            inline=True)
                    await message.edit(embed=new_embed)
                    await self.remove_reacts(message)
                    return
                else:
                    new_embed = discord.Embed(title="Error",
                                              description="*You cannot grant your own wish.*",
                                              color=0xff0209)
                    await channel.send(embed=new_embed)
                    await self.remove_reacts(message)
                    return
            elif payload.emoji.name == '❎':
                if str(member.name) in comm_owner:
                    await discord.Message.delete(message)
                else:
                    new_embed = discord.Embed(title=old_embed.title,
                                              description=old_embed.description,
                                              color=old_embed.color,
                                              timestamp=old_embed.timestamp)
                    new_embed.set_thumbnail(
                        url="https://cdn.discordapp.com/attachments/767568459939708950/800966534956318720/destiny_icon_grey.png")
                    new_embed.set_footer(text=old_embed.footer.text)
                    for i, field in enumerate(old_embed.fields):
                        if field.name == '**Accepted by:**':
                            field.value = field.value.replace(str(member.mention), '')
                            try:
                                field.value = field.value.replace('\n\n', '\n')
                            finally:
                                if field.value == '':
                                    field.value = 'N/A'
                        new_embed.add_field(name=field.name,
                                            value=field.value,
                                            inline=True)
                    await message.edit(embed=new_embed)
                    await self.remove_reacts(message)
                    return


def setup(bot):
    bot.add_cog(WishWall(bot))
