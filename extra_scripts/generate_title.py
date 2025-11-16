"""
Script to generate a pixelated RPG-style title image for the game.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_pixelated_title():
    """Create a pixelated RPG-style title image."""
    
    # Image dimensions
    width = 800
    height = 200
    
    # Create a new image with transparent background
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Title text
    title_text = "Echoes of Lyra"
    
    # Try to use a bold system font, fallback to default
    font_size = 80
    try:
        # Try to find a bold monospace or pixel-like font
        font = ImageFont.truetype("CascadiaMono.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("Arial Bold.ttf", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
    
    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), title_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate position to center the text
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw white text only (no shadows or outlines for pixel-perfect transparency)
    draw.text((x, y), title_text, fill=(255, 255, 255, 255), font=font)
    
    # Apply pixelation effect
    # Resize down then back up for pixelated look
    pixel_size = 2
    small_width = width // pixel_size
    small_height = height // pixel_size
    
    # Resize down
    img_small = img.resize((small_width, small_height), Image.NEAREST)
    # Resize back up
    img_pixelated = img_small.resize((width, height), Image.NEAREST)
    
    # Create assets directory if it doesn't exist
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    # Save the image
    output_path = os.path.join(assets_dir, "title.png")
    img_pixelated.save(output_path)
    print(f"Title image created: {output_path}")
    print(f"Image dimensions: {width}x{height} pixels")

if __name__ == "__main__":
    create_pixelated_title()
