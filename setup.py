from setuptools import setup

long_description = "Django wrapper and utilities for generating PDF and PNG " \
    "files with context using the headless chrome or chromium browser."

setup(
    name='django-hardcopy',
    version='0.1.4',
    description=long_description,
    author='Casey Kinsey / Lofty Labs',
    author_email='casey@hirelofty.com',
    url='https://github.com/loftylabs/django-hardcopy',
    packages=['hardcopy'],
)
