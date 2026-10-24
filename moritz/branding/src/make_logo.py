"""Build the Moritz wordmark: "moritz" in lower-case GenEi Kiwami Gothic, navy and white, transparent.

Writes moritz/branding/moritz_logo.png and moritz_logo_white.png.
Run from the repository root: python moritz/branding/src/make_logo.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

NAVY = (11, 29, 61)
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "GenEiKiwamiGo.ttf")
OUT = "moritz/branding"

font = ImageFont.truetype(FONT, 600)
x0, y0, x1, y1 = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), "moritz", font=font)
mask = Image.new("L", (x1 - x0, y1 - y0), 0)
ImageDraw.Draw(mask).text((-x0, -y0), "moritz", font=font, fill=255)

for name, color in (("moritz_logo.png", NAVY), ("moritz_logo_white.png", (255, 255, 255))):
    logo = Image.new("RGBA", mask.size, color + (0,))
    logo.putalpha(mask)
    logo.save(os.path.join(OUT, name))
print("wrote", mask.size)
