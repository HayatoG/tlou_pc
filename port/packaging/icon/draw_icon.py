"""Draws packaging/icon/tlou-icon-1024.png: original art made for this port (an overgrown ruined
skyline at dusk with fireflies), no game artwork. Needs Pillow. usage: draw_icon.py [out.png]
Then packaging/windows/make_icon.py launcher/tlou.ico launcher/tlou.png."""
import math, random, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

N = 1024


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / 'tlou-icon-1024.png'
    random.seed(1111)
    img = Image.new('RGBA', (N, N))
    d = ImageDraw.Draw(img)
    for y in range(N):
        t = y / N
        d.line([(0, y), (N, y)], fill=(int(255 * (1 - t) + 70 * t), int(170 * (1 - t) + 42 * t), int(90 * (1 - t) + 60 * t), 255))
    glow = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for rad in range(300, 0, -4):
        gd.ellipse([560 - rad, 520 - rad, 560 + rad, 520 + rad], fill=(255, 225, 160, int(120 * (1 - rad / 300) ** 1.6)))
    img = Image.alpha_composite(img, glow)
    d = ImageDraw.Draw(img)

    def tower(x, w, h, col, winc, overgrow):
        top = N - h
        pts = [(x, N), (x, top + random.randint(0, 30))]
        for i in range(1, 5):
            pts.append((x + w * i / 5, top + random.choice([0, 0, random.randint(10, int(h * 0.2))])))
        pts += [(x + w, top + random.randint(0, 40)), (x + w, N)]
        d.polygon(pts, fill=col)
        for wy in range(int(top + 40), N - 60, 38):
            for wx in range(int(x + 14), int(x + w - 18), 28):
                if random.random() < 0.6:
                    d.rectangle([wx, wy, wx + 11, wy + 18], fill=winc)
        for _ in range(overgrow):  # moss climbing the facade
            vx = x + random.randint(0, w)
            vy = random.randint(top + int(h * 0.3), N)
            rr = random.randint(8, 20)
            d.ellipse([vx - rr, vy - rr, vx + rr, vy + rr], fill=random.choice([(52, 98, 56, 255), (70, 120, 62, 255), (40, 80, 46, 255)]))
        for _ in range(overgrow // 12):  # hanging vines
            vx = x + random.randint(4, w - 4)
            vy = top + random.randint(0, 40)
            for k in range(0, random.randint(80, int(h * 0.6)), 2):
                d.ellipse([vx + math.sin(k / 11) * 5 - 3, vy + k - 3, vx + math.sin(k / 11) * 5 + 3, vy + k + 3], fill=(58, 110, 58, 255))

    x = -30
    while x < N:
        w = random.randint(80, 140)
        tower(x, w, random.randint(420, 700), (120, 78, 74, 255), (150, 98, 88, 255), 25)
        x += w + random.randint(10, 30)
    x = -50
    while x < N:
        w = random.randint(140, 230)
        tower(x, w, random.randint(300, 560), (46, 34, 42, 255), (70, 52, 58, 255), 90)
        x += w + random.randint(-10, 10)
    for _ in range(1600):
        gx = random.randint(0, N)
        d.line([(gx, N), (gx + random.randint(-14, 14), N - random.randint(30, 110))],
               fill=random.choice([(34, 70, 40, 255), (46, 90, 48, 255)]), width=4)
    fl = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fl)
    for _ in range(30):  # fireflies
        fx, fy, s = random.randint(80, N - 80), random.randint(N - 520, N - 120), random.randint(6, 11)
        for rad in range(s * 5, 0, -2):
            fd.ellipse([fx - rad, fy - rad, fx + rad, fy + rad], fill=(255, 240, 150, int(200 * (1 - rad / (s * 5)) ** 2)))
    img = Image.alpha_composite(img, fl.filter(ImageFilter.GaussianBlur(1.5)))
    v = Image.new('L', (N, N), 0)
    ImageDraw.Draw(v).rounded_rectangle([90, 90, N - 90, N - 90], radius=200, fill=255)
    img = Image.composite(img, Image.new('RGBA', (N, N), (10, 6, 8, 255)), v.filter(ImageFilter.GaussianBlur(70)))
    mask = Image.new('L', (N, N), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, N - 1, N - 1], radius=180, fill=255)
    img.putalpha(mask)
    img.save(out)


if __name__ == '__main__':
    main()
