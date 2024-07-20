# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 14:28:20 2024

@author: shane
"""
import requests

REQUEST_READ_TIMEOUT = 18
REQUEST_CONNECT_TIMEOUT = 5

# TODO: try all of these; cache (save in prefs.json) the one which works first
URLS_API = (
    "https://api.nutra.tk",
    "https://api.dev.nutra.tk",
    "http://216.218.228.93",  # dev
    "http://216.218.216.163",  # prod
)


def cache_mirrors() -> str:
    """Cache mirrors"""
    for mirror in URLS_API:
        try:
            _res = requests.get(
                mirror,
                timeout=(REQUEST_CONNECT_TIMEOUT, REQUEST_READ_TIMEOUT),
                verify=mirror.startswith("https://"),
            )

            _res.raise_for_status()
            # TODO: save in persistence config.ini
            print("INFO: mirror SUCCESS '%s'" % mirror)
            return mirror
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            print("WARN: mirror FAILURE '%s'" % mirror)

    return str()


class ApiClient:
    """Client for connecting to the remote server/API."""

    def __init__(self) -> None:
        self.host = cache_mirrors()
        if not self.host:  # pragma: no cover
            raise ConnectionError("Cannot find suitable API host!")

    def post(self, path: str, data: dict) -> requests.Response:
        """Post data to the API."""
        _res = requests.post(
            self.host + "/" + path,
            json=data,
            timeout=(REQUEST_CONNECT_TIMEOUT, REQUEST_READ_TIMEOUT),
        )
        _res.raise_for_status()
        return _res

    # TODO: move this outside class; support with host iteration helper method
    def post_bug(self, bug: dict) -> requests.Response:
        """Post a bug report to the developer."""
        return self.post("bug", bug)
