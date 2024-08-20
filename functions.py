from PIL import Image, ImageDraw
import time

def round_to_lowest_hundred(number):
    number = int(number)
    if int(number) < 1000:
        return str(number)
    elif int(number) < 10000:
        return f"{number/1000:.1f}k"
    else:
        return f"{number/1000:.0f}k"

def shorten_int(n):
    suffixes = ['', 'K', 'M', 'B', 'T', 'P', 'E', 'Z', 'Y']
    magnitude = 0
    while abs(n) >= 1000:
        magnitude += 1
        n /= 1000.0
    if abs(n) < 10 and n != 0:
        result = '{:.1f}{}'.format(n, suffixes[magnitude])
        if result.startswith('0'):
            result = result[1:]
        return result.rstrip('0').rstrip('.').replace('.0', '')
    else:
        return '{:.0f}{}'.format(n, suffixes[magnitude])
        
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return rgb

def draw_rounded_rectangle(draw, xy, color, border_radius):
    top_left, bottom_right = xy
    x1, y1 = top_left
    x2, y2 = bottom_right

    color_rgb = hex_to_rgb(color)

    # Draw the rounded rectangle
    draw.rectangle([x1 + border_radius, y1, x2 - border_radius, y2], fill=color_rgb)
    draw.rectangle([x1, y1 + border_radius, x2, y2 - border_radius], fill=color_rgb)
    draw.pieslice([x1, y1, x1 + 2 * border_radius, y1 + 2 * border_radius], 180, 270, fill=color_rgb)
    draw.pieslice([x2 - 2 * border_radius, y1, x2, y1 + 2 * border_radius], 270, 360, fill=color_rgb)
    draw.pieslice([x1, y2 - 2 * border_radius, x1 + 2 * border_radius, y2], 90, 180, fill=color_rgb)
    draw.pieslice([x2 - 2 * border_radius, y2 - 2 * border_radius, x2, y2], 0, 90, fill=color_rgb)

def progress_bar_image(percentage, height_pixels, width_pixels):
    # Create a blank image with an RGBA mode
    image = Image.new('RGBA', (width_pixels, height_pixels), (255, 255, 255, 0))

    # Create a drawing object
    draw = ImageDraw.Draw(image)

    # Set the border radius for the curved edges
    border_radius = height_pixels // 2

    # Draw the background rectangle with curved edges (backside)
    draw_rounded_rectangle(draw, [(0, 0), (width_pixels, height_pixels)], "#333333", border_radius)

    fill_width = int(width_pixels * percentage / 100)

    if fill_width > border_radius * 2:
        draw_rounded_rectangle(draw, [(0, 0), (fill_width, height_pixels)], "#a89eFF", border_radius)
    else:
        draw_rounded_rectangle(draw, [(0, 0), (fill_width + border_radius * 2, height_pixels)], "#a89eFF", border_radius)

    return image
    
uppercase_letter_replacements = {
    "7Vp": 'A',
    "hrM": 'B',
    "qaq": 'C',
    "aGE": 'D',
    "7Rl": 'E',
    "Zbc": 'F',
    "l7j": 'G',
    "bAh": 'H',
    "PAq": 'I',
    "sJu": 'J',
    "jmd": 'K',
    "gco": 'L',
    "8ps": 'M',
    "0ov": 'N',
    "lV9": 'O',
    "7xs": 'P',
    "Tsp": 'Q',
    "4iV": 'R',
    "5y9": 'S',
    "28N": 'T',
    "pfN": 'U',
    "lxF": 'V',
    "CP5": 'W',
    "F5L": 'X',
    "lQ9": 'Y',
    "SD0": 'Z'
}

# Letter replacements (lowercase)
lowercase_letter_replacements = {
    "uUE": 'a',
    "z7A": 'b',
    "F6W": 'c',
    "MjW": 'd',
    "RjF": 'e',
    "3I9": 'f',
    "qp7": 'g',
    "SIg": 'h',
    "4tp": 'i',
    "wa8": 'j',
    "iyN": 'k',
    "R1L": 'l',
    "n0C": 'm',
    "KQK": 'n',
    "yvZ": 'o',
    "n1t": 'p',
    "LmD": 'q',
    "zWj": 'r',
    "mB1": 's',
    "wBW": 't'
}

def decode(encoded_str):
    decoded_str = encoded_str

    # Decode letter replacements (uppercase)
    for replacement, letter in uppercase_letter_replacements.items():
        decoded_str = decoded_str.replace(replacement, letter)
    
    # Decode letter replacements (lowercase)
    for replacement, letter in lowercase_letter_replacements.items():
        decoded_str = decoded_str.replace(replacement, letter)
    
    # Decode number replacements
    for replacement, number in number_replacements.items():
        decoded_str = decoded_str.replace(replacement, number)
    
    # Decode special character replacements
    for replacement, char in special_char_replacements.items():
        decoded_str = decoded_str.replace(replacement, char)
    pairs = decoded_str.split("&")
    result_dict = {key_value[0]: key_value[1] for key_value in (pair.split("=", 1) for pair in pairs)}
    return result_dict
