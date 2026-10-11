"""Which public site is this request for: nkusu.com or 2tume.com?

One Flask, one database, two domains. Payment return URLs must bring the
buyer back to the domain they paid from, so they are built from the Host
header of the request — but only for the domains listed in SITE_URLS.
Anything else (an IP, a forged Host) falls back to FRONTEND_URL.
"""
from urllib.parse import urlsplit

from flask import current_app, has_request_context, request


def site_url():
    """Root URL of the current site, e.g. 'https://2tume.com' (no trailing slash)."""
    default = current_app.config['FRONTEND_URL'].rstrip('/')
    if not has_request_context():
        return default

    # nginx forwards the visitor's Host; X-Forwarded-Host wins if a proxy sets it.
    host = (request.headers.get('X-Forwarded-Host') or request.host or '').split(',')[0].strip().lower()
    for url in current_app.config['SITE_URLS']:
        if urlsplit(url).netloc.lower() == host:
            return url.rstrip('/')
    return default


def on_site(url):
    """Move a configured absolute URL onto the current site, keeping its path.

    'https://www.nkusu.com/api/payments/payment/success' seen from 2tume.com
    becomes 'https://2tume.com/api/payments/payment/success'.
    """
    parts = urlsplit(url)
    path = parts.path + (f'?{parts.query}' if parts.query else '')
    return f'{site_url()}{path}'
