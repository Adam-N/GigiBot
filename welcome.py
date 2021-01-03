import random
import discord
from discord.ext import commands
import datetime


class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = await self.bot.fetch_channel(channel_id=334925467431862272)
        ment = member.mention
        welcome_messages = [
            f"\U0001f4e2 \U0000269f Say hello to {ment}!",
            f"\U0001f4e2 \U0000269f Hello there! ~~General Kenobi~~ {ment}!!",
            f"\U0001f4e2 \U0000269f A wild {ment} appeared.",
            f"\U0001f4e2 \U0000269f Everyone welcome, {ment}",
            f"\U0001f4e2 \U0000269f Welcome, {ment}! We hope you brought pizza.",
            f"\U0001f4e2 \U0000269f Brace yourselves. {ment} is here!",
            f"\U0001f4e2 \U0000269f {ment} is here, as the prophecy foretold.",
            f"\U0001f4e2 \U0000269f Hey! Listen! {ment} has joined!",
            f"\U0001f4e2 \U0000269f {ment} is near.",
            f"\U0001f4e2 \U0000269f {ment} joined your party.",
            f"\U0001f4e2 \U0000269f {ment} is breaching the wall on the north side. Give them all you got!",
            f"\U0001f4e2 \U0000269f Welcome ~~Tenno~~ {ment}!"
        ]
        await channel.send(random.choice(welcome_messages))

        welcome_embed = discord.Embed(title="Member joined", description=f'{member} has joined.')
        welcome_embed.add_field(name="ID:", value=f"{member.id}", inline=True)
        created = member.created_at.strftime("%b %d, %Y")
        welcome_embed.add_field(name="Created on:", value=f"{created}", inline=True)
        welcome_embed.set_thumbnail(url=member.avatar_url)
        welcome_embed.timestamp = datetime.datetime.utcnow()

        bot_role = member.guild.get_role(511306250479337476)
        number = len(bot_role.members)
        total = member.guild.member_count
        welcome_embed.add_field(name="Join number: ", value=f"{total - number}", inline=True)

        await channel.send(embed=welcome_embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = await self.bot.fetch_channel(channel_id=334925467431862272)

        leave_embed = discord.Embed(title="Member left", description=f'{member} has left')
        leave_embed.add_field(name="Nick: ", value=f"{member.nick}", inline=True)
        leave_embed.add_field(name="ID:", value=f"{member.id}", inline=True)

        joined = member.joined_at.strftime("%b %d, %Y")
        leave_embed.add_field(name="Joined on:", value=f"{joined}")

        mentions = [role.mention for role in member.roles if role.name != '@everyone']
        leave_embed.add_field(name="Roles:", value=" ".join(mentions))

        leave_embed.set_thumbnail(url=member.avatar_url)
        leave_embed.timestamp = datetime.datetime.utcnow()

        await channel.send(embed=leave_embed)


def setup(bot):
    bot.add_cog(WelcomeCog(bot))
