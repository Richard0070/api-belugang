from PIL import Image, ImageDraw, ImageFont
import os
import aiohttp
from io import BytesIO
import asyncio
import math
from quart import Quart, send_file, request, render_template
from functions import *

app = Quart(__name__)

@app.route("/")
def index():
    return render_template('index.html')
    
@app.route('/generate_card')
async def card_endpoint():
    username = request.args.get('username')
    pfp_url = request.args.get('pfp_url')
    level = request.args.get('level')
    xp = request.args.get('xp')
    xp_out_of = request.args.get('xp_out_of')
    rank = request.args.get('rank')
    color = request.args.get('color')

    if not all([username, pfp_url, level, xp, xp_out_of, rank, color]):
        return "Missing parameters", 400

    await card(username, pfp_url, level, xp, xp_out_of, rank, color)
    return await send_file("assets/cache/rankcard.png")

async def save_profile_picture(url):
    file_path = "assets/cache/av.png"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                image_data = await response.read()

        image = Image.open(BytesIO(image_data))
        image = image.resize((128, 128))
        image.save(file_path)

        return file_path
    except Exception as e:
        print(f"Error: {e}")
        return None

async def card(username, pfp_url, level, xp, xp_out_of, rank, color):
    await save_profile_picture(pfp_url)
    avatar = Image.open("assets/cache/av.png").convert("RGBA")
    background = Image.new("RGBA", avatar.size, (255, 255, 255, 0))
    mask = Image.new("L", avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    offset = 4
    draw.ellipse((offset, offset, avatar.size[0] - offset, avatar.size[1] - offset), fill=255)
    avatar = Image.composite(avatar, background, mask)
    color = color
    color_hex = get_hex_code(color)
    bg = Image.open(f"assets/rankcards/{color}.png").convert("RGBA")
    white = (233, 233, 233)
    grey = (116, 120, 121)
    green = grey
    bg.paste(avatar, (12, 12), mask=avatar)
    member_name = str(username)[0:19]
    member_level = level
    member_xp = xp
    member_rank = rank
    member_xp_out_of = shorten_int(int(xp_out_of)) 
    percentage = round(int(xp)/int(xp_out_of)*100, 1)
    progress_bar_img = progress_bar_image(round(float(str(percentage).replace("%", ""))), 20, 300, color_hex, 70)
    bg.paste(progress_bar_img, (115, 150), mask=progress_bar_img)
    font_normal = ImageFont.truetype("assets/fonts/font1.ttf", 30)
    font_normal2 = ImageFont.truetype("assets/fonts/font2.ttf", 22)
    font_normal3 = ImageFont.truetype("assets/fonts/font1.ttf", 35)
    font_normal4 = ImageFont.truetype("assets/fonts/font3.ttf", 24)
    font_normal5 = ImageFont.truetype("assets/fonts/font2.ttf", 25)
    draw = ImageDraw.Draw(bg)
    member_xp = round_to_lowest_hundred(member_xp)
    draw.text((148, 25), member_name, white, font=font_normal)
    draw.text((152, 95), f"Level: {member_level}", (255, 255, 255), font=font_normal4)
    draw.text((275, 95), f"XP: {member_xp}/{member_xp_out_of}", (255, 255, 255), font=font_normal4)
    draw.text((440, 95), f"Rank: #{member_rank}", (255, 255, 255), font=font_normal4)
    draw.text((36, 144), f"{str(percentage)}%", green, font=font_normal5)
    draw.text((550, 145), "100%", grey, font=font_normal5)
    bg.save(f"assets/cache/rankcard.png")

if __name__ == "__main__":
    app.run(debug=True)
