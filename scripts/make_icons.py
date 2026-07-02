"""Generates PWA icons (192, 512, apple-touch 180) as plain PNGs, no deps.
Reuses the same pixel silhouette as the 'calm & buff' Beast state in index.html.
"""
import struct
import zlib
import os

COLS, ROWS = 16, 14
BODY_ROWS = [
    [(3, 4), (11, 12)],
    [(3, 5), (10, 12)],
    [(4, 11)],
    [(3, 12)],
    [(3, 12)],
    [(3, 12)],
    [(3, 12)],
    [(3, 12)],
    [(3, 12)],
    [(3, 12)],
    [(4, 11)],
    [(4, 11)],
    [(4, 5), (10, 11)],
    [(4, 5), (10, 11)],
]
ARMS = [(1, 2, 6, 7), (13, 14, 6, 7)]  # col_start,col_end,row_start,row_end
EYES = [(6, 5), (9, 5)]
MOUTH = (6, 8, 4)  # col, row, width

BODY = (61, 220, 132)     # #3ddc84
FEATURE = (10, 51, 25)    # #0a3319
BG = (20, 18, 31)         # #14121f


def build_grid():
    grid = [[BG for _ in range(COLS)] for _ in range(ROWS)]
    for row, segments in enumerate(BODY_ROWS):
        for start, end in segments:
            for c in range(start, end + 1):
                grid[row][c] = BODY
    for c0, c1, r0, r1 in ARMS:
        for r in range(r0, r1):
            for c in range(c0, c1):
                grid[r][c] = BODY
    for col, row in EYES:
        grid[row][col] = FEATURE
    mc, mr, mw = MOUTH
    for c in range(mc, mc + mw):
        grid[mr][c] = FEATURE
    grid[9][5] = FEATURE
    grid[9][10] = FEATURE
    return grid


def write_png(path, size, solid_bg=False):
    grid = build_grid()
    block = int(size * 0.8 / max(COLS, ROWS))
    grid_w, grid_h = COLS * block, ROWS * block
    off_x = (size - grid_w) // 2
    off_y = (size - grid_h) // 2

    pixels = [[BG for _ in range(size)] for _ in range(size)]
    for row in range(ROWS):
        for col in range(COLS):
            color = grid[row][col]
            if color == BG and not solid_bg:
                continue
            for y in range(block):
                py = off_y + row * block + y
                if py < 0 or py >= size:
                    continue
                for x in range(block):
                    px = off_x + col * block + x
                    if px < 0 or px >= size:
                        continue
                    pixels[py][px] = color

    raw = bytearray()
    for y in range(size):
        raw.append(0)  # filter type: none
        for x in range(size):
            r, g, b = pixels[y][x]
            raw += bytes((r, g, b, 255))

    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data +
                struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)
    idat = zlib.compress(bytes(raw), 9)
    png = sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(png)


if __name__ == '__main__':
    base = os.path.join(os.path.dirname(__file__), '..', 'icons')
    write_png(os.path.join(base, 'icon-192.png'), 192, solid_bg=True)
    write_png(os.path.join(base, 'icon-512.png'), 512, solid_bg=True)
    write_png(os.path.join(base, 'apple-touch-icon.png'), 180, solid_bg=True)
    print('Icons written to', os.path.abspath(base))
