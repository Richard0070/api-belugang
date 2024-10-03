from PIL import Image, ImageDraw, ImageFont
import os
import aiohttp
from io import BytesIO
import asyncio
from datetime import datetime
import math
import requests
import random
from flask import Flask, send_file, request, render_template, jsonify
from functions import *

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')
    
@app.route('/generate_card')
async def card_endpoint():
    encrypted_query = request.args.get('query')

    if not encrypted_query:
        return "Missing parameters", 400

    decoded_data = decode(encrypted_query)
    username = decoded_data.get('username')
    pfp_url = decoded_data.get('pfp_url')
    level = decoded_data.get('level')
    xp = decoded_data.get('xp')
    xp_out_of = decoded_data.get('xp_out_of')
    rank = decoded_data.get('rank')

    if pfp_url == "":
        pfp_url = "https://cdn.discordapp.com/embed/avatars/0.png"

    img_byte_array = await card(username, pfp_url, level, xp, xp_out_of, rank)
    
    return send_file(img_byte_array, mimetype='image/png')
        
async def card(username, pfp_url, level, xp, xp_out_of, rank):
    async with aiohttp.ClientSession() as session:
        async with session.get(pfp_url) as response:
            response.raise_for_status()
            image_data = await response.read()
    avatar = Image.open(BytesIO(image_data)).convert("RGBA")

    new_size = (280, 280)
    avatar = avatar.resize(new_size) # Resize avatar

    mask = Image.new("L", avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    offset = 4
    draw.ellipse((offset, offset, avatar.size[0] - offset, avatar.size[1] - offset), fill=255)
    avatar = Image.composite(avatar, Image.new("RGBA", avatar.size), mask)

    font1 = ImageFont.truetype("assets/fonts/Montserrat-Bold.ttf", size=60)
    font2 = ImageFont.truetype("assets/fonts/Montserrat-Bold.ttf", size=40)

    # Randomize the background card
    bg_cards = ["card_1"]  # rename to card_1 later
    
    selected_bg = random.choice(bg_cards)
    bg = Image.open(f"assets/rankcards/{selected_bg}.png").convert("RGBA")
    
    bg.paste(avatar, (60, 60), mask=avatar)

    draw = ImageDraw.Draw(bg)
    member_name = "@" + username if len(username) <= 20 else f"{username[:17]}..."
    member_xp = shorten_int(int(xp))
    member_xp_out_of = shorten_int(int(xp_out_of))
    percentage = round(int(xp) / int(xp_out_of) * 100, 1)

    formatted_rank = f"# {int(rank)//1000}K+" if int(rank) > 1000 else f"# {rank}"

    draw.text((410, 50), member_name, (255, 255, 255), font=font1)
    draw.text((410, 200), f"LEVEL - {level}", (255, 255, 255), font=font2)
 
    xp_text = f"XP - {member_xp} / {member_xp_out_of}"
    draw.text((700, 200), xp_text, (255, 255, 255), font=font2)   
    xp_text_width = draw.textlength(xp_text, font=font2)    

    draw.text((700 + xp_text_width + 50, 200), formatted_rank, (255, 255, 255), font=font2)
    
    progress_bar_img = progress_bar_image(percentage, height_pixels=40, width_pixels=750)    
    bg.paste(progress_bar_img, (410, 290), mask=progress_bar_img)

    img_byte_array = BytesIO()
    bg.save(img_byte_array, format='PNG')
    img_byte_array.seek(0)

    return img_byte_array
    
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
      image_path = 'assets/images/base2.png'
      img = Image.open(image_path)
      draw = ImageDraw.Draw(img)

      font1 = ImageFont.truetype("assets/fonts/font.ttf", size=40)
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
