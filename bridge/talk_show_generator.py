"""
Talk Show Scene Generator

Creates a still image of a talk show setting using pixel substrate concepts.

Characters:
1. Host - Stoic and serious
2. Panelist - Superhero who helps people help themselves
3. Tuna - A marlin living in a fishbowl
4. Petunia Cartfight - Nerdy guest with an eye for the host
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Image dimensions
WIDTH = 1920
HEIGHT = 1080

# Colors
BACKGROUND = (20, 30, 50)  # Dark blue studio background
DESK_COLOR = (80, 60, 40)  # Wood desk
FLOOR_COLOR = (40, 40, 45)  # Dark floor

# Character colors (simplified for now)
HOST_SUIT = (30, 30, 35)  # Dark suit
SUPERHERO_COSTUME = (200, 50, 50)  # Red costume
TUNA_COLOR = (100, 150, 200)  # Blue marlin
PETUNIA_OUTFIT = (150, 100, 150)  # Purple nerdy outfit

def create_talk_show_scene():
    """Create the talk show scene."""
    
    # Create image
    img = Image.new('RGB', (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(img)
    
    # Draw floor
    draw.rectangle([(0, HEIGHT * 0.7), (WIDTH, HEIGHT)], fill=FLOOR_COLOR)
    
    # Draw desk
    desk_y = HEIGHT * 0.6
    desk_height = HEIGHT * 0.15
    draw.rectangle([(0, desk_y), (WIDTH, desk_y + desk_height)], fill=DESK_COLOR)
    
    # Draw desk highlights (wood grain effect)
    for i in range(5):
        y = desk_y + i * 20
        lighter = tuple(min(c + 10, 255) for c in DESK_COLOR)
        draw.line([(0, y), (WIDTH, y)], fill=lighter, width=2)
    
    # Character positions (x, y for center of head)
    host_pos = (WIDTH * 0.25, HEIGHT * 0.4)
    superhero_pos = (WIDTH * 0.5, HEIGHT * 0.45)
    tuna_pos = (WIDTH * 0.7, HEIGHT * 0.5)  # In fishbowl on desk
    petunia_pos = (WIDTH * 0.85, HEIGHT * 0.42)
    
    # Draw HOST (stoic and serious)
    draw_host(draw, host_pos)
    
    # Draw SUPERHERO PANELIST
    draw_superhero(draw, superhero_pos)
    
    # Draw TUNA (marlin in fishbowl)
    draw_tuna_in_fishbowl(draw, tuna_pos)
    
    # Draw PETUNIA (nerdy guest)
    draw_petunia(draw, petunia_pos)
    
    # Add labels
    try:
        # Try to use a font, fall back to default if not available
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Character labels
    draw.text((host_pos[0] - 30, HEIGHT * 0.85), "HOST", fill=(255, 255, 255), font=font)
    draw.text((superhero_pos[0] - 60, HEIGHT * 0.85), "SUPERHERO", fill=(255, 255, 255), font=font)
    draw.text((tuna_pos[0] - 30, HEIGHT * 0.85), "TUNA", fill=(255, 255, 255), font=font)
    draw.text((petunia_pos[0] - 50, HEIGHT * 0.85), "PETUNIA", fill=(255, 255, 255), font=font)
    
    # Title
    try:
        title_font = ImageFont.truetype("arial.ttf", 48)
    except:
        title_font = font
    
    draw.text((WIDTH // 2 - 200, 50), "THE TALK SHOW", fill=(255, 200, 100), font=title_font)
    
    return img

def draw_host(draw, pos):
    """Draw the stoic, serious host."""
    x, y = int(pos[0]), int(pos[1])
    
    # Head (stern expression)
    draw.ellipse([(x-40, y-50), (x+40, y+30)], fill=(220, 180, 150), outline=(0, 0, 0), width=2)
    
    # Eyes (serious, narrow)
    draw.ellipse([(x-25, y-20), (x-15, y-10)], fill=(50, 50, 50))
    draw.ellipse([(x+15, y-20), (x+25, y-10)], fill=(50, 50, 50))
    
    # Mouth (straight line - stoic)
    draw.line([(x-20, y+10), (x+20, y+10)], fill=(100, 50, 50), width=3)
    
    # Suit
    draw.rectangle([(x-50, y+30), (x+50, y+150)], fill=HOST_SUIT, outline=(0, 0, 0), width=2)
    
    # Tie
    draw.polygon([(x-10, y+40), (x+10, y+40), (x+5, y+100), (x-5, y+100)], fill=(150, 0, 0))

def draw_superhero(draw, pos):
    """Draw the superhero panelist."""
    x, y = int(pos[0]), int(pos[1])
    
    # Head
    draw.ellipse([(x-35, y-45), (x+35, y+25)], fill=(220, 180, 150), outline=(0, 0, 0), width=2)
    
    # Mask
    draw.ellipse([(x-30, y-25), (x+30, y-5)], fill=(0, 0, 0))
    
    # Eyes (confident)
    draw.ellipse([(x-20, y-18), (x-10, y-8)], fill=(255, 255, 255))
    draw.ellipse([(x+10, y-18), (x+20, y-8)], fill=(255, 255, 255))
    draw.ellipse([(x-17, y-15), (x-13, y-11)], fill=(0, 100, 200))
    draw.ellipse([(x+13, y-15), (x+17, y-11)], fill=(0, 100, 200))
    
    # Smile (helpful)
    draw.arc([(x-15, y), (x+15, y+20)], 0, 180, fill=(100, 50, 50), width=3)
    
    # Costume with cape
    draw.rectangle([(x-45, y+25), (x+45, y+140)], fill=SUPERHERO_COSTUME, outline=(0, 0, 0), width=2)
    
    # Cape
    draw.polygon([(x-45, y+30), (x-80, y+40), (x-70, y+120), (x-45, y+100)], fill=(200, 0, 0))
    draw.polygon([(x+45, y+30), (x+80, y+40), (x+70, y+120), (x+45, y+100)], fill=(200, 0, 0))
    
    # Emblem (helping hand)
    draw.ellipse([(x-15, y+60), (x+15, y+90)], fill=(255, 200, 0), outline=(0, 0, 0), width=2)
    draw.text((x-8, y+65), "H", fill=(200, 0, 0))

def draw_tuna_in_fishbowl(draw, pos):
    """Draw Tuna the marlin in a fishbowl."""
    x, y = int(pos[0]), int(pos[1])
    
    # Fishbowl
    draw.ellipse([(x-60, y-40), (x+60, y+80)], fill=(150, 200, 255, 100), outline=(100, 150, 200), width=3)
    
    # Water line
    draw.line([(x-55, y+20), (x+55, y+20)], fill=(100, 150, 200), width=2)
    
    # Tuna (marlin) body
    draw.ellipse([(x-40, y-10), (x+30, y+30)], fill=TUNA_COLOR, outline=(0, 0, 0), width=2)
    
    # Marlin bill (long nose)
    draw.polygon([(x+30, y+10), (x+55, y+8), (x+55, y+12), (x+30, y+10)], fill=(80, 120, 160))
    
    # Eye
    draw.ellipse([(x+10, y+5), (x+20, y+15)], fill=(255, 255, 255))
    draw.ellipse([(x+13, y+8), (x+17, y+12)], fill=(0, 0, 0))
    
    # Fins
    draw.polygon([(x-10, y), (x-20, y-15), (x-5, y+5)], fill=(80, 120, 160))
    draw.polygon([(x, y+30), (x-10, y+45), (x+10, y+35)], fill=(80, 120, 160))
    
    # Bubbles
    for bx, by in [(x-30, y-20), (x-10, y-30), (x+20, y-25)]:
        draw.ellipse([(bx-3, by-3), (bx+3, by+3)], outline=(200, 230, 255), width=1)

def draw_petunia(draw, pos):
    """Draw Petunia Cartfight (nerdy, has an eye for the host)."""
    x, y = int(pos[0]), int(pos[1])
    
    # Head
    draw.ellipse([(x-38, y-48), (x+38, y+28)], fill=(220, 180, 150), outline=(0, 0, 0), width=2)
    
    # Glasses (nerdy)
    draw.ellipse([(x-28, y-22), (x-12, y-8)], outline=(0, 0, 0), width=3)
    draw.ellipse([(x+12, y-22), (x+28, y-8)], outline=(0, 0, 0), width=3)
    draw.line([(x-12, y-15), (x+12, y-15)], fill=(0, 0, 0), width=3)
    
    # Eyes (looking left toward host, with hearts)
    draw.ellipse([(x-24, y-18), (x-16, y-12)], fill=(100, 50, 50))
    draw.ellipse([(x+16, y-18), (x+24, y-12)], fill=(100, 50, 50))
    
    # Heart eyes effect
    draw.text((x-30, y-35), "♥", fill=(255, 100, 150))
    draw.text((x+20, y-35), "♥", fill=(255, 100, 150))
    
    # Smile (smitten)
    draw.arc([(x-18, y+2), (x+18, y+22)], 0, 180, fill=(200, 100, 100), width=3)
    
    # Hair (messy, nerdy)
    for hx in range(x-35, x+35, 10):
        draw.line([(hx, y-48), (hx-5, y-60)], fill=(100, 60, 20), width=4)
    
    # Outfit (purple, nerdy)
    draw.rectangle([(x-48, y+28), (x+48, y+145)], fill=PETUNIA_OUTFIT, outline=(0, 0, 0), width=2)
    
    # Book in hand (nerdy prop)
    draw.rectangle([(x-60, y+80), (x-40, y+110)], fill=(150, 100, 50), outline=(0, 0, 0), width=2)

if __name__ == "__main__":
    print("Generating talk show scene...")
    img = create_talk_show_scene()
    
    # Save
    output_path = "talk_show_scene.png"
    img.save(output_path)
    print(f"✅ Talk show scene saved to: {output_path}")
    print(f"   Size: {WIDTH}x{HEIGHT}")
    print(f"   Characters: Host, Superhero, Tuna (marlin), Petunia Cartfight")

