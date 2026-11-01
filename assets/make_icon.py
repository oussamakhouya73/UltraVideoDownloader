"""Generates the app icon (run: python assets/make_icon.py). Needs Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw

out = Path(__file__).resolve().parent
S = 2048
u = S / 1024
blue, chalk, saffron = (43, 53, 209, 255), (246, 247, 251, 255), (247, 181, 0, 255)

img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle((0, 0, S - 1, S - 1), radius=int(S * 0.22), fill=blue)
# download arrow: stem + head, then a saffron tray line under it
d.rounded_rectangle((436 * u, 196 * u, 588 * u, 560 * u), radius=28 * u, fill=chalk)
d.polygon([(268 * u, 488 * u), (756 * u, 488 * u), (512 * u, 770 * u)], fill=chalk)
d.rounded_rectangle((226 * u, 812 * u, 798 * u, 890 * u), radius=39 * u, fill=saffron)

def size(n):
    return img.resize((n, n), Image.LANCZOS)

size(512).save(out / "icon.png")
size(180).save(out / "icon-180.png")
size(64).save(out / "icon-64.png")
size(256).save(out / "icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("icons written to", out)
