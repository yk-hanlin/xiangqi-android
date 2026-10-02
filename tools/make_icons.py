# -*- coding: utf-8 -*-
"""生成中国象棋 App 图标（无需外部素材）。

用法：
    <venv-python> tools/make_icons.py

产出（写入 ../www/icons/）：
    icon-foreground.png  1024  透明背景前景图（Adaptive Icon 用）
    icon-background.png  1024  纯色背景图（Adaptive Icon 用）
    icon.png             1024  完整方形图标（Capacitor/PWA 源图）
    icon-192.png          192  PWA
    icon-512.png          512  PWA
    maskable-512.png      512  PWA maskable（内容内缩到安全区）
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'www', 'icons')
OUT = os.path.normpath(OUT)
os.makedirs(OUT, exist_ok=True)

SIZE = 1024
BG_TOP = (141, 94, 47)      # 木质深棕
BG_BOTTOM = (96, 58, 26)
PIECE_FILL = (253, 249, 238)
PIECE_EDGE = (176, 42, 31)  # 棋子红边 + 红字
GOLD = (198, 156, 84)

FONTS = [
    r'C:\Windows\Fonts\msyhbd.ttc',   # 微软雅黑 Bold
    r'C:\Windows\Fonts\simhei.ttf',   # 黑体
    r'C:\Windows\Fonts\simkai.ttf',   # 楷体
    r'C:\Windows\Fonts\simsun.ttc',
]


def load_font(px):
    for f in FONTS:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, px)
            except Exception:
                continue
    return ImageFont.load_default()


def rounded_bg(size, radius_ratio=0.22):
    """绘制圆角渐变背景"""
    r = int(size * radius_ratio)
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=BG_TOP)
    # 竖向渐变（逐行混合）
    top = Image.new('RGBA', (size, size), BG_TOP + (255,))
    bot = Image.new('RGBA', (size, size), BG_BOTTOM + (255,))
    grad = Image.new('RGBA', (size, size))
    gd = ImageDraw.Draw(grad)
    band = 8
    for y in range(0, size, band):
        t = y / float(size - 1)
        col = tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3)) + (255,)
        gd.rectangle([0, y, size - 1, min(y + band, size - 1)], fill=col)
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=255)
    img.paste(grad, (0, 0), mask)

    # 内描边，增强边界感
    d2 = ImageDraw.Draw(img)
    d2.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, outline=(255, 255, 255, 40), width=max(2, size // 170))
    return img


def draw_piece(size, glyph='帥'):
    """绘制一枚象棋棋子（透明背景正方形，边长 = size）"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = size / 2.0
    r_out = size * 0.44
    pad = max(2, int(size * 0.012))

    # 阴影
    d.ellipse([cx - r_out * 0.99, cy - r_out * 0.93, cx + r_out * 0.99, cy + r_out * 1.05],
              fill=(40, 22, 8, 90))
    # 棋子本体
    d.ellipse([cx - r_out, cy - r_out, cx + r_out, cy + r_out], fill=PIECE_FILL + (255,))
    # 金色外环 + 红色双圈
    d.ellipse([cx - r_out, cy - r_out, cx + r_out, cy + r_out], outline=GOLD + (255,), width=max(3, int(size * 0.022)))
    d.ellipse([cx - r_out * 0.86, cy - r_out * 0.86, cx + r_out * 0.86, cy + r_out * 0.86],
              outline=PIECE_EDGE + (255,), width=max(3, int(size * 0.028)))
    d.ellipse([cx - r_out * 0.74, cy - r_out * 0.74, cx + r_out * 0.74, cy + r_out * 0.74],
              outline=PIECE_EDGE + (150,), width=max(1, int(size * 0.012)))

    font = load_font(int(size * 0.62))
    # 文字垂直居中（用 bounding box 校正）
    tmp = ImageDraw.Draw(img)
    bbox = tmp.textbbox((0, 0), glyph, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    d.text((cx - w / 2.0 - bbox[0], cy - h / 2.0 - bbox[1] - size * 0.01), glyph, font=font, fill=PIECE_EDGE + (255,))
    return img


def compose(size, mode):
    if mode == 'foreground':
        canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        piece = draw_piece(int(size * 0.66))
        canvas.paste(piece, ((size - piece.width) // 2, (size - piece.height) // 2), piece)
        return canvas
    if mode == 'background':
        return Image.new('RGBA', (size, size), BG_TOP + (255,))
    if mode == 'full':
        bg = rounded_bg(size)
        piece = draw_piece(int(size * 0.60))
        bg.paste(piece, ((size - piece.width) // 2, int(size * 0.20)), piece)
        return bg
    if mode == 'maskable':
        bg = Image.new('RGBA', (size, size), BG_TOP + (255,))
        bd = ImageDraw.Draw(bg)
        for y in range(0, size, 8):
            t = y / float(size - 1)
            bd.rectangle([0, y, size - 1, min(y + 8, size - 1)],
                         fill=tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3)) + (255,))
        piece = draw_piece(int(size * 0.46))  # 缩到安全区（maskable 会裁掉边缘）
        bg.paste(piece, ((size - piece.width) // 2, (size - piece.height) // 2), piece)
        return bg
    raise ValueError(mode)


def save(img, name):
    path = os.path.join(OUT, name)
    img.save(path, 'PNG', optimize=True)
    print('  写出 %-24s %dx%d  %.1f KB' % (name, img.width, img.height, os.path.getsize(path) / 1024.0))


def main():
    print('图标输出目录：' + OUT)
    fg = compose(SIZE, 'foreground')
    bg = compose(SIZE, 'background')
    full = compose(SIZE, 'full')
    mask = compose(SIZE, 'maskable')

    save(fg, 'icon-foreground.png')
    save(bg, 'icon-background.png')
    save(full, 'icon.png')
    save(full.resize((192, 192), Image.LANCZOS), 'icon-192.png')
    save(full.resize((512, 512), Image.LANCZOS), 'icon-512.png')
    save(mask.resize((512, 512), Image.LANCZOS), 'maskable-512.png')
    print('完成。')


if __name__ == '__main__':
    main()
