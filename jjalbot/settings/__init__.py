import os


if os.getenv('JJALBOT_PRODUCTION'):
    from .production import *
else:
    from .development import *
