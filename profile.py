import urllib.request

from discord.ext import commands
from discord import File

from PIL import Image, ImageDraw, ImageFont
import io

# read background image only once
url = 'https://i.imgur.com/FizDC6y.png'
response = urllib.request.urlopen(url)
background_image = Image.open(response)  # it doesn't need `io.Bytes` because it `response` has method `read()`
background_image = background_image.convert('RGBA')  # add channel ALPHA to draw transparent rectangle


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='canvas')
    async def canvas(self, ctx):
        AVATAR_SIZE = 128

        # --- duplicate image ----

        image = background_image.copy()

        image_width, image_height = image.size

        # --- draw on image ---

        # create object for drawing

        # draw = ImageDraw.Draw(image)

        # draw red rectangle with alpha channel on new image (with the same size as original image)

        rect_x0 = 20  # left marign
        rect_y0 = 20  # top marign

        rect_x1 = image_width - 20  # right margin
        rect_y1 = 20 + AVATAR_SIZE - 1  # top margin + size of avatar

        rect_width = rect_x1 - rect_x0
        rect_height = rect_y1 - rect_y0

        rectangle_image = Image.new('RGBA', (image_width, image_height))
        rectangle_draw = ImageDraw.Draw(rectangle_image)

        rectangle_draw.rectangle((rect_x0, rect_y0, rect_x1, rect_y1), fill=(255, 0, 0, 128))

        # put rectangle on original image

        image = Image.alpha_composite(image, rectangle_image)

        # create object for drawing

        draw = ImageDraw.Draw(image)  # create new object for drawing after changing original `image`

        # draw text in center

        text = f'Hello {ctx.author.name}'

        font = ImageFont.truetype('arial.ttf', 30)

        text_width, text_height = draw.textsize(text, font=font)
        x = (rect_width - text_width - AVATAR_SIZE) // 2  # skip avatar when center text
        y = (rect_height - text_height) // 2

        x += rect_x0 + AVATAR_SIZE  # skip avatar when center text
        y += rect_y0

        draw.text((x, y), text, fill=(0, 0, 255, 255), font=font)

        # --- avatar ---

        # get URL to avatar
        # sometimes `size=` doesn't gives me image in expected size so later I use `resize()`
        avatar_asset = ctx.author.avatar_url_as(format='jpg', size=AVATAR_SIZE)

        # read JPG from server to buffer (file-like object)
        buffer_avatar = io.BytesIO()
        await avatar_asset.save(buffer_avatar)
        buffer_avatar.seek(0)

        # read JPG from buffer to Image
        avatar_image = Image.open(buffer_avatar)

        # resize it
        avatar_image = avatar_image.resize((AVATAR_SIZE, AVATAR_SIZE))  #

        image.paste(avatar_image, (rect_x0, rect_y0))

        # --- sending image ---

        # create buffer
        buffer_output = io.BytesIO()

        # save PNG in buffer
        image.save(buffer_output, format='PNG')

        # move to beginning of buffer so `send()` it will read from beginning
        buffer_output.seek(0)

        # send image
        await ctx.send(file=File(buffer_output, 'myimage.png'))


def setup(bot):
    bot.add_cog(Profile(bot))
