import asyncio
import json
from datetime import datetime

import discord
from discord.ext import commands
from discord.utils import get


class WishWall(commands.Cog, name='WishWall'):
    def __init__(self, bot):
        self.bot = bot
        self.url = 'https://cdn.discordapp.com/attachments/767568459939708950/800966534956318720/destiny_icon_grey.png'
        self.prefix: str = ''

    @staticmethod
    async def build_embed(self, old_embed: discord.Embed = None,
                          author: str = None, platform: str = None, description: str = None,
                          add: discord.Member = None, remove: discord.Member = None,
                          error: bool = False, error_type: int = 0):
        if not error:
            if old_embed:
                new_embed = discord.Embed(title=old_embed.title,
                                          description=old_embed.description,
                                          color=old_embed.color)
                new_embed.add_field(name=old_embed.fields[0].name,
                                    value=old_embed.fields[0].value,
                                    inline=True)
                new_embed.set_thumbnail(url=self.url)
                new_embed.set_footer(text=old_embed.footer.text)
                new_embed.timestamp = old_embed.timestamp
                if add:
                    user_list = old_embed.fields[1].value
                    if add.mention not in user_list:
                        user_list = user_list.replace('N/A', '')
                        user_list += '\n' + str(add.mention)
                elif remove:
                    user_list = old_embed.fields[1].value
                    if remove.mention in user_list:
                        user_list = user_list.replace(remove.mention, '')
                        if len(user_list) == 0:
                            user_list = 'N/A'
                new_embed.add_field(name=old_embed.fields[1].name,
                                    value=user_list,
                                    inline=True)
            if author and platform and description:
                new_embed = discord.Embed(title=f'{author} has made a new wish!',
                                          description=f'\"{description}\"',
                                          color=0xff0209)
                new_embed.add_field(name='**Platform:**',
                                    value=f'{platform}',
                                    inline=True)
                new_embed.add_field(name='**Accepted by:**',
                                    value='N/A',
                                    inline=True)
                new_embed.set_thumbnail(url=self.url)
                new_embed.set_footer(text=f'Created by: {author}')
                new_embed.timestamp = datetime.utcnow()
        else:
            new_embed = discord.Embed(title=f'**Error**',
                                      color=0xff0209)
            if error_type == 1:
                new_embed.description = (f'*Configuration for WishWall is improperly formatted/*\n' +
                                         f'*missing from file. Please contact staff for assistance.*')
            elif error_type == 2:
                new_embed.description = (f'*Missing argument. Please properly format your wish.*\n' +
                                         f'***{self.prefix}wish <__platform__> <description>***')
            elif error_type == 3:
                new_embed.description = (f'*Missing argument. Please properly format your wish.*\n' +
                                         f'***{self.prefix}wish <platform> <__description__>***')
            else:
                new_embed.description = (f'*An unspecified error has occured while executing command.*\n' +
                                         f'*Please contact staff for assistance.*')
        return new_embed

    @staticmethod
    async def build_embed_reacts(self, message, config):
        if message.reactions:
            for react in message.reactions:
                async for user in react.users():
                    if not user == self.bot.user:
                        await react.remove(user)
        else:
            await discord.Message.add_reaction(message, config['accept_emoji'])
            await discord.Message.add_reaction(message, config['un-accept_emoji'])

    @commands.command(name='wish')
    async def wish(self, ctx, platform: str = None, *args):
        """Use this in the WishWall channel to make a wish!"""
        self.prefix = ctx.prefix
        guild = ctx.guild.id
        channel = await self.bot.fetch_channel(ctx.channel.id)
        author = ctx.message.author
        ps_emote = get(ctx.message.guild.emojis, name='ps4')
        xb_emote = get(ctx.message.guild.emojis, name='xbox')
        pc_emote = get(ctx.message.guild.emojis, name='pc')
        alias_list = {f'{ps_emote} Playstation': {'playstation', 'ps'},
                      f'{xb_emote} Xbox': {'xbox', 'xb'},
                      f'{pc_emote} Steam': {'pc', 'steam'}}
        if platform:
            for alias in alias_list:
                if platform.lower() in alias_list[alias]:
                    platform = alias
                    break
            if platform not in alias_list.keys():
                platform = None
        wish_desc = ' '.join(args)
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        try:
            config = config[str(guild)]['wishwall']
        except KeyError:
            sent = await channel.send(embed=(await self.build_embed(self, error=True, error_type=1)))
            await asyncio.sleep(5)
            print('Deleted Here <-----')
            await sent.delete()
            return
        if channel.id == config['channel']:
            if author.nick:
                wish_owner = str(author.nick)
            else:
                wish_owner = str(author)[:-5]
            if not platform:
                sent = await channel.send(embed=(await self.build_embed(self, error=True, error_type=2)))
                await asyncio.sleep(5)
                print('Deleted Here <-----')
                await sent.delete()
            elif len(wish_desc) == 0:
                sent = await channel.send(embed=(await self.build_embed(self, error=True, error_type=3)))
                await asyncio.sleep(5)
                print('Deleted Here <-----')
                await sent.delete()
            else:
                await channel.send(
                    embed=(await self.build_embed(self, author=wish_owner, platform=platform, description=wish_desc)))

    @commands.Cog.listener()
    async def on_message(self, ctx):
        guild = ctx.guild.id
        channel = await self.bot.fetch_channel(ctx.channel.id)
        message = ctx
        author = message.author
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        try:
            config = config[str(guild)]['wishwall']
        except KeyError:
            sent = await channel.send(embed=(await self.build_embed(self, error=True, error_type=1)))
            await asyncio.sleep(5)
            print('Deleted Here <-----')
            await sent.delete()
            return
        if channel.id == config['channel']:
            if author == self.bot.user:
                await self.build_embed_reacts(self, message, config)
            elif author != self.bot.user:
                print('===============[ author != self.bot.user ]===============')
                print('author = ' + str(author))
                print('self.bot.user = ' + str(self.bot.user))
                print('===============[ Message Deleted ]===============')
                await discord.Message.delete(message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, ctx):
        payload = ctx
        guild = payload.guild_id
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = await channel.guild.fetch_member(payload.user_id)
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        try:
            config = config[str(guild)]['wishwall']
        except KeyError:
            sent = await channel.send(embed=(await self.build_embed(self, error=True, error_type=1)))
            await asyncio.sleep(5)
            print('Deleted Here <-----')
            await sent.delete()
            return
        if channel.id == config['channel'] and message.author == self.bot.user and not member == self.bot.user and \
                message.embeds[0]:
            if member.name not in message.embeds[0].footer.text:
                if str(payload.emoji) == config['accept_emoji']:
                    await message.edit(embed=(await self.build_embed(self, old_embed=message.embeds[0], add=member)))
                elif str(payload.emoji) == config['un-accept_emoji']:
                    await message.edit(embed=(await self.build_embed(self, old_embed=message.embeds[0], remove=member)))
            elif member.name in message.embeds[0].footer.text:
                if str(payload.emoji) == config['un-accept_emoji']:
                    print('===============[ member.name & payload.emoji ]===============')
                    print('member.name = ' + str(member.name))
                    print('message.embeds[0].footer.text = ' + str(message.embeds[0].footer.text))
                    print('payload.emoji = ' + str(payload.emoji))
                    print('config[\'un-accept_emoji\'] = ' + str(config['un-accept_emoji']))
                    print('===============[ Message Deleted ]===============')
                    await discord.Message.delete(message)
                    return
            await self.build_embed_reacts(self, message, config)


def setup(bot):
    bot.add_cog(WishWall(bot))
