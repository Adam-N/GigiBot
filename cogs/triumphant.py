import json
import os
import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions


class TriumphantCog(commands.Cog, name='Triumphant'):
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
            posted = False
            copy_embed = ""
            not_bot_user = None
            msg = await message.guild.get_channel(channel_id=payload.channel_id).fetch_message(payload.message_id)
            id_list = []
            name_list = []
            with open(f'assets/json/server/{guild.id}/profiles.json', 'r') as f:
                profiles = json.load(f)
            with open('assets/json/config.json', 'r') as f:
                config = json.load(f)

            for react in message.reactions:
                async for user in react.users():
                    if user.id == int(config[str(payload.guild_id)]['gigiid']):
                        posted = True
                    if emoji.name != '🏆' or posted:
                        return
            await message.add_reaction(emoji)
            posting_channel = await self.bot.fetch_channel(int(config[str(payload.guild_id)]['triumphant']))
            if message.embeds:
                for member in guild.members:
                    if str(member.name) in message.embeds[0].description:
                        not_bot_user = member.id
                        users[str(member.id)] = 1
                        break
                    else:
                        continue
                for i in profiles.keys():
                    for j in profiles[i].keys():
                        if profiles[i][j] in message.embeds[0].description:
                            not_bot_user = int(i)
                        else:
                            continue
                copy_embed = message.embeds[0].to_dict()
                if message.content:
                    try:
                        content = message.content.__add__(f'\n\n**Link Preview:**\n{copy_embed["description"]}')
                    except KeyError:
                        try:
                            content = message.content.__add__(f'\n\n**Link Preview:**\n{copy_embed["title"]}')
                        except KeyError:
                            pass
                        pass
                else:
                    try:
                        content = copy_embed["description"]
                    except KeyError:
                        content = copy_embed["title"]
                if "fields" in copy_embed:
                    for embeds in message.embeds:
                        for field in embeds.fields:
                            content = content.__add__(f'\n\n**{field.name}**')
                            content = content.__add__(f'\n{field.value}')
            else:
                content = message.content
                if message.mentions:
                    for member in guild.members:
                        if member in message.mentions:
                            id_list.append(str(member.id))
                            name_list.append(str(member.name))
            embed = discord.Embed(title=f"{message.author} said...",
                                  description=f'{content}\n\n[Jump to Message](https://discordapp.com/channels/{payload.guild_id}/{payload.channel_id}/{payload.message_id})',
                                  colour=0x784fd7,
                                  timestamp=message.created_at)
            if id_list:
                name_string = "\n".join(name_list)
                id_string = "\n".join(id_list)
                print(f"1 {id_string}")
                print(f"2 {name_string}")
                embed.add_field(name="People mentioned in the message:", value=name_string)
                embed.add_field(name="IDs:", value=id_string)
            if not msg.author.bot:
                embed.set_footer(text=f"ID:{msg.author.id}")
                embed.set_thumbnail(url=msg.author.avatar_url)
                embed.add_field(name="Nominated User:", value=f"{msg.author.name}")
            if msg.author.bot:
                if not_bot_user:
                    embed.set_footer(text=f"ID:{not_bot_user}")
                    avatar_member = self.bot.get_user(not_bot_user)
                    embed.set_thumbnail(url=avatar_member.avatar_url)
                    embed.add_field(name="Nominated User:", value=f"{avatar_member.name}")
            if message.embeds:
                if "image" in copy_embed:
                    embed.set_image(url=copy_embed["image"]["url"])
                elif "video" in copy_embed:
                    embed.set_image(url=copy_embed["thumbnail"]["url"])
            elif message.attachments:
                embed.set_image(url=message.attachments[0].url)
            embed.add_field(name='Nominated by:', value=f'{payload.member.name}')
            await posting_channel.send(embed=embed)
            if os.path.isfile(f'assets/json/server/{guild.id}/triumphant.json'):
                with open(f'assets/json/server/{guild.id}/triumphant.json', 'r') as f:
                    users = json.load(f)
            if not msg.author.bot:
                users[str(msg.author.id)] = 1
            if msg.author.bot and not_bot_user:
                users[str(not_bot_user)] = 1
            if message.mentions:
                for member in id_list:
                    users[str(member)] = 1
            with open(f'assets/json/server/{guild.id}/triumphant.json', 'w') as f:
                json.dump(users, f)

    @commands.command(hidden=True)
    @has_permissions(manage_messages=True)
    async def triumph_delete(self, ctx, member_id: int):
        member = await ctx.guild.fetch_member(member_id=member_id)
        with open(f'assets/json/server/{ctx.guild.id}/triumphant.json', 'r') as f:
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
        with open(f'assets/json/server/{ctx.guild.id}/triumphant.json', 'w+') as f:
            json.dump(users, f)
        await ctx.send(f"Succesfully deleted {member.name} from triumphant list. ID: {member_id}")

    @commands.command(hidden=True)
    @has_permissions(manage_messages=True)
    async def triumph_add(self, ctx, member_id: int):
        member = await ctx.guild.fetch_member(member_id=member_id)
        with open(f'assets/json/server/{ctx.guild.id}/triumphant.json', 'r') as f:
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

        with open(f'assets/json/server/{ctx.guild.id}/triumphant.json', 'w') as f:
            json.dump(users, f)

        add_embed = discord.Embed(title='User is now triumphant')
        add_embed.add_field(name="User:", value=f"{member.name}")
        add_embed.add_field(name="User Id:", value=f"{member_id}")
        await ctx.send(embed=add_embed)

    @commands.command(hidden=True)
    @has_permissions(manage_messages=True)
    @commands.is_owner()
    async def triumph_list(self, ctx):
        id_list = ''
        user_list = ''
        with open(f'assets/json/server/{ctx.guild.id}/triumphant.json', 'r') as f:
            users = json.load(f)

        for key in users:
            member = await ctx.guild.fetch_member(member_id=int(key))
            user_list = user_list + str(member.name) + " \n"
            id_list = id_list + key + " \n"

        list_embed = discord.Embed(title='Members on the triumphant list')
        list_embed.add_field(name='List:', value=f"{user_list}")
        list_embed.add_field(name="IDs:", value=f"{id_list}")
        await ctx.send(embed=list_embed)

    @commands.command(hidden=True)
    @has_permissions(manage_messages=True)
    @commands.is_owner()
    async def give_triumphant(self, ctx):
        triumphant_role = discord.utils.get(ctx.author.guild.roles, name="Triumphant/Reward")
        current_triumphant = list(triumphant_role.members)
        member_list = ""

        with open(f'assets/json/server/{ctx.guild.id}/triumphant.json', 'r') as f:
            users = json.load(f)

        for member in current_triumphant:
            await member.remove_roles(triumphant_role)

        for key in users:
            user = ctx.channel.guild.get_member(user_id=int(key))
            member_list = member_list + user.name + '\n'
            await user.add_roles(triumphant_role)

        os.remove(f'assets/json/server/{ctx.guild.id}/triumphant.json')

        triumph_embed = discord.Embed(title="Triumphant Role Success",
                                      description="These users have received their role.")
        triumph_embed.add_field(name="Users:", value=f"{member_list}")
        await ctx.send(embed=triumph_embed)

    @commands.command(hidden=True)
    @has_permissions(manage_messages=True)
    async def start_timer(self, ctx):
        self.triumphant_timer.start()

    @tasks.loop(hours=168)
    async def triumphant_timer(self):
        for server in self.bot.guilds:
            with open('assets/json/config.json', 'r') as f:
                config = json.load(f)
            chan = self.bot.get_channel(config[server]['triumphant'])

            await chan.send("\U0001f5d3 Timer Started \U0001f5d3")

            if os.path.isfile(f'server/{str(server.id)}/triumphant_copy.json'):
                os.remove(f'assets/json/server/{str(server.id)}/triumphant_copy.json')
            with open(f'assets/json/server/{str(server.id)}/triumphant.json', 'r') as f:
                users = json.load(f)

            with open(f'assets/json/server/{str(server.id)}/triumphant_copy.json', 'w+') as f:
                json.dump(users, f)

            os.remove(f'assets/json/server/{str(server.id)}/triumphant.json')

            reset_embed = discord.Embed(title="\U0001f5d3| New Week Starts Here. Get that bread!")

            await chan.send(embed=reset_embed)


def setup(bot):
    bot.add_cog(TriumphantCog(bot))
