import json
import os

import discord
from discord.ext import commands


class OwnerCog(commands.Cog, name='owner'):

    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        """Command which Loads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        """Command which Unloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name="update", hidden=True, pass_context=True, aliases=['change', 'modify'])
    @commands.is_owner()
    async def update(self, ctx, setting: str, change: str):
        """changes a setting in the config file"""
        if os.path.isfile('assets/json/config.json'):
            with open('assets/json/config.json', 'r') as f:
                config = json.load(f)
        else:
            config = {}

        setting = setting.lower()

        if setting == 'prefix' or setting == "ironwork" or setting == 'wishwall' \
                or setting == 'gigiid' or setting == 'triumphant' or setting == 'birthday' \
                or setting == 'welcome' or setting == 'general' or setting == 'toptalker'\
                or setting == 'topthanks' or setting == 'topthanker' or setting == 'top5'\
                or setting == 'ringleader' or setting == 'mod' or setting == 'botpost' or setting == 'triumphrole':
            try:
                config[str(ctx.message.guild.id)][setting] = change
                await ctx.send(f'Change to {setting} made. It is now {change}')
            except KeyError:
                config[str(ctx.message.guild.id)] = {}
                config[str(ctx.message.guild.id)][setting] = change
                await ctx.send(f'Change to {setting} made. It is now {change}')

        elif setting == "bot_channel":
            try:

                config[str(ctx.message.guild.id)][setting].append(change)
            except KeyError:
                config[str(ctx.message.guild.id)][setting] = {}
                config[str(ctx.message.guild.id)][setting] = [change]

            await ctx.send(f'Added {change} to {setting} list')


        else:
            await ctx.send(f'Something went wrong. {setting} was not in the database.')

        with open('assets/json/config.json', 'w') as f:
            json.dump(config, f)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.bot.logout()

    @commands.command(hidden= True,aliases=['changesettings', 'change_settings'])
    @commands.is_owner()
    async def config(self, ctx, board:str, setting: str, value: str):
        if os.path.isfile('assets/json/config.json'):
            with open('assets/json/config.json', 'r') as f:
                config = json.load(f)
        else:
            config = {}
        setting = setting.lower()
        board = board.lower()

        if board != 'starboard' and board != 'wishwall' and board != 'ironworks':
            ctx.send('First argument should be starboard, wishwall or ironworks')
            return

        if setting in ["star_emoji", "count", "conf_emoji"] and board != 'starboard':
            ctx.send(f'{setting} is only available in starboard. It was used with {board}')
            return

        if setting in ["un-accept_emoji", "accept_emoji"] and board not in ['wishwall', 'ironworks']:
            ctx.send(f'{setting} is only available in wishwall or starboard. It was used with {board}')
            return

        try:
            config[str(ctx.message.guild.id)][board][setting] = value
        except KeyError:
            ctx.send(f'Appears something went wrong. Did you create {board} first?')

        with open('assets/json/config.json', 'w') as f:
            json.dump(config, f)
        await ctx.send(f'Completed. {setting} is now {value}')


    @commands.command(name="create", hidden=True, pass_context=True, aliases=['new', 'make', 'bind'])
    @commands.is_owner()
    async def create(self, ctx,board: str, channel: discord.TextChannel):
        """creates a starboard for this guild"""
        board = board.lower()

        if board != 'starboard' and board != 'wishwall' and board != 'ironworks':
            ctx.send('First argument should be starboard, wishwall or ironworks')
            return

        if not os.path.isfile('assets/json/config.json'):
            # if the file doesn't exist, it gives default values to all of the settings.
            if board == 'starboard':
                config = {}
                config[str(ctx.message.guild.id)] = {}
                config[str(ctx.message.guild.id)][board] = {}
                config[str(ctx.message.guild.id)][board]['channel'] = channel.id
                config[str(ctx.message.guild.id)][board]["star_emoji"] = "\u2b50"
                config[str(ctx.message.guild.id)][board]["count"] = 3
                config[str(ctx.message.guild.id)][board]["conf_emoji"] = "\u2705"

            elif board == 'wishwall' or board == 'ironworks':
                config = {}
                config[str(ctx.message.guild.id)] = {}
                config[str(ctx.message.guild.id)][board] = {}
                config[str(ctx.message.guild.id)][board]['channel'] = channel.id
                config[str(ctx.message.guild.id)][board]["accept_emoji"] = "\u2705"
                config[str(ctx.message.guild.id)][board]["un-accept_emoji"] = "\u274E"

            with open('assets/json/config.json', 'w') as f:
                json.dump(config, f)

        elif os.path.isfile('assets/json/config.json'):
            with open('assets/json/config.json', 'r') as f:
                config = json.load(f)
            try:
                if config[str(ctx.message.guild.id)][board]:
                    await ctx.send(f"{board} AlreadyExists")
                    return
            except KeyError:
                if board == "starboard":
                    config[str(ctx.message.guild.id)][board] = {}
                    config[str(ctx.message.guild.id)][board]['channel'] = channel.id
                    config[str(ctx.message.guild.id)][board]["star_emoji"] = "\u2b50"
                    config[str(ctx.message.guild.id)][board]["count"] = 3
                    config[str(ctx.message.guild.id)][board]["conf_emoji"] = "\u2705"

                elif board == 'wishwall' or board == 'ironworks':
                    config[str(ctx.message.guild.id)][board] = {}
                    config[str(ctx.message.guild.id)][board]['channel'] = channel.id
                    config[str(ctx.message.guild.id)][board]["accept_emoji"] = "\u2705"
                    config[str(ctx.message.guild.id)][board]["un-accept_emoji"] = "\u274E"

            with open('assets/json/config.json', "w") as f:
                json.dump(config, f)

        else:
            await ctx.send("Something went wrong, starboard could not be created")

        await ctx.send(f"{board} Created")

def setup(bot):
    bot.add_cog(OwnerCog(bot))

