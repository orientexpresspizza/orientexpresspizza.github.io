"""Render an HTML file to PNG with headless Google Chrome (used for the localized posters and the campus map)."""
import os
import shutil
import subprocess
import tempfile


def chrome_bin():
    for name in ('google-chrome', 'chromium', 'chromium-browser'):
        if shutil.which(name):
            return shutil.which(name)
    raise SystemExit('Google Chrome / Chromium not found')


def shot(html_path, png_path, width, height, scale, wait_ms=15000):
    """Screenshot html_path (CSS size width x height) at device scale `scale` into png_path."""
    profile = tempfile.mkdtemp(prefix='oe-chrome-')
    try:
        subprocess.run([
            chrome_bin(), '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
            '--user-data-dir=' + profile, '--allow-file-access-from-files',
            '--window-size=%d,%d' % (round(width), round(height)),
            '--force-device-scale-factor=%s' % scale,
            '--virtual-time-budget=%d' % wait_ms,
            '--screenshot=' + os.path.abspath(png_path),
            'file://' + os.path.abspath(html_path),
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
