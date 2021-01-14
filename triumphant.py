import json
import os
import random
import discord
from discord.ext import commands, tasks


class TriumphantCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.member.bot:
            users = {}
            guild = self.bot.get_guild(payload.guild_id)
            channel = await self.bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            emoji = payload.emoji
            copy_embed = ""
            msg = await message.guild.get_channel(channel_id=payload.channel_id).fetch_message(payload.message_id)

            if emoji.name == '🏆':
                await message.add_reaction(emoji)
                channel_id = open("triumphant_channel.txt", "r").readline()

                posting_channel = await self.bot.fetch_channel(int(channel_id))
                if message.embeds:

                    for member in guild.members:
                        if str(member.name) in message.embeds[0].description:
                            not_bot_user = member.id
                            users[str(member.id)] = 1
                            break
                        else:
                            continue
                    # if so, copy it into a dict so we can work with it
                    copy_embed = message.embeds[0].to_dict()

                    # let's start with the embed's description
                    if message.content:
                        # if the message has both content and an embed, then we'll need to copy both
                        try:
                            content = message.content.__add__(f'\n\n**Link Preview:**\n{copy_embed["description"]}')
                        except KeyError:
                            try:
                                content = message.content.__add__(f'\n\n**Link Preview:**\n{copy_embed["title"]}')
                            except KeyError:
                                pass
                            pass
                    else:
                        # otherwise we'll just copy the description
                        try:
                            content = copy_embed["description"]
                        except KeyError:
                            content = copy_embed["title"]

                    # then append any fields it has on the bottom, not elegant for inlines but deal
                    if "fields" in copy_embed:
                        for embeds in message.embeds:
                            for field in embeds.fields:
                                content = content.__add__(f'\n\n**{field.name}**')
                                content = content.__add__(f'\n{field.value}')

                else:
                    # if not, we'll just use the message's content
                    content = message.content

                # create the embed to send to the starboard
                embed = discord.Embed(title=f"{message.author} said...",
                                      description=f'{content}\n\n[Jump to Message](https://discordapp.com/channels/{payload.guild_id}/{payload.channel_id}/{payload.message_id})',
                                      colour=0x784fd7,
                                      timestamp=message.created_at)
                if not msg.author.bot:
                    embed.set_footer(text=f"ID:{msg.author.id}")
                    embed.set_thumbnail(url=msg.author.avatar_url)
                    embed.add_field(name="Nominated User:", value=f"{msg.author.name}")

                if msg.author.bot:
                    embed.set_footer(text=f"ID:{not_bot_user}")
                    avatar_member = self.bot.get_user(not_bot_user)
                    embed.set_thumbnail(url=avatar_member.avatar_url)
                    embed.add_field(name="Nominated User:", value=f"{avatar_member.name}")

                # add the author's avatar as the thumbnail

                # add attached image or link preview if there is one
                if message.embeds:
                    if "image" in copy_embed:
                        embed.set_image(url=copy_embed["image"]["url"])
                    elif "video" in copy_embed:
                        embed.set_image(url=copy_embed["thumbnail"]["url"])
                elif message.attachments:
                    embed.set_image(url=message.attachments[0].url)

                embed.add_field(name='Nominated by:', value=f'{payload.member.name}')
                await posting_channel.send(embed=embed)

                if os.path.isfile('triumphant.json'):
                    with open('triumphant.json', 'r') as f:
                        users = json.load(f)

                if not msg.author.bot:
                    users[str(msg.author.id)] = 1

                if msg.author.bot:
                    users[str(not_bot_user)] = 1

                with open('triumphant.json', 'w') as f:
                    json.dump(users, f)

    @commands.command()
    @commands.is_owner()
    async def triumph_delete(self, ctx, member_id: int):
        member = await ctx.guild.fetch_member(member_id=member_id)
        with open('triumphant.json', 'r') as f:
            users = json.load(f)
        try:
            if users[str(member_id)] == 1:
                del users[str(member_id)]
        except:
            del_embed = discord.Embed(title='User was not in the list')
            del_embed.add_field(name="User:", value=f"{member.name}")
            del_embed.add_field(name="User Id:", value=f"{member_id}")
            await ctx.send(embed=del_embed)
            return
        with open('triumphant.json', 'w+') as f:
            json.dump(users, f)
        await ctx.send(f"Succesfully deleted {member.name} from triumphant list. ID: {member_id}")

    @commands.command()
    @commands.is_owner()
    async def triumph_add(self, ctx, member_id: int):
        member = await ctx.guild.fetch_member(member_id=member_id)
        with open('triumphant.json', 'r') as f:
            users = json.load(f)

        try:
            if users[str(member_id)]:
                add_embed = discord.Embed(title='User was already triumphant')
                add_embed.add_field(name="User:", value=f"{member.name}")
                add_embed.add_field(name="User Id:", value=f"{member_id}")
                await ctx.send(embed=add_embed)
                return
        except:
            users[str(member_id)] = 1

        with open('triumphant.json', 'w') as f:
            json.dump(users, f)

        add_embed = discord.Embed(title='User is now triumphant')
        add_embed.add_field(name="User:", value=f"{member.name}")
        add_embed.add_field(name="User Id:", value=f"{member_id}")
        await ctx.send(embed=add_embed)

    @commands.command()
    @commands.is_owner()
    async def triumph_list(self, ctx):
        id_list = ''
        user_list = ''
        with open('triumphant.json', 'r') as f:
            users = json.load(f)

        for key in users:
            member = await ctx.guild.fetch_member(member_id=int(key))
            user_list = user_list + str(member.name) + " \n"
            id_list = id_list + key + " \n"

        list_embed = discord.Embed(title='Members on the triumphant list')
        list_embed.add_field(name='List:', value=f"{user_list}")
        list_embed.add_field(name="IDs:", value=f"{id_list}")
        await ctx.send(embed=list_embed)

    @commands.command()
    @commands.is_owner()
    async def give_triumphant(self, ctx):
        triumphant_role = discord.utils.get(ctx.author.guild.roles, name="Triumphant/Reward")
        current_triumphant = list(triumphant_role.members)
        member_list = ""

        with open('triumphant_copy.json', 'r') as f:
            users = json.load(f)

        for member in current_triumphant:
            await member.remove_roles(triumphant_role)

        for key in users:
            user = ctx.channel.guild.get_member(user_id=int(key))
            member_list = member_list + user.name + '\n'
            await user.add_roles(triumphant_role)

        os.remove('triumphant_copy.json')

        triumph_embed = discord.Embed(title="Triumphant Role Success",
                                      description="These users have received their role.")
        triumph_embed.add_field(name="Users:", value=f"{member_list}")
        await ctx.send(embed=triumph_embed)

    @commands.command()
    @commands.is_owner()
    async def embed(self, ctx):
        # This command is for testing purposes only!
        member = random.choice(ctx.guild.members)
        if member.bot:
            while member.bot:
                member = random.choice(ctx.guild.members)
        embed = discord.Embed(title="title",
                              description=f'rnamdnoidfdsafoida{member.name}jfasd ldsfjlkdsajdfsjkljlksafjkfdsjkl')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def start_timer(self, ctx):
        self.triumphant_timer.start()

    @tasks.loop(minutes=10)
    async def triumphant_timer(self):
        chan = self.bot.get_channel(742389034420142090)
        await chan.send("\U0001f5d3 Timer Started \U0001f5d3")

        print(1)
        if os.path.isfile('triumphant_copy.json'):
            os.remove('triumphant_copy.json')
        with open('triumphant.json', 'r') as f:
            users = json.load(f)

        with open('triumphant_copy.json', 'w+') as f:
            users = json.dump(users, f)

        os.remove('triumphant.json')

        reset_embed = discord.Embed(title="\U0001f5d3| New Week Starts Here. Get that bread!")
        chan = self.bot.get_channel(742389034420142090)
        await chan.send(embed=reset_embed)


def setup(bot):
    bot.add_cog(TriumphantCog(bot))
