"""Original app icon: an isometric locomotive and tender on a block of land.

Drawn in a 2:1 isometric projection at 1024 px and scaled down for smooth edges.
Usage: python3 make_icon.py OUT_DIR SIZE [SIZE ...]
"""
import math
import sys
from PIL import Image, ImageDraw, ImageFilter

S = 1024
A = 70            # pixels per world unit along the iso axes
CX, CY = 640, 640  # screen position of world origin


def iso(x, y, z=0.0):
    return (CX + (x - y) * A, CY + (x + y) * A / 2 - z * A)


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def poly(d, pts, fill, outline=None):
    d.polygon([iso(*p) for p in pts], fill=fill, outline=outline)


def box(d, x0, y0, z0, lx, ly, lz, col, top=1.12, left=0.78, right=0.58):
    """Axis-aligned box; we see the top, the +y face (front-left) and the +x face (front-right)."""
    x1, y1, z1 = x0 + lx, y0 + ly, z0 + lz
    poly(d, [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], shade(col, left))
    poly(d, [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], shade(col, right))
    poly(d, [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], shade(col, top))


def cylinder_x(d, x0, x1, yc, zc, r, col, n=28, cap=True):
    """Cylinder lying along x (a boiler): drawn as its visible half plus the front end cap."""
    # visible part of the round surface: from underneath (t = -90 deg) over the front (+y, t = 0)
    # and the top (t = 90 deg) to the back edge (t = 135 deg); y = r cos t, z = r sin t
    t_start, t_span = -math.pi / 2, math.pi * 1.25
    for i in range(n):
        t0 = t_start + t_span * i / n
        t1 = t_start + t_span * (i + 1) / n
        tm = (t0 + t1) / 2
        f = 0.55 + 0.6 * max(0.0, math.sin(tm + 0.5))   # lit from above, slightly front
        pts = [(x0, yc + r * math.cos(t0), zc + r * math.sin(t0)), (x1, yc + r * math.cos(t0), zc + r * math.sin(t0)),
               (x1, yc + r * math.cos(t1), zc + r * math.sin(t1)), (x0, yc + r * math.cos(t1), zc + r * math.sin(t1))]
        poly(d, pts, shade(col, f))
    if not cap:
        return
    # front end cap (x = x1 face)
    cap = [(x1, yc + r * math.cos(t), zc + r * math.sin(t)) for t in [2 * math.pi * i / 36 for i in range(36)]]
    poly(d, cap, shade(col, 0.5))


def wheel(d, xc, y, zc, r, rim, hub):
    pts = [(xc + r * math.cos(t), y, zc + r * math.sin(t)) for t in [2 * math.pi * i / 32 for i in range(32)]]
    poly(d, pts, rim)
    r2 = r * 0.72
    pts = [(xc + r2 * math.cos(t), y, zc + r2 * math.sin(t)) for t in [2 * math.pi * i / 32 for i in range(32)]]
    poly(d, pts, shade(rim, 1.6))
    r3 = r * 0.22
    pts = [(xc + r3 * math.cos(t), y, zc + r3 * math.sin(t)) for t in [2 * math.pi * i / 16 for i in range(16)]]
    poly(d, pts, hub)


