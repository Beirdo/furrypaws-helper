import json
import logging
import os
import re
import sys

from bs4 import BeautifulSoup
from laracna.scraper import Scraper

from furrypaws_helper import setup_logging
from furrypaws_helper.config import FurryConfig
from furrypaws_helper.genotype import Genotype

logger = logging.getLogger(__name__)


class KennelScraper(object):
    dog_re = re.compile(r'^https://www.furry-paws.com/dog/index/(?P<id>\d+)/?$')
    kennel_re = re.compile(r'https://www.furry-paws.com/kennel/view/\d+/\d+/?$')
    age_re = re.compile(r'^(?P<age>\d+) FP Days')
    breed_wait_re = re.compile(r'^(?P<count>\d+)(?:\s+\(Can be bred again in (?P<wait>\d+) days\))?$')
    breed_today_re = re.compile(r'^(?P<count>\d+)(?:\s+\(Can be bred (?P<today>\d+) times today\))?$')
    breed_re = re.compile(r'^(?:Registered\s+)?(?P<breed>.*?)\s\((?P<group>.*?)\)$')
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
    pedigree_order = ["paternal grandfather", "paternal grandmother",
                      "father", "maternal grandfather", "maternal grandmother",
                      "mother"]

    def __init__(self):
        self.callbacks = {
            "login": self.login_response,
            "kennel": self.kennel_response,
            "dog": self.dog_response,
        }
        self.config = FurryConfig()
        self.scraper = Scraper(callbacks=self.callbacks, basedir=self.config.cachedir(), expiry=self.config.expiry())
        self.cookiefile = self.config.cookiefile()

    def login_response(self, response):
        logger.info("Got login response: code %d" % response.get("code", None))
        self.scraper.save_cookies(self.cookiefile)

    def kennel_response(self, response):
        logger.info("Got kennel response: code %d" % response.get("code", None))
        # parse the kennel page, return no response, but a list of dog pages to hit
        soup = BeautifulSoup(response.get("body", ""), features="html.parser")
        urls = {a['href'] for a in soup.select("a")}
        dog_urls = list(filter(self.dog_re.search, urls))
        kennel_urls = list(filter(self.kennel_re.search, urls))
        items = [{"url": url, "type": "dog"} for url in dog_urls]
        items.extend([{"url": url, "type": "kennel"} for url in kennel_urls])
        return {"chain": items}

    def dog_response(self, response):
        logger.info("Got dog response: code %d" % response.get("code", None))
        # parse the dog page, return the data item as a response, and no chain
        soup = BeautifulSoup(response.get("body", ""), features="html.parser")
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
        results["last-update"] = response.get("ctime", 0.0)
        genotype = Genotype(results.get("genotype", ""))
        results["summary"] = genotype.get_summary()

        age = 0
        match = self.age_re.search(results.get("age", ""))
        if match:
            age = int(match.group("age"))
            results["age"] = age

        sex = results.get("sex", "")
        wait = 0
        if sex == "Female":
            match = self.breed_wait_re.search(results.get("bred", ""))
            if match:
                wait = match.group("wait")
                if not wait:
                    wait = 0
                else:
                    wait = int(wait)
                count = int(match.group("count"))
                results["breed-count"] = count
                results["breed-wait"] = wait
        else:
            match = self.breed_today_re.search(results.get("bred", ""))
            if match:
                today = match.group("today")
                if not today:
                    today = 0
                else:
                    today = int(today)
                count = int(match.group("count"))
                results["breed-count"] = count
                results["breed-today"] = today
                if today == 0:
                    wait = 1

        breedable = 12 <= age <= 110 and wait == 0
        results["breedable"] = breedable

        match = self.breed_re.search(results.get("breed", ""))
        if match:
            results["breed"] = match.group("breed")
            results["breed-group"] = match.group("group")

        history_tab = soup.select_one("div#tab_history")
        pedigree_boxes = history_tab.select("div.pedigree_box")
        pedigree_texts = [[text for text in box.stripped_strings]
                          for box in pedigree_boxes]
        pedigree = {name: pedigree_texts[index] for (index, name) in enumerate(self.pedigree_order)}
        results["pedigree"] = pedigree

        match = self.dog_re.search(response.get("url", ""))
        if match:
            results["id"] = int(match.group("id"))

        logger.info("Dog: %s" % results["name"])
        return {"results": results}

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
