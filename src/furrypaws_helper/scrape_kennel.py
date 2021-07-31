import json
import logging
import os
import re
import sys

from bs4 import BeautifulSoup
from laracna.scraper import Scraper

from furrypaws_helper import setup_logging
from furrypaws_helper.config import FurryConfig

logger = logging.getLogger(__name__)


class KennelScraper(object):
    dog_re = re.compile(r'^https://www.furry-paws.com/dog/index/\d+/?$')

    def __init__(self):
        self.callbacks = {
            "login": self.login_response,
            "kennel-list": self.kennel_response,
            "dog": self.dog_response,
        }
        self.config = FurryConfig()
        self.scraper = Scraper(callbacks=self.callbacks, basedir=self.config.cachedir(), expiry=self.config.expiry())
        self.cookiefile = self.config.cookiefile()

    def login_response(self, code, body):
        logger.info("Got login response: code %d" % code)
        self.scraper.save_cookies(self.cookiefile)
        return (None, [])

    def kennel_response(self, code, body):
        logger.info("Got kennel response: code %d" % code)
        # parse the kennel page, return no response, but a list of dog pages to hit
        soup = BeautifulSoup(body, features="html.parser")
        urls = {a['href'] for a in soup.select("tr a")}
        urls = list(filter(self.dog_re.search, urls))
        items = [{"url": url, "type": "dog"} for url in urls]
        return (None, items)

    def dog_response(self, code, body):
        logger.info("Got dog response: code %d" % code)
        # parse the dog page, return the data item as a response, and no chain
        return (None, [])

    def execute(self, output_filename):
        self.scraper.scrape()

        if os.path.exists(self.cookiefile):
            self.scraper.load_cookies(self.cookiefile)
        else:
            # Login to the page, using credentials in ~/.furrypaws
            logger.info("Logging into furrypaws")
            login_form_data = self.config.get_login_form_data()
            self.scraper.queue(**login_form_data)

        # And start scraping from the "overview" page to get all of the dogs listed
        logger.info("Queuing kennel overview")
        self.scraper.queue(url="https://www.furry-paws.com/kennel/overview", type_="kennel-list")

        # Wait for scraper to finish
        logger.info("Waiting for scraper to finish")
        self.scraper.wait()

        logger.info("Grabbing results")
        results = self.scraper.get_results()

        logger.info("Saving results to %s" % output_filename)
        with open(output_filename, "w") as f:
            json.dump(results, f, indent=2, sort_keys=True)


def main():
    setup_logging(logging.DEBUG)
    kennel_scraper = KennelScraper()
    kennel_scraper.execute("kennel-list.json")


if __name__ == "__main__":
    sys.exit(main())
