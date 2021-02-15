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
        signature = f'*{ctx.prefix}{full_invoke}{short_invoke}   {command.signature}*'
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

    async def setup_help_page(self, ctx):
        pages = []
        for cog in self.bot.cogs:
            entry = ''
            cog = self.bot.get_cog(cog)
            filtered_commands = await self.return_filtered_commands(ctx, cog)
            if filtered_commands:
                entry += (
                    f'\n\n**=====[\t{cog.qualified_name} Commands\t]=====**\n\n'
                )
            for command in filtered_commands:
                description = command.short_doc or command.description
                signature = self.get_command_signature(command, ctx)
                entry += (
                    f'⏺ - [ **__{command.name}__** ]\n{signature}\n*```css\n  {description}```*\n'
                )
            pages.append(entry)
        await Pages(title=f'{self.bot.user.name}\'s Commands', color=0xCE2029, embed=True,
                    timeout=30, entries=pages, length=2, thumbnail=self.bot.user.avatar_url).start(ctx, 1)

    @commands.command(name='help', aliases=['h'], description='Custom Help Command')
    async def help(self, ctx):
        """Displays this command!"""
        await self.setup_help_page(ctx)
        await ctx.message.delete()

    def cog_unload(self):
        self.bot.help_command = self._original_help


def setup(bot):
    bot.add_cog(Help(bot))
