from django.conf import settings

PRIVAT24_API_TOKEN = getattr(settings, 'PRIVAT24_API_TOKEN', '')
