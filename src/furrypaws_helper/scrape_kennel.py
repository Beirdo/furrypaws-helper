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
    kennel_re = re.compile(r'https://www.furry-paws.com/kennel/view/\d+/\d+/?$')
    dog_items = {
        "Full Name:": "name",
        "Callname:": "callname",
        "Breed:": "breed",
        "Gender:": "sex",
        "Days Aged:": "age",
        "Genotype:": "genotype",
        "Generation:": "generation",
        "Times Bred:": "bred",
    }
    dog_stats = ["level", "agility", "charisma", "intelligence", "speed",
                 "stamina", "strength"]

    def __init__(self):
        self.callbacks = {
            "login": self.login_response,
            "kennel": self.kennel_response,
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
        urls = {a['href'] for a in soup.select("a")}
        dog_urls = list(filter(self.dog_re.search, urls))
        kennel_urls = list(filter(self.kennel_re.search, urls))
        items = [{"url": url, "type": "dog"} for url in dog_urls]
        items.extend([{"url": url, "type": "kennel"} for url in kennel_urls])
        return (None, items)

    def dog_response(self, code, body):
        logger.info("Got dog response: code %d" % code)
        # parse the dog page, return the data item as a response, and no chain
        soup = BeautifulSoup(body, features="html.parser")
        about_rows = soup.select("div#tab_about tr")
        data = {row.th.get_text().strip(): row.td.get_text().strip()
                for row in about_rows}

        results = {self.dog_items[key]: value for (key, value) in data.items()
                   if key in self.dog_items}

        overview = soup.select("div.dog_overview_holder")
        if overview:
            for item in overview:
                text = item.get_text()

                if "LOCKED" in text:
                    results["locked"] = True

                if "Accepting Breeding Requests" in text:
                    results["accepting-requests"] = True

        spans = {item: soup.select("[class~=var_%s]" % item)
                 for item in self.dog_stats}
        stats = {key: span.pop().get_text() for (key, span) in spans.items()
                 if span}
        results["stats"] = stats

        logger.info("Dog: %s" % results["name"])
        return (results, [])

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
        logger.info("Queuing Main kennel")
        self.scraper.queue(url="https://www.furry-paws.com/kennel/view/1621357/0", type_="kennel")

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
