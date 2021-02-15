import asyncio
import discord
from discord.ext import commands
from discord.ext.buttons import Paginator


class Pages(Paginator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Help(commands.Cog, name='Help'):
    def __init__(self, bot):
        self.bot = bot
        self._original_help = self.bot.help_command
        self.bot.help_command = None

    @classmethod
    def get_command_signature(self, command: commands.Command, ctx: commands.Context):
        aliases = '|'.join(command.aliases)
        short_invoke = f'[{command.name}|{aliases}]' if command.aliases else f'[{command.name}]'
        full_invoke = command.qualified_name.replace(command.name, "")
        signature = f'{ctx.prefix}{full_invoke}{short_invoke} {command.signature}'
        return signature

    @classmethod
    async def return_filtered_commands(self, ctx, query):
        filtered = []
        for command in query.walk_commands():
            try:
                if command.hidden or command.parent:
                    continue
                await command.can_run(ctx)
                filtered.append(command)
            except commands.CommandError:
                continue
        return sorted(filtered, key=lambda x: x.name)

    async def setup_help_page(self, ctx, command: commands.Command = None):
        if command:
            command_title = f'{self.bot.user.name}\'s __{command.qualified_name}__ Command'
            command_sig = self.get_command_signature(command, ctx)
            command_desc = f'**Usage:** *`{command_sig}`*\n```css\n{command.short_doc}```'
            new_embed = discord.Embed(title=command_title, description=command_desc, color=0xCE2029)
            new_embed.set_thumbnail(url=self.bot.user.avatar_url)
            sent = await ctx.send(embed=new_embed)
            await asyncio.sleep(8)
            await sent.delete()
        else:
            pages = []
            for cog in self.bot.cogs:
                entry = ''
                cog = self.bot.get_cog(cog)
                cog_commands = await self.return_filtered_commands(ctx, cog)
                if cog_commands:
                    entry += f'\n\n**=====[\t{cog.qualified_name} Commands\t]=====**\n\n'
                    for command in cog_commands:
                        command_desc = command.description or command.short_doc
                        command_sig = self.get_command_signature(command, ctx)
                        entry += f'⏺ - [ **__{command.name}__** ]\n y*Usage:  `{command_sig}`*\n*```css\n  {command_desc}```*\n'
                    pages.append(entry)
            await Pages(title=f'{self.bot.user.name}\'s Commands', color=0xCE2029, embed=True,
                        timeout=25, entries=pages, length=1, thumbnail=self.bot.user.avatar_url).start(ctx, 1)

    @commands.command(name='help', aliases=['h'], description='Custom Help Command')
    async def help(self, ctx, query=None):
        """Displays this command!"""
        await ctx.message.delete()
        if query:
            try:
                command = self.bot.get_command(query)
                await self.setup_help_page(ctx, command)
            except commands.CommandNotFound:
                error = await ctx.send(embed=discord.Embed(title='Command not found'))
                await asyncio.sleep(3)
                await error.delete()
        else:
            await self.setup_help_page(ctx)

    def cog_unload(self):
        self.bot.help_command = self._original_help


def setup(bot):
    bot.add_cog(Help(bot))
