"""Build Moritz's app icon: a lower-case Medula One "m", white on a navy rounded square.

Writes moritz/branding/moritz_icon.png (1024 px) and release/windows/icons/winblender.ico.
Run from the repository root: python moritz/branding/src/make_icon.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

S = 1024
NAVY = (11, 29, 61)
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "MedulaOne-Regular.ttf")

img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.2), fill=NAVY + (255,))

# Size the "m" to fill most of the square, centered on its ink box.
font = ImageFont.truetype(FONT, 100)
x0, y0, x1, y1 = d.textbbox((0, 0), "m", font=font)
scale = min(S * 0.70 / (x1 - x0), S * 0.62 / (y1 - y0))
font = ImageFont.truetype(FONT, int(100 * scale))
x0, y0, x1, y1 = d.textbbox((0, 0), "m", font=font)
d.text(((S - (x1 - x0)) / 2 - x0, (S - (y1 - y0)) / 2 - y0), "m", font=font, fill=(255, 255, 255, 255))

img.save("moritz/branding/moritz_icon.png")
sizes = [16, 24, 32, 48, 64, 128, 256]
img.save("release/windows/icons/winblender.ico", sizes=[(s, s) for s in sizes])
print("wrote moritz_icon.png and winblender.ico")
