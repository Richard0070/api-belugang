from PIL import Image, ImageDraw, ImageFont
import os
import aiohttp
from io import BytesIO
import asyncio
from datetime import datetime
import math
import requests
from flask import Flask, send_file, request, render_template
from functions import *

app = Flask(__name__)

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

def ensure_url_format(url, apply_www=False):
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    if apply_www:
        scheme, rest = url.split("://", 1)
        if not rest.startswith("www."):
            url = f"{scheme}://www.{rest}"
    return url

@app.route('/redirect', methods=['GET'])
def check_redirect():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    original_url = ensure_url_format(url, apply_www=False)
    try:
        response = requests.get(original_url, allow_redirects=True)
        total_redirects = len(response.history)
        redirect_chain = []

        for i, resp in enumerate(response.history[:4]):
            formatted_url = ensure_url_format(resp.url, apply_www=False)
            if i == 0 and formatted_url == original_url:
                continue
            truncated_url = formatted_url[:35] + '...' if len(formatted_url) > 38 else formatted_url
            redirect_chain.append({
                "status_code": resp.status_code,
                "url": truncated_url
            })

        final_url = ensure_url_format(response.url, apply_www=False)
        truncated_final_url = final_url[:35] + '...' if len(final_url) > 38 else final_url
        if final_url != original_url:
            redirect_chain.append({
                "status_code": response.status_code,
                "url": truncated_final_url
            })

        redirect_data = {
            "original_url": original_url[:35] + '...' if len(original_url) > 38 else original_url,
            "redirect_chain": redirect_chain,
            "date_d": datetime.now().strftime("%d"),
            "date_m": datetime.now().strftime("%m"),
            "date_y": datetime.now().strftime("%y"),
            "total_redirects": total_redirects 
        }

        img = create_redirect_image(redirect_data)
        img_byte_array = BytesIO()
        img.save(img_byte_array, format='PNG')
        img_byte_array.seek(0)

        return send_file(img_byte_array, mimetype='image/png')

    except requests.exceptions.RequestException as e:
        error_data = {
            "error": str(e) 
        }

        img = create_error_image(error_data)
        img_byte_array = io.BytesIO()
        img.save(img_byte_array, format='PNG')
        img_byte_array.seek(0)

        return send_file(img_byte_array, mimetype='image/png')
        
def create_redirect_image(redirect_data):
    image_path = 'assets/images/base.png'
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    font1 = ImageFont.truetype("assets/fonts/font7.ttf", size=94)
    font2 = ImageFont.truetype("assets/fonts/font7.ttf", size=98)

    draw.text((1175, 140), f"{redirect_data['total_redirects']}", fill=(255, 255, 255), font=font1)
    
    draw.text((2240, 140), f"{redirect_data['date_d']}", fill=(255, 255, 255), font=font1)        
    draw.text((2480, 140), f"{redirect_data['date_m']}", fill=(255, 255, 255), font=font1)        
    draw.text((2745, 140), f"{redirect_data['date_y']}", fill=(255, 255, 255), font=font1)
    
    draw.text((210, 760), "1", fill=(255, 255, 255), font=font2)
    draw.text((550, 760), f"{redirect_data['original_url']}", fill=(233, 233, 233), font=font2)

    y_offset = 1060
    for i, redirect in enumerate(redirect_data['redirect_chain']):
       draw.text((210, y_offset), f"{i+2}", fill=(255, 255, 255), font=font2)
       draw.text((550, y_offset), f"{redirect['url']}", fill=(233, 233, 233), font=font2)
       y_offset += 290

    return img

def create_error_image(error_data):
      image_path = 'base2.png'
      img = Image.open(image_path)
      draw = ImageDraw.Draw(img)

      font1 = ImageFont.truetype("fonts/font.ttf", size=40)
      max_width = 1790

      lines = []
      words = error_data['error'].split()
      current_line = ""

      for word in words:
          test_line = f"{current_line} {word}".strip()
          text_bbox = draw.textbbox((0, 0), test_line, font=font1)
          text_width = text_bbox[2] - text_bbox[0]
          if text_width <= max_width:
              current_line = test_line
          else:
              if current_line:
                  lines.append(current_line)
              current_line = word

      if current_line:
          lines.append(current_line)

      y_text = 560
      for line in lines:
          draw.text((110, y_text), line, fill=(255, 255, 255), font=font1)
          y_text += draw.textbbox((0, 0), line, font=font1)[3] - draw.textbbox((0, 0), line, font=font1)[1]

      return img
    
if __name__ == "__main__":
    app.run(debug=True)
