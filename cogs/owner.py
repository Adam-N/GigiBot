import json
import os

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
    @commands.has_guild_permissions(administrator=True)
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
                or setting == 'welcome' or setting == 'general':
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

def setup(bot):
    bot.add_cog(OwnerCog(bot))

