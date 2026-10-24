"""Build Moritz's app icon from the "m" artwork (moritz/branding/src/icon_m.png, 512 px).

Writes moritz/branding/moritz_icon.png and release/windows/icons/winblender.ico.
Run from the repository root: python moritz/branding/src/make_icon.py
"""
import os

from PIL import Image

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon_m.png")

img = Image.open(SRC).convert("RGBA")
img.save("moritz/branding/moritz_icon.png")
sizes = [16, 24, 32, 48, 64, 128, 256]
img.save("release/windows/icons/winblender.ico", sizes=[(s, s) for s in sizes])
print("wrote moritz_icon.png and winblender.ico")
