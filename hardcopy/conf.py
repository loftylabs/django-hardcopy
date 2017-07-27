import platform
from django.conf import settings


def smart_chrome_default():
    """
    Attempt to guess the Chrome path by default.  (Mostly to find Chrome by default on OSX in it's
    weird Apple place.)
    """

    if platform.uname()[0] == "Darwin":
        return '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome'

    return 'chrome'


class HardCopyConfig(object):
    CHROME_PATH = getattr(settings, 'CHROME_PATH', smart_chrome_default())


hc_settings = HardCopyConfig()