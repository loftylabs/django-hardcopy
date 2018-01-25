import platform
from pathlib import Path

from django.conf import settings

LINUX_PATHS = [
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/usr/bin/chrome',
    '/usr/bin/chrome-browser',
]


def get_chrome_path():
    """Attempt to guess the Chrome path by default."""

    if platform.uname()[0] == "Darwin":
        return '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome'
    if platform.uname()[0] == "Linux":
        # Iterate through some sane path defaults.
        for path in LINUX_PATHS:
            if Path(path).is_file():
                return path
    # No path found, throw an error.
    raise ValueError('Missing CHROME_PATH! Unable to resolve path!')


class HardCopyConfig(object):
    CHROME_PATH = (
        settings.CHROME_PATH
        if hasattr(settings, 'CHROME_PATH')
        else get_chrome_path())
    CHROME_WINDOW_SIZE = getattr(settings, 'CHROME_WINDOW_SIZE', '1280,720')


settings = HardCopyConfig()
