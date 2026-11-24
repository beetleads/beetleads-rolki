#!/usr/bin/env python3
"""render.py <katalog_rolki> [--podglad]  -> final.mp4 (obraz + dźwięk z mix.wav)"""
import sys, os, json, subprocess
from playwright.sync_api import sync_playwright

d = os.path.abspath(sys.argv[1]); prev = '--podglad' in sys.argv
data = json.loads(open(f'{d}/data.js').read()[len('window.DATA='):-1])
FPS = 30; end = data['end']; n = int(end * FPS)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--disable-gpu', '--allow-file-access-from-files'])
    pg = b.new_page(viewport={'width': 1080, 'height': 1920})
    pg.goto(f'file://{d}/gen.html'); pg.wait_for_timeout(800)
    if prev:
        os.makedirs(f'{d}/podglad', exist_ok=True)
        for t in [0.0, 0.6] + [s['s'] + 0.9 for s in data['scenes']] + [data['ctaS'] + 0.7, data['ctaS'] + 1.8]:
            pg.evaluate(f'render({t})'); pg.screenshot(path=f'{d}/podglad/t{t:05.2f}.jpg', type='jpeg', quality=80)
        sys.exit(0)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'image2pipe', '-framerate', str(FPS), '-i', '-',
                           '-i', f'{d}/mix.wav', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
                           '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', f'{d}/final.mp4'], stdin=subprocess.PIPE)
    for i in range(n):
        pg.evaluate(f'render({i / FPS})')
        ff.stdin.write(pg.screenshot(type='jpeg', quality=90))
    ff.stdin.close(); ff.wait(); b.close()
print('ok', d)