def draw():
    im = Image.new('RGB', (S, S))
    d = ImageDraw.Draw(im)
    # evening sky gradient
    for y in range(S):
        t = y / S
        d.line([(0, y), (S, y)], fill=(int(46 + 60 * t), int(70 + 62 * t), int(96 + 40 * t)))

    # land block (grass top, earth sides)
    G0, G1 = -8.0, 8.0
    grass, earth = (92, 128, 60), (120, 92, 62)
    box(d, G0, G0, -1.6, G1 - G0, G1 - G0, 1.6, earth, top=1.0, left=0.85, right=0.62)
    poly(d, [(G0, G0, 0), (G1, G0, 0), (G1, G1, 0), (G0, G1, 0)], grass)
    # subtle tile grid like a map
    for k in range(int(G0), int(G1) + 1, 2):
        d.line([iso(k, G0, 0), iso(k, G1, 0)], fill=shade(grass, 0.93), width=2)
        d.line([iso(G0, k, 0), iso(G1, k, 0)], fill=shade(grass, 0.93), width=2)

    # a few trees (simple cones) behind the line
    for (tx, ty) in [(-4.0, -3.4), (-2.2, -4.2), (2.6, -3.0), (-6.8, 2.4), (4.6, 2.6)]:
        d.ellipse([*map(int, (iso(tx, ty)[0] - 24, iso(tx, ty)[1] - 10)), *map(int, (iso(tx, ty)[0] + 24, iso(tx, ty)[1] + 10))], fill=shade(grass, 0.7))
        base = iso(tx, ty, 0.3)
        top_ = iso(tx, ty, 2.6)
        d.polygon([(base[0] - 46, base[1]), (base[0] + 46, base[1]), top_], fill=(54, 92, 50))
        d.polygon([(base[0], base[1] + 2), (base[0] + 46, base[1]), top_], fill=(40, 72, 40))

    # ballast bed and track along x at y in [-0.9, 0.9]
    yb0, yb1 = -1.0, 1.0
    poly(d, [(G0, yb0, 0.02), (G1, yb0, 0.02), (G1, yb1, 0.02), (G0, yb1, 0.02)], (138, 128, 114))
    for k in range(int(G0 * 2), int(G1 * 2)):
        x = k / 2 + 0.1
        poly(d, [(x, -0.85, 0.05), (x + 0.22, -0.85, 0.05), (x + 0.22, 0.85, 0.05), (x, 0.85, 0.05)], (92, 70, 50))
    for yr in (-0.5, 0.5):
        poly(d, [(G0, yr - 0.06, 0.1), (G1, yr - 0.06, 0.1), (G1, yr + 0.06, 0.1), (G0, yr + 0.06, 0.1)], (200, 200, 206))

    # ---- locomotive (front towards +x) and tender
    GREEN, BLACK, RED, BRASS = (34, 84, 60), (34, 34, 38), (150, 36, 30), (196, 156, 72)
    # tender
    box(d, -5.6, -0.75, 0.55, 2.6, 1.5, 1.3, GREEN)
    box(d, -5.45, -0.6, 1.85, 2.3, 1.2, 0.18, (40, 36, 34))   # coal
    # frame / running plate
    box(d, -2.8, -0.78, 0.5, 6.3, 1.56, 0.28, BLACK)
    box(d, 3.5, -0.85, 0.42, 0.2, 1.7, 0.42, RED)               # buffer beam
    # cab
    box(d, -2.8, -0.78, 0.78, 1.7, 1.56, 1.7, GREEN)
    box(d, -2.95, -0.88, 2.48, 2.0, 1.76, 0.14, BLACK)          # roof
    # cab window on the front-left face
    poly(d, [(-2.55, 0.781, 1.55), (-1.6, 0.781, 1.55), (-1.6, 0.781, 2.2), (-2.55, 0.781, 2.2)], (232, 206, 120))
    # boiler + smokebox
    cylinder_x(d, -1.1, 2.4, 0.0, 1.45, 0.62, GREEN)
    cylinder_x(d, 2.4, 3.3, 0.0, 1.45, 0.64, BLACK)
    for bx in (0.0, 1.3):                                        # brass bands
        cylinder_x(d, bx, bx + 0.12, 0.0, 1.45, 0.635, BRASS, n=20, cap=False)
    # dome and chimney
    box(d, 0.45, -0.25, 1.95, 0.55, 0.5, 0.45, BRASS)
    box(d, 2.65, -0.2, 2.0, 0.4, 0.4, 0.75, BLACK)
    # wheels on the visible (+y) side
    for xc in (-0.6, 0.9, 2.4):
        wheel(d, xc, 0.8, 0.6, 0.55, (24, 24, 26), RED)
    for xc in (-4.9, -3.7):
        wheel(d, xc, 0.76, 0.42, 0.38, (24, 24, 26), RED)
    # coupling rod
    poly(d, [(-0.6, 0.83, 0.52), (2.4, 0.83, 0.52), (2.4, 0.83, 0.64), (-0.6, 0.83, 0.64)], (168, 168, 176))

    # light smoke drifting back
    smoke = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(smoke)
    px, py = iso(2.85, 0.0, 3.0)
    for i, (dx, dy, r, a) in enumerate([(0, -10, 50, 175), (-90, -70, 66, 140), (-210, -110, 80, 100), (-360, -130, 88, 60)]):
        sd.ellipse([px + dx - r, py + dy - r, px + dx + r, py + dy + r], fill=(230, 230, 232, a))
    smoke = smoke.filter(ImageFilter.GaussianBlur(14))
    im.paste(smoke, (0, 0), smoke)
    return im


if __name__ == '__main__':
    img = draw()
    for size in map(int, sys.argv[2:]):
        img.resize((size, size), Image.LANCZOS).save(f'{sys.argv[1]}/icon-{size}.png')
