from django.conf import settings


class HardCopyConfig(object):
    PATH_TO_CHROME = getattr(settings, 'PATH_TO_CHROME', 'chrome')


hc_settings = HardCopyConfig()