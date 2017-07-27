from django.conf import settings


class HardCopyConfig(object):
    CHROME_PATH = getattr(settings, 'CHROME_PATH', 'chrome')


hc_settings = HardCopyConfig()