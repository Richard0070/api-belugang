from PIL import Image, ImageDraw

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
