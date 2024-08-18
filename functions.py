from PIL import Image, ImageDraw

def get_hex_code(color_name):
    color_dict = {
        'blue': '#3498DB',
        'brown': '#8B4513',
        'burgundy': '#800020',
        'cerise': '#DE3163',
        'cyan': '#00FFFF',
        'gold': '#FFD700',
        'gray': '#808080',
        'green': '#008000',
        'lavender': '#C277EF',
        'midnight': '#191970',
        'orange': '#FFA500',
        'pink': '#ff66e8',
        'purple': '#800080',
        'red': '#FF0000',
        'salmon': '#FA8072',
        'tangerine': '#FFA07A',
        'teal': '#008080',
        'violet': '#EE82EE',
        'white': '#FFFFFF',
        'yellow': '#f1c431',
        "arcane": "#41B2B0",
        "card_base": "#FFFFFF"
    }

    # Convert color_name to lowercase to handle case-insensitivity
    lower_color_name = color_name.lower()

    # Check if the color name is in the dictionary
    if lower_color_name in color_dict:
        return color_dict[lower_color_name]
    else:
        return f"Hex code not found for {color_name}"

def hex_to_rgb(hex_color):
    # Remove '#' if it exists in the hex color code
    hex_color = hex_color.lstrip('#')

    # Convert the hex color code to an RGB tuple
    rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return rgb
  
def draw_rounded_rectangle(draw, xy, color, border_radius, transparency_percentage=0):
    top_left, bottom_right = xy
    x1, y1 = top_left
    x2, y2 = bottom_right

    # Convert hexadecimal color to RGB tuple
    color_rgb = hex_to_rgb(color)

    # Draw rectangle with curved edges
    draw.rectangle([(x1 + border_radius, y1), (x2 - border_radius, y2)], fill=color_rgb)
    draw.rectangle([(x1, y1 + border_radius), (x2, y2 - border_radius)], fill=color_rgb)

    # Draw four filled circles at each corner with transparency
    draw.pieslice([x1, y1, x1 + 2 * border_radius, y1 + 2 * border_radius], 180, 270, fill=color_rgb + (int(255 * (1 - transparency_percentage / 100)),))
    draw.pieslice([x2 - 2 * border_radius, y1, x2, y1 + 2 * border_radius], 270, 360, fill=color_rgb + (int(255 * (1 - transparency_percentage / 100)),))
    draw.pieslice([x1, y2 - 2 * border_radius, x1 + 2 * border_radius, y2], 90, 180, fill=color_rgb + (int(255 * (1 - transparency_percentage / 100)),))
    draw.pieslice([x2 - 2 * border_radius, y2 - 2 * border_radius, x2, y2], 0, 90, fill=color_rgb + (int(255 * (1 - transparency_percentage / 100)),))

    # Apply transparency to the rectangle
    alpha = int(255 * (1 - transparency_percentage / 100))
    fill_color = (color_rgb[0], color_rgb[1], color_rgb[2], alpha)
    draw.rectangle([x1 + border_radius, y1, x2 - border_radius, y2], fill=fill_color)

# Special character replacements
special_char_replacements = {
    "LkU0mY": '?',
    "erxL8Q": '&',
    "oJwa60": ' ',
    "hnGwq5": '/',
    "WDigwg": '.',
    "m3zziu": ':',
    "VRfbjC": '=',
    "J6u1mM": '!',
    "QjpC4K": '_'
}

# Number replacements
number_replacements = {
    "c9h4n": '1',
    "yasJb": '2',
    "QDEMu": '3',
    "VnBsl": '4',
    "uji6t": '5',
    "QafiD": '6',
    "ip7o3": '7',
    "ZIxmO": '8',
    "sAbZG": '9',
    "Gv2usn": '0'
}

# Letter replacements (uppercase)
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
