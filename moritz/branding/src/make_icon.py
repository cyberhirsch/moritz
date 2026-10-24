"""Build Moritz's app icon from the "m" artwork (moritz/branding/src/icon_m.png, 512 px).

Writes moritz/branding/moritz_icon.png and the app and .blend file icons
(release/windows/icons/winblender.ico, winblenderfile.ico). The menu icon
(release/datafiles/icons_svg/blender.svg) is the same shape as a vector, written by hand.
Run from the repository root: python moritz/branding/src/make_icon.py
"""
import os

from PIL import Image

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon_m.png")

img = Image.open(SRC).convert("RGBA")
img.save("moritz/branding/moritz_icon.png")
sizes = [16, 24, 32, 48, 64, 128, 256]
for name in ("winblender.ico", "winblenderfile.ico"):
    img.save("release/windows/icons/" + name, sizes=[(s, s) for s in sizes])
print("wrote moritz_icon.png, winblender.ico and winblenderfile.ico")
