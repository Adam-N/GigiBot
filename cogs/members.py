import discord
from discord.ext import commands
import datetime as dt


class MembersCog(commands.Cog, name='members'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def joined(self, ctx, *, member: discord.Member = None):
        """Says when a member joined."""
        if member is None:
            member = ctx.author
        await ctx.send(f'{member.display_name} joined on {member.joined_at}')

    @commands.command(name='top_role', aliases=['toprole'])
    @commands.guild_only()
    async def show_toprole(self, ctx, *, member: discord.Member = None):
        """Simple command which shows the members Top Role."""

        if member is None:
            member = ctx.author

        await ctx.send(f'The top role for {member.display_name} is {member.top_role.name}')

    @commands.command(name='perms', aliases=['perms_for', 'permissions'])
    @commands.guild_only()
    async def check_permissions(self, ctx, *, member: discord.Member = None):
        """A simple command which checks a members Guild Permissions.
        If member is not provided, the author will be checked."""

        if not member:
            member = ctx.author

        perms = '\n'.join(perm for perm, value in member.guild_permissions if value)

        embed = discord.Embed(title='Permissions for:', description=ctx.guild.name, colour=member.colour)
        embed.set_author(icon_url=member.avatar_url, name=str(member))

        embed.add_field(name='\uFEFF', value=perms)

        await ctx.send(content=None, embed=embed)

    @commands.command(hidden=True)
    async def check(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        embed = discord.Embed(title=f"{member.name}'s Profile", value="Check this out")

        embed.add_field(name="Joined at", value=f"{dt.datetime.strftime(member.joined_at, '%d %B, %Y  %H:%M')}")
        embed.add_field(name="Created at", value=f"{dt.datetime.strftime(member.created_at, '%d %B, %Y  %H:%M')}")
        embed.add_field(name="Username", value=f"{member.name}{member.discriminator}")
        embed.add_field(name="Top role:", value=f"{member.top_role}")
        embed.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def role_number(self, ctx, *role_name: str):
        i = 0
        role_name_joined = " ".join(role_name)
        role = discord.utils.get(ctx.message.guild.roles, name=role_name_joined)
        for member in role.members:
            i += 1
        embed = discord.Embed(title=f"{i} people in {role}", value=".")
        await ctx.send(embed=embed)

    @commands.command(name='ping')
    async def ping(self, ctx):
        """returns the bot's latency in milliseconds"""

        # return ping
        await ctx.send(f':ping_pong:⠀⠀**Pong!**⠀{round(self.bot.latency, 3)}ms')

def setup(bot):
    bot.add_cog(MembersCog(bot))
