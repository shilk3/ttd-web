# Original app icon: a steam locomotive on a track in a green landscape.
# Drawn large and downscaled for smooth edges.
import sys
from PIL import Image, ImageDraw, ImageFilter
S = 1024
def P(x, y): return (int(x * S), int(y * S))
def R(x0, y0, x1, y1): return [int(x0 * S), int(y0 * S), int(x1 * S), int(y1 * S)]

im = Image.new('RGB', (S, S))
d = ImageDraw.Draw(im)
# sky gradient
for y in range(S):
    t = y / S
    d.line([(0, y), (S, y)], fill=(int(120 + 70 * t), int(180 + 40 * t), int(235 - 10 * t)))
# distant hills
d.ellipse(R(-0.30, 0.48, 0.70, 1.10), fill=(96, 150, 70))
d.ellipse(R(0.40, 0.44, 1.40, 1.10), fill=(80, 135, 60))
# foreground grass
d.rectangle(R(0, 0.70, 1, 1), fill=(70, 120, 48))
# ballast + sleepers + rails
d.polygon([P(0, 0.80), P(1, 0.80), P(1, 0.90), P(0, 0.90)], fill=(140, 125, 105))
for i in range(-1, 14):
    x = i * 0.08 + 0.01
    d.rectangle(R(x, 0.815, x + 0.045, 0.885), fill=(96, 66, 40))
for y in (0.825, 0.865):
    d.rectangle(R(0, y - 0.008, 1, y + 0.008), fill=(205, 205, 212))

# smoke (behind the chimney, drifting back)
smoke = Image.new('RGBA', (S, S), (0, 0, 0, 0))
sd = ImageDraw.Draw(smoke)
for (cx, cy, r, a) in [(0.70, 0.20, 0.075, 235), (0.60, 0.13, 0.09, 215), (0.47, 0.09, 0.10, 190), (0.33, 0.08, 0.10, 150), (0.20, 0.09, 0.09, 110)]:
    sd.ellipse(R(cx - r, cy - r, cx + r, cy + r), fill=(245, 245, 245, a))
smoke = smoke.filter(ImageFilter.GaussianBlur(S * 0.006))
im.paste(smoke, (0, 0), smoke)
d = ImageDraw.Draw(im)

RED, RED_D = (196, 40, 32), (140, 26, 22)
GRN, GRN_D = (34, 104, 58), (22, 70, 40)
BLK, BRASS = (32, 32, 36), (226, 180, 70)

# cab (rear, left)
d.rectangle(R(0.13, 0.36, 0.38, 0.66), fill=GRN)
d.rectangle(R(0.11, 0.33, 0.40, 0.37), fill=BLK)            # roof
d.rectangle(R(0.17, 0.41, 0.31, 0.52), fill=(250, 220, 130))  # window
d.rectangle(R(0.17, 0.41, 0.31, 0.52), outline=GRN_D, width=int(S * 0.012))
# boiler
d.rounded_rectangle(R(0.36, 0.44, 0.86, 0.64), radius=int(S * 0.09), fill=GRN)
d.rectangle(R(0.36, 0.44, 0.60, 0.64), fill=GRN)
for x in (0.50, 0.66):                                         # boiler bands
    d.rectangle(R(x, 0.44, x + 0.02, 0.64), fill=BRASS)
d.ellipse(R(0.80, 0.44, 0.92, 0.64), fill=GRN_D)              # smokebox front
d.ellipse(R(0.84, 0.50, 0.89, 0.56), fill=BRASS)              # lamp
# dome + chimney
d.ellipse(R(0.53, 0.37, 0.63, 0.47), fill=BRASS)
d.rectangle(R(0.72, 0.27, 0.79, 0.45), fill=BLK)
d.rectangle(R(0.70, 0.25, 0.81, 0.29), fill=BLK)
# running board / frame
d.rectangle(R(0.11, 0.64, 0.92, 0.70), fill=RED)
d.rectangle(R(0.11, 0.69, 0.92, 0.71), fill=RED_D)
# cowcatcher / buffer beam
d.polygon([P(0.92, 0.64), P(0.97, 0.64), P(0.99, 0.79), P(0.92, 0.79)], fill=RED_D)
# wheels
def wheel(cx, r):
    cy = 0.818 - r
    d.ellipse(R(cx - r, cy - r, cx + r, cy + r), fill=RED)
    d.ellipse(R(cx - r, cy - r, cx + r, cy + r), outline=BLK, width=int(S * 0.016))
    d.ellipse(R(cx - 0.022, cy - 0.022, cx + 0.022, cy + 0.022), fill=BRASS)
    return cy
cys = [wheel(0.27, 0.095), wheel(0.50, 0.095), wheel(0.80, 0.06)]
# coupling rod across the big wheels
d.rectangle(R(0.25, cys[0] + 0.03, 0.52, cys[0] + 0.05), fill=(170, 170, 180))
# piston
d.rectangle(R(0.62, 0.66, 0.74, 0.74), fill=BLK)

for size in map(int, sys.argv[2:]):
    im.resize((size, size), Image.LANCZOS).save(f'{sys.argv[1]}/icon-{size}.png')
