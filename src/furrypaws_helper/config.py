import configparser
import logging
import os

logger = logging.getLogger(__name__)


class FurryConfig(object):
    def __init__(self):
        filename = os.path.expanduser("~/.furrypaws/config")
        logger.info("Reading config from %s" % filename)
        config = configparser.SafeConfigParser()
        config.read(filename)
        self.config = config

    def cookiefile(self):
        filename = self.get("cookie-file", "~/.furrypaws/cookies.pickle")
        return os.path.expanduser(filename)

    def cachedir(self):
        cachedir = self.get("cache-dir", "~/.furrypaws/cache")
        return os.path.expanduser(cachedir)

    def expiry(self):
        return int(self.get("cache-expiry", 86400))

    def get(self, key, fallback=None):
        return self.config.get("furrypaws", key, fallback=fallback)

    def get_login_form_data(self):
        username = self.get("username")
        password = self.get("password")

        data = {
            "username": username,
            "password": password,
            "login_submit": "Log In",
            "remember_me": "on",
        }

        return {
            "url": "https://www.furry-paws.com/",
            "method": "POST",
            "data": data,
            "type_": "login",
            "headers": {
                "Referer": "https://www.furry-paws.com/",
            },
        }
