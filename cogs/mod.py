import asyncio
import json

import discord
from discord.ext import commands


class ModCog(commands.Cog, name='mods'):
    """Contains Message Retaining Info"""

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        channel = self.bot.get_channel(int(config[str(payload.guild_id)]['modpost']))
        if not payload.cached_message:
            deleted_channel = self.bot.get_channel(payload.channel_id)
            message_id = payload.message_id

            embed = discord.Embed(title='Message Deleted', description='Was not in internal cache. Cannot fetch '
                                                                       'context.')
            embed.add_field(name='Deleted in:',value=deleted_channel.mention)
            embed.add_field(name='Message ID',value=message_id)

            await channel.send(embed=embed)
        elif payload.cached_message:
            message = payload.cached_message
            embed = discord.Embed(title='Message Deleted')
            embed.add_field(name='Message Author:', value=message.author.mention)
            embed.add_field(name='Channel:', value=message.channel.mention)
            embed.add_field(name='Message Content:', value=message.content)
            embed.set_footer(text=f'Author ID: {message.author.id} | Message ID: {message.id}')
            embed.set_thumbnail(url=message.author.avatar_url)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_message_edit(self,payload):
        edited_channel = self.bot.get_channel(payload.channel_id)
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        channel = self.bot.get_channel(int(config[str(edited_channel.guild.id)]['modpost']))
        edited_channel = self.bot.get_channel(payload.channel_id)
        edited_message = await edited_channel.fetch_message(payload.message_id)
        if edited_message.author.bot:
            return
        data = payload.data
        if not payload.cached_message:
            embed = discord.Embed(title='Message Edited. **Not in Internal Cache.**', description=f'[Jump to message]({edited_message.jump_url})')
            embed.add_field(name='Channel:', value=edited_channel.mention)
            embed.add_field(name='Message Author', value=edited_message.author.mention)
            embed.add_field(name='Edited Message',value=data['content'])
            await channel.send(embed=embed)
        if payload.cached_message:
            embed = discord.Embed(title='Message Edited', description=f'[Jump to message]({edited_message.jump_url})')
            embed.add_field(name='Channel:', value=edited_channel.mention)
            embed.add_field(name='User:', value=edited_message.author.mention)
            embed.add_field(name='Message Before:', value=payload.cached_message.content)
            embed.add_field(name='Message After:', value=data['content'])
            embed.set_footer(text=f'User ID: {edited_message.author.id}')
            embed.set_thumbnail(url=edited_message.author.avatar_url)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        channel = self.bot.get_channel(int(config[str(before.guild.id)]['rolepost']))
        if before.roles == after.roles:
            return
        embed = discord.Embed(title=f'{before.name}#{before.discriminator}')
        embed.add_field(name='User:', value=after.mention)
        if set(before.roles) != set(after.roles):
            if len(before.roles) > len(after.roles):
                for role in before.roles:
                    if role not in after.roles:
                        embed.add_field(name='Role change:', value=f'{role.name} removed')
            elif len(before.roles) < len(after.roles):
                for role in after.roles:
                    if role not in before.roles:
                        embed.add_field(name='Role change:', value=f'{role.name} added')
        embed.set_footer(text=f'User ID:{after.id}', icon_url=after.avatar_url)
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(ModCog(bot))
