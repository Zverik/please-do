GITHUB_PROJECT = ''
EMAIL_TO = ''

SMTP_SERVER = 'localhost'
SMTP_LOGIN = None
SMTP_PASSWORD = None
EMAIL_FROM = 'github-issues@maps.me'

# Override these settings in 'config_local.py'
try:
    from config_local import *
except ImportError:
    pass
