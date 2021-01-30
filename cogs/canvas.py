import json
import discord
from discord.ext import commands
from discord import File

from PIL import Image, ImageDraw, ImageFont
import io


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sys_aliases = {'PS': {'PS', 'PSN', 'PS4', 'PS5', 'PLAYSTATION'},
                            'XB': {'XB', 'XB1', 'XBOX', 'MICROSOFT'},
                            'STEAM': {'STEAM', 'VALVE'},
                            'UPLAY': {'UPLAY', 'UBI', 'UBISOFT'},
                            'FFXIV': {'FFXIV', 'XIV', 'FF'}}

    @staticmethod
    def sort(user):
        sort_order = ['PS', 'XB', 'UPLAY', 'FFXIV', 'STEAM', 'STEAMURL', 'WANTEDTEXT']
        sorted_list = {}
        unsorted = {}
        for x in range(len(sort_order)):
            for key in user:
                try:
                    if key == sort_order[x]:
                        sorted_list[key] = user[key]
                    else:
                        unsorted[key] = user[key]
                except IndexError:
                    continue
        for key in unsorted:
            user[key] = unsorted[key]
        return sorted_list

    @commands.Cog.listener()
    async def on_member_join(self, member):
        with open(f'assets/json/server/{str(member.guild.id)}/profiles.json', 'r') as f:
            users = json.load(f)
        users[str(member.id)] = {}
        with open(f'assets/json/server/{str(member.guild.id)}/profiles.json', 'w') as f:
            json.dump(users, f)

    @commands.command(aliases=['reset_profiles'], hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    async def build_profiles(self, ctx):
        users = {}
        for member in ctx.guild.members:
            users[str(member.id)] = {}
        with open(f'assets/json/server/{str(ctx.guild.id)}/profiles.json', 'w') as f:
            json.dump(users, f)
        await ctx.send("Done")

    @commands.command(aliases=['add'])
    async def set(self, ctx, system: str, *name: str):
        """Add your usernames for your game system"""
        system = system.upper()
        name_joined = " ".join(name)
        with open(f'assets/json/server/{str(ctx.guild.id)}/profiles.json', 'r') as f:
            users = json.load(f)
        for platform in self.sys_aliases:
            if system in self.sys_aliases[platform]:
                if system == 'PS' and len(name_joined) > 16:
                    await ctx.send(embed=discord.Embed(title='Error',
                                                       description='PSN names must not exceed 16 characters'))
                    return
                if system == 'XB' and len(name_joined) > 16:
                    await ctx.send(embed=discord.Embed(title='Error',
                                                       description='GamerTags must not exceed 15 characters'))
                    return
                if system == 'STEAM' and len(name_joined) > 32:
                    await ctx.send(embed=discord.Embed(title='Error',
                                                       description='Steam usernames must not exceed 32 characters'))
                    return
                if system == 'UPLAY' and len(name_joined) > 15:
                    await ctx.send(embed=discord.Embed(title='Error',
                                                       description='Uplay usernames must not exceed 12 characters'))
                    return
                if system == 'FFXIV' and len(name_joined) > 20:
                    await ctx.send(embed=discord.Embed(title='Error',
                                                       description='FFXIV names must not exceed 20 characters'))
                    return
                try:
                    users[str(ctx.author.id)][platform] = name_joined
                except KeyError:
                    users[str(ctx.author.id)] = {}
                    users[str(ctx.author.id)][platform] = name_joined
                with open(f'assets/json/server/{str(ctx.guild.id)}/profiles.json', 'w') as f:
                    users[str(ctx.author.id)] = self.sort(users[str(ctx.author.id)])
                    json.dump(users, f)
                await ctx.send(embed=discord.Embed(title=f"Successfully added your {platform} ID: {name_joined}"))
                if platform == 'STEAM':
                    await ctx.send(embed=discord.Embed(title='Reminder',
                                                       description=f'Remember to set a Steam URL using:\n'
                                                       f'**`{ctx.prefix}set steamurl <...>`**'))
                return
            elif system == 'STEAMURL':
                users[str(ctx.author.id)][system] = '<' + name_joined.strip('<>') + '>'
                with open(f'assets/json/server/{str(ctx.guild.id)}/profiles.json', 'w') as f:
                    users[str(ctx.author.id)] = self.sort(users[str(ctx.author.id)])
                    json.dump(users, f)
                await ctx.send(embed=discord.Embed(title=f"Successfully set your Steam URL to:\n{name_joined}"))
                return
        else:
            await ctx.send(embed=discord.Embed(title='Error',
                                               description=f"{system} not a valid, found platform or alias."))
            return

    @commands.command()
    async def get(self, ctx, system: str, member: discord.Member = None):
        """Get a users usernames."""
        if member is None:
            member = ctx.author
        system = system.upper()
        for platform in self.sys_aliases:
            if system in self.sys_aliases[platform]:
                with open(f'assets/json/server/{str(ctx.guild.id)}/profiles.json', 'r') as f:
                    users = json.load(f)
                try:
                    if users[str(member.id)]:
                        username = users[str(member.id)][platform]
                except KeyError:
                    if member == ctx.author:
                        await ctx.send(embed=discord.Embed(title='Error',
                                                           description=f'You do not appear to have a profile, or do not have that system registered.'
                                                           f' System provided was {system}.'))
                    elif member != ctx.author:
                        await ctx.send(embed=discord.Embed(title='Error',
                                                           description=f'{member.name} does not have a profile for that system. System provided was {system}'))
                    return
                await ctx.send(embed=discord.Embed(title=f'{member.name}\'s username for {platform} is {username}'))
                if platform == 'STEAM':
                    try:
                        await ctx.send(embed=discord.Embed(
                            title='{}\'s Steam URL is {}'.format(member.name, users[str(member.id)]['STEAMURL'])))
                    except KeyError:
                        await ctx.send(embed=discord.Embed(title='Reminder',
                                                           description=f'You have not set a Steam URL for your {platform} username yet\n'
                                                           f'Remember to set one using **`{ctx.prefix}set steamurl <...>`**'))
                return
        await ctx.send(f"Error. {system} not a valid platform or alias.")

    @commands.command()
    async def search(self, ctx, query: str = None, exact_match: bool = False):
        """Search for a user"""
        matches = []
        if query:
            with open(f'assets/json/server/{str(ctx.guild.id)}/profiles.json', 'r') as f:
                users = json.load(f)
            for user in users:
                match = None
                for platform in users[user]:
                    if exact_match:
                        if query.upper() == users[user][platform].upper():
                            match = ctx.guild.get_member(int(user))
                    else:
                        if query.upper() in users[user][platform].upper():
                            match = ctx.guild.get_member(int(user))
                if match:
                    matches.append(match.mention)
            if matches:
                new_embed = discord.Embed(title=f'*Found __{str(len(matches))}__ for query: "__{query}__":*')
                new_embed.add_field(name=f'Exact Match = {str(exact_match)}',
                                    value='\n'.join(matches),
                                    inline=True)
                await ctx.send(embed=new_embed)
                return
            else:
                await ctx.send(embed=discord.Embed(title=f'*No matches for "__{query}__" found with criteria*'))
                return
        else:
            await ctx.send(embed=discord.Embed(title='Please format your search request properly:',
                                               description=f'`{ctx.prefix}search <query> <exact_match=True/False>`'))

    @commands.command(aliases=['del'])
    async def delete(self, ctx, system):
        """Delete a username"""
        with open(f'assets/json/server/{str(ctx.guild.id)}/profiles.json', 'r') as f:
            users = json.load(f)
        system = system.upper()
        user = {}
        if system == 'WANTED':
            system = 'WANTEDTEXT'
        for platform in self.sys_aliases:
            if system in self.sys_aliases[platform]:
                try:
                    if users[str(ctx.author.id)][platform]:
                        for key in users[str(ctx.author.id)]:
                            user[key] = users[str(ctx.author.id)][key]
                        system_name = list(user)
                        for item in system_name:
                            if item == platform:
                                del user[item]
                                if item == 'STEAM':
                                    try:
                                        del user['STEAMURL']
                                    finally:
                                        pass
                        users[str(ctx.author.id)] = user
                        with open(f'assets/json/server/{str(ctx.guild.id)}/profiles.json', 'w') as f:
                            users[str(ctx.author.id)] = self.sort(users[str(ctx.author.id)])
                            json.dump(users, f)
                        await ctx.send(embed=discord.Embed(title=f'Successfully deleted your profile for {platform}'))
                        return
                except KeyError:
                    await ctx.send(embed=discord.Embed(title='Error',
                                                       description=f'It appears you do not have profile for that platform.'
                                                       f'Make sure you typed it in properly. You used {system}'))

    @commands.command(aliases=['plist'])
    async def profile_list(self, ctx, member: discord.Member = None):
        """Text only profile"""
        if member is None:
            member = ctx.author
        profile = {}
        async with ctx.message.channel.typing():
            with open(f'assets/json/server/{str(ctx.guild.id)}/profiles.json', 'r') as f:
                users = json.load(f)
            try:
                for key in users[str(member.id)]:
                    if key == 'WANTEDTEXT':
                        continue
                    profile[key] = users[str(member.id)][key]
            except KeyError:
                await ctx.send(embed=discord.Embed(
                    title='It appears you haven\'t set up your profile yet! Please use the `set` command'))
                return
            profile_embed = discord.Embed(title="GoldxGuns Profile", description=f"{member.name}'s profile:")
            for key in profile:
                if key == 'PS':
                    system = "Playstation"
                if key == 'XB':
                    system = 'Xbox'
                if key == 'STEAM':
                    system = 'Steam'
                if key == 'UPLAY':
                    system = 'Uplay'
                if key == 'STEAMURL':
                    system = 'Steam URL'
                if key == 'FFXIV':
                    system = "Final Fantasy"
                profile_embed.add_field(name=str(system), value=str(profile[key]), inline=True)
            await ctx.send(embed=profile_embed)
            return

    @commands.command(aliases=['card', 'profilecard', 'canvas'])
    async def profile(self, ctx, member: discord.Member = None):
        """Displays your profile card."""
        sys_alias = {'PS': "assets/icon/ps_logo.png",
                     'XB': "assets/icon/xb_logo.png",
                     'STEAM': "assets/icon/steam_logo.png",
                     'UPLAY': "assets/icon/ubi_logo.png",
                     'FFXIV': "assets/icon/xiv_logo.png"}
        if member is None:
            member = ctx.author
        async with ctx.message.channel.typing():
            with open(f'assets/json/server/{str(ctx.guild.id)}/profiles.json', 'r') as f:
                profiles = json.load(f)
            with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'r') as f:
                users = json.load(f)
            bg_img = Image.open("assets/card_to_draw.png").convert('RGBA')
            ref_img = bg_img.copy()
            draw = ImageDraw.Draw(ref_img)
            element_buffer = 20
            draw_bounds = [175, int(ref_img.width - element_buffer), 110, 200]
            ref_coord = [draw_bounds[0], draw_bounds[2]]
            pfp_buffer = [30, 75]
            level_val = int(users[str(member.id)]['level'])
            level_text = f'Level: {str(level_val).strip()}'
            bounty_val = f'{int(users[str(member.id)]["experience"]): ,}'
            title_font = ImageFont.truetype('assets/font/NASHVILL.ttf', 42)
            wanted_font = ImageFont.truetype('assets/font/NASHVILL.ttf', 18)
            level_font = ImageFont.truetype('assets/font/HELLDORA.ttf', 23)
            draw.line((element_buffer, 35, (element_buffer * 6), 35),
                      fill=(16, 16, 16), width=5)
            draw.line(((ref_img.width - (element_buffer * 6)), 35, (ref_img.width - element_buffer), 35),
                      fill=(16, 16, 16), width=5)
            draw.text((int((ref_img.width - draw.textsize('WANTED', font=title_font)[0]) / 2), 15),
                      'WANTED', fill=(0, 0, 0), font=title_font)
            draw.line(((element_buffer * 2), 60, (ref_img.width - (element_buffer * 2)), 60),
                      fill=(16, 16, 16), width=5)
            if member.avatar is None:
                avatar_image = Image.open("assets/gigi_avatar.png").resize((128, 128)).convert('RGBA')
            elif member.avatar:
                avatar_asset = member.avatar_url_as(format='png', size=128)
                buffer_avatar = io.BytesIO()
                await avatar_asset.save(buffer_avatar)
                buffer_avatar.seek(0)
                avatar_image = Image.open(buffer_avatar).resize((128, 128)).convert('RGBA')
            emblem_image = Image.open(f"assets/emblem_{level_val}.png").convert('RGBA')
            draw.rectangle(((pfp_buffer[0] - 5, pfp_buffer[1] - 5),
                            (pfp_buffer[0] + avatar_image.width + 4), (pfp_buffer[1] + avatar_image.height + 4)),
                           fill=None, outline=(16, 16, 16), width=5)
            ref_img.paste(avatar_image, (pfp_buffer[0], pfp_buffer[1]), avatar_image)
            ref_img.paste(emblem_image, (pfp_buffer[0] + int((avatar_image.width / 2) - (emblem_image.width / 2)),
                                         pfp_buffer[1] + avatar_image.height + 1), emblem_image)
            draw.text((180, 70), level_text, fill=(0, 0, 0), font=level_font)
            draw.line((int(180 + draw.textsize(level_text, level_font)[0] + (element_buffer / 2)), 60,
                       int(180 + draw.textsize(level_text, level_font)[0] + (element_buffer / 2)), 100),
                      fill=(16, 16, 16), width=3)
            draw.text(((180 + draw.textsize(level_text, level_font)[0] + element_buffer), 70),
                      f'Bounty: ${str(bounty_val).strip()}', fill=(0, 0, 0), font=level_font)
            draw.line(((ref_coord[0] - 12), int(ref_coord[1] - (element_buffer / 2)),
                       (ref_img.width - (element_buffer * 2)), int(ref_coord[1] - (element_buffer / 2))),
                      fill=(16, 16, 16), width=4)
            for key in profiles[str(member.id)]:
                start_coord = [draw_bounds[0], (draw_bounds[2] - 5)]
                username = f'{profiles[str(member.id)][key]}'
                font_size = 18
                sys_img = None
                threshold = 10
                while len(username) >= threshold:
                    try:
                        first, second = username.split(' ')
                        username = first + '\n' + second
                    except ValueError:
                        pass
                    font_size -= 2
                    threshold += 5
                font = ImageFont.truetype('assets/font/libel_suit.ttf', font_size)
                url_font = ImageFont.truetype('assets/font/libel_suit.ttf', 14)
                for platform in sys_alias:
                    if key in platform:
                        sys_img = Image.open(sys_alias[platform]).convert('RGBA').resize((30, 30))
                    elif key == 'WANTEDTEXT' or key == 'STEAMURL':
                        continue
                if sys_img:
                    if (ref_coord[0] + sys_img.width + draw.multiline_textsize(username, font)[0]) >= draw_bounds[1]:
                        ref_coord[0] = start_coord[0]
                        ref_coord[1] += 35
                    ref_img.paste(sys_img, (ref_coord[0], (ref_coord[1])), sys_img)
                    draw.text(((ref_coord[0] + sys_img.width + 5),
                               (ref_coord[1] + (sys_img.height - draw.multiline_textsize(username, font)[1]) / 2)),
                              username, fill=(0, 0, 0), font=font)
                    ref_coord[0] += (sys_img.width + 85)
                # elif key == 'STEAMURL':
                # draw.text((start_coord[0], ref_coord[1] + (element_buffer * 2)),
                #          profiles[str(member.id)][key].strip('<>'), fill=(32, 32, 32), font=url_font)
            draw.line(((element_buffer * 2), 240, (ref_img.width - (element_buffer * 2)), 240),
                      fill=(16, 16, 16), width=5)
            draw.text((20, 252), 'Wanted for', fill=(0, 0, 0), font=wanted_font, )
            try:
                wanted_text = profiles[str(member.id)]['WANTEDTEXT']
            except KeyError:
                wanted_text = 'Shootin\', lootin\' and rootin\' tootin\' degeneracy'
            draw.text((35, 275), wanted_text, fill=(32, 32, 32), font=wanted_font)
            buffer_output = io.BytesIO()
            ref_img.save(buffer_output, format='PNG')
            buffer_output.seek(0)
            await ctx.send(file=File(buffer_output, 'myimage.png'))

    @commands.command()
    async def wanted(self, ctx, *text):
        """Sets the custom wanted text on your profile card. """
        text = " ".join(text)
        with open(f'assets/json/server/{str(ctx.guild.id)}/profiles.json', 'r') as f:
            users = json.load(f)
        if len(text) > 0:
            if len(text) > 50:
                await ctx.send(embed=discord.Embed(title='Error',
                                                   description='Your wanted text cannot be longer than 50 characters'))
                return
            users[str(ctx.author.id)]['WANTEDTEXT'] = text
            await ctx.send(embed=discord.Embed(title=f'Successfully added the wanted text to your profile card'))
        else:
            try:
                del users[str(ctx.author.id)]['WANTEDTEXT']
            except KeyError:
                pass
            await ctx.send(embed=discord.Embed(title=f'Successfully changed wanted text to default'))
        with open(f'assets/json/server/{str(ctx.guild.id)}/profiles.json', 'w') as f:
            users[str(ctx.author.id)] = self.sort(users[str(ctx.author.id)])
            json.dump(users, f)


def setup(bot):
    bot.add_cog(Profile(bot))
