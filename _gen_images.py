#!/usr/bin/env python3
"""Genere favicon (tete d'Eric, ronde) + image Open Graph 1200x630."""
from PIL import Image, ImageDraw, ImageFont
import random

VERT_FONCE = (4, 92, 44)
VERT = (0, 132, 61)
VERT_CLAIR = (43, 182, 115)
OR = (244, 180, 0)
WHITE = (255, 255, 255)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def circle_mask(size, ss=4):
    """Masque circulaire anti-aliase."""
    big = Image.new("L", (size * ss, size * ss), 0)
    ImageDraw.Draw(big).ellipse((0, 0, size * ss - 1, size * ss - 1), fill=255)
    return big.resize((size, size), Image.LANCZOS)

# ---------- FAVICON (tete ronde, fond transparent) ----------
def make_favicon():
    src = Image.open("eric.png").convert("RGB")
    base = 256
    photo = src.resize((base, base), Image.LANCZOS)
    mask = circle_mask(base)
    icon = Image.new("RGBA", (base, base), (0, 0, 0, 0))
    # anneau vert fin pour detacher du fond clair des onglets
    ring = Image.new("RGBA", (base, base), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, base - 1, base - 1), fill=VERT + (255,))
    icon = Image.composite(ring, icon, mask)
    inner_sz = base - 16
    inner = circle_mask(inner_sz)
    photo_rgba = photo.resize((inner_sz, inner_sz), Image.LANCZOS).convert("RGBA")
    off = 8
    canvas = Image.new("RGBA", (base, base), (0, 0, 0, 0))
    canvas.paste(photo_rgba, (off, off), inner)
    icon = Image.alpha_composite(icon, canvas)

    icon.resize((180, 180), Image.LANCZOS).save("apple-touch-icon.png")
    for s in (16, 32, 48):
        icon.resize((s, s), Image.LANCZOS).save(f"favicon-{s}.png")
    icon.save("favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    print("favicon OK (16/32/48/180 + ico)")

# ---------- OPEN GRAPH 1200x630 ----------
def make_og():
    W, H = 1200, 630
    bg = Image.new("RGB", (W, H))
    px = bg.load()
    for y in range(H):
        ty = y / H
        for x in range(W):
            t = (x / W) * 0.45 + ty * 0.55
            c = lerp(VERT_FONCE, VERT, t / 0.5) if t < 0.5 else lerp(VERT, VERT_CLAIR, (t - 0.5) / 0.5)
            px[x, y] = c
    draw = ImageDraw.Draw(bg, "RGBA")

    # confettis discrets
    random.seed(16)
    cols = [OR, WHITE, VERT_CLAIR, (255, 217, 102)]
    for _ in range(70):
        x = random.randint(0, W); y = random.randint(0, H)
        r = random.randint(3, 8); col = random.choice(cols)
        draw.ellipse((x, y, x + r, y + r), fill=col + (90,))

    # photo ronde a gauche, avec anneau blanc
    d = 360
    src = Image.open("eric.png").convert("RGB").resize((d, d), Image.LANCZOS)
    cx, cy = 300, H // 2
    rr = d // 2 + 9
    draw.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(255, 255, 255, 235))
    bg.paste(src, (cx - d // 2, cy - d // 2), circle_mask(d))

    # textes a droite
    f_kick = ImageFont.truetype(SANS_B, 30)
    f_name = ImageFont.truetype(SERIF, 92)
    f_age = ImageFont.truetype(SERIF, 50)
    f_par = ImageFont.truetype(SANS_B, 40)
    tx = 560

    def shadow_text(xy, txt, font, fill, anchor="lm"):
        draw.text((xy[0] + 2, xy[1] + 3), txt, font=font, fill=(0, 0, 0, 140), anchor=anchor)
        draw.text(xy, txt, font=font, fill=fill, anchor=anchor)

    kick = "JOYEUX ANNIVERSAIRE"
    shadow_text((tx, cy - 150), " ".join(kick), f_kick, OR + (255,), anchor="lm")
    shadow_text((tx, cy - 70), "Eric Viau", f_name, WHITE + (255,), anchor="lm")
    shadow_text((tx, cy + 10), "53 ans", f_age, WHITE + (255,), anchor="lm")
    shadow_text((tx, cy + 95), "— mon parrain", f_par, OR + (255,), anchor="lm")

    bg.save("og-image.png")
    print("og-image.png OK (1200x630)")

if __name__ == "__main__":
    make_favicon()
    make_og()
