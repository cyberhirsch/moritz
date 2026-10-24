"""Build Moritz's splash image (release/datafiles/splash.png, 1000x500).

Run from the repository root: python moritz/branding/src/make_splash.py
Needs Pillow and the Inter font (C:/Windows/Fonts/Inter-Regular.ttf or set INTER_TTF).
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, SS = 1000, 500, 2          # final size and supersampling
NAVY = (11, 29, 61)
LIGHT = (32, 66, 122)
LOGO = "moritz/branding/moritz_logo_white.png"
OUT = "release/datafiles/splash.png"
FONT = os.environ.get("INTER_TTF", "C:/Windows/Fonts/Inter-Regular.ttf")

w, h = W * SS, H * SS

# Background: navy, lighter toward the upper right.
bg = Image.new("RGB", (w, h), NAVY)
glow = Image.new("L", (w, h), 0)
ImageDraw.Draw(glow).ellipse([w * 0.45, -h * 0.6, w * 1.4, h * 0.9], fill=255)
glow = glow.filter(ImageFilter.GaussianBlur(220 * SS / 2))
bg = Image.composite(Image.new("RGB", (w, h), LIGHT), bg, glow)

# A viewport floor grid fading into the horizon.
grid = Image.new("L", (w, h), 0)
d = ImageDraw.Draw(grid)
horizon, cx = h * 0.56, w * 0.62
for i in range(-24, 25):
    d.line([(cx + i * w * 0.012, horizon), (cx + i * w * 0.16, h * 1.6)], fill=70, width=SS)
for k in range(1, 18):
    y = horizon + (h - horizon) * (k / 9) ** 2
    d.line([(0, y), (w, y)], fill=70, width=SS)
fade = Image.linear_gradient("L").resize((w, h))
fade = fade.point(lambda v: max(0, min(255, int((v - 0.56 * 255) * 3.2))))
grid = Image.composite(grid, Image.new("L", (w, h), 0), fade)
bg = Image.composite(Image.new("RGB", (w, h), (120, 160, 220)), bg, grid.point(lambda v: v // 3))

# Logo and credit line.
img = bg.convert("RGBA")
logo = Image.open(LOGO)
lw = int(w * 0.46)
logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
img.alpha_composite(logo, (int(w * 0.06), int(h * 0.20)))
font = ImageFont.truetype(FONT, 15 * SS)
ImageDraw.Draw(img).text((int(w * 0.06), int(h * 0.86)), "Based on Blender", font=font,
                         fill=(255, 255, 255, 150))

img.convert("RGB").resize((W, H), Image.LANCZOS).save(OUT, optimize=True)
print("wrote", OUT)
