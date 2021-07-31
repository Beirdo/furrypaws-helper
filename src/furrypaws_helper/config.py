import configparser
import logging
import os

logger = logging.getLogger(__name__)


class FurryConfig(object):
    def __init__(self):
        filename = os.path.expanduser("~/.furrypaws")
        config = configparser.SafeConfigParser()
        config.read(filename)
        self.config = config

    @staticmethod
    def cookiefile():
        return os.path.expanduser("~/.furrypaws.cookies")

    def get(self, key):
        return self.config.get("furrypaws", key)

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
