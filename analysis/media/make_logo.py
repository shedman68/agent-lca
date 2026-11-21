"""
Logo and 600x600 thumbnail for the submission (Hakim's proposal; submission/ is Rashed's, so these go to analysis/media/).

  analysis/media/logo-512.png        logo mark + wordmark, transparent background
  analysis/media/thumbnail-600.png   600x600 thumbnail: logo + the package result

Colours follow the app (dark green #1f6b45 on off-white #f6f5f0). Numbers are the package result from
measures/package_summary.csv (read here, not typed). Change TITLE if the team vote picks another name.
Usage: python analysis/media/make_logo.py
"""
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
TITLE, SUB = "GreenOps Basel", "CO2 first, francs on top"
GREEN, DARK, LIGHT, BG, INK = (31, 107, 69), (18, 64, 41), (198, 226, 208), (246, 245, 240), (28, 28, 26)
FONTS = Path("C:/Windows/Fonts")
font = lambda name, size: ImageFont.truetype(str(FONTS / name), size)
BOLD, REG = "segoeuib.ttf", "segoeui.ttf"

s = pd.read_csv(ROOT / "measures/package_summary.csv")
s = s.set_index(s.columns[0]).iloc[:, 0]
co2, chf, pdays = float(s["co2_pct_mid"]), float(s["chf_pct"]), float(s["effort_pd"])


def mark(size: int) -> Image.Image:
    """Ring (like the package gauge, filled to the CO2 cut) with a leaf inside."""
    k = 4                                              # supersample for smooth edges
    S = size * k
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = int(S * 0.09)
    box = [w // 2, w // 2, S - w // 2, S - w // 2]
    d.ellipse(box, outline=LIGHT, width=w)
    d.arc(box, start=-90, end=-90 + 360 * co2 / 100, fill=GREEN, width=w)   # 43 % of the circle
    # leaf: two arcs as a lens shape, tilted, with a midrib
    leaf = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ld = ImageDraw.Draw(leaf)
    c, h = S / 2, S * 0.27                             # half-length of the leaf
    R = h * 1.6                                        # radius of the two circles; their overlap is a pointed leaf
    off = (R ** 2 - h ** 2) ** 0.5
    m1 = Image.new("L", (S, S), 0); ImageDraw.Draw(m1).ellipse([c - off - R, c - R, c - off + R, c + R], fill=255)
    m2 = Image.new("L", (S, S), 0); ImageDraw.Draw(m2).ellipse([c + off - R, c - R, c + off + R, c + R], fill=255)
    from PIL import ImageChops
    leaf.paste(GREEN + (255,), (0, 0), ImageChops.multiply(m1, m2))
    ld.line([(c, c - h * 0.8), (c, c + h * 1.15)], fill=BG, width=max(2, int(S * 0.016)))
    leaf = leaf.rotate(-35, resample=Image.BICUBIC, center=(c, c))
    im.alpha_composite(leaf)
    return im.resize((size, size), Image.LANCZOS)


def centered(d, y, text, f, fill, W):
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
    d.text(((W - (x1 - x0)) / 2 - x0, y), text, font=f, fill=fill)


# logo 512: mark + wordmark under it
L = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
L.alpha_composite(mark(300), (106, 30))
d = ImageDraw.Draw(L)
centered(d, 350, TITLE, font(BOLD, 54), DARK, 512)
centered(d, 425, SUB, font(REG, 26), GREEN, 512)
L.save(ROOT / "analysis/media/logo-512.png")

# thumbnail 600
T = Image.new("RGBA", (600, 600), BG + (255,))
T.alpha_composite(mark(250), (175, 48))
d = ImageDraw.Draw(T)
centered(d, 318, TITLE, font(BOLD, 58), DARK, 600)
centered(d, 398, "A safe CO2 package for a Basel SME", font(REG, 27), INK, 600)
d.rounded_rectangle([40, 462, 560, 540], radius=18, fill=GREEN)
centered(d, 481, f"CO2 −{co2:.0f} %  ·  cost −{chf:.1f} %  ·  {pdays:g} PD", font(BOLD, 27), (255, 255, 255), 600)
T.convert("RGB").save(ROOT / "analysis/media/thumbnail-600.png")
print("wrote logo-512.png and thumbnail-600.png;", f"CO2 -{co2} %, cost -{chf} %, {pdays} PD from measures/package_summary.csv")
