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
scraper = None
config = None
dog_re = re.compile(r'^https://www.furry-paws.com/dog/index/\d+/?$')

def login_response(code, body):
    logger.info("Got login response: code %d" % code)
    cookiefile = FurryConfig.cookiefile()
    global scraper
    scraper.save_cookies(cookiefile)

    return (None, [])


def kennel_response(code, body):
    logger.info("Got kennel response: code %d" % code)
    # parse the kennel page, return no response, but a list of dog pages to hit
    soup = BeautifulSoup(body, features="html.parser")
    urls = {a['href'] for a in soup.select("tr a")}
    urls = list(filter(dog_re.search, urls))
    items = [{"url": url, "type": "dog"} for url in urls]
    return (None, items)


def dog_response(code, body):
    logger.info("Got dog response: code %d" % code)
    # parse the dog page, return the data item as a response, and no chain
    return (None, [])


callbacks = {
    "login": login_response,
    "kennel-list": kennel_response,
    "dog": dog_response,
}


def main():
    setup_logging(logging.DEBUG)
    config = FurryConfig()
    global scraper
    scraper = Scraper(callbacks=callbacks)
    scraper.scrape()

    cookiefile = config.cookiefile()
    if os.path.exists(cookiefile):
        scraper.load_cookies(cookiefile)
    else:
        # Login to the page, using credentials in ~/.furrypaws
        logger.info("Logging into furrypaws")
        login_form_data = config.get_login_form_data()
        logger.info("login: %s" % login_form_data)
        scraper.queue(**login_form_data)

    # And start scraping from the "overview" page to get all of the dogs listed
    logger.info("Queuing kennel overview")
    scraper.queue(url="https://www.furry-paws.com/kennel/overview", type_="kennel-list")

    # Wait for scraper to finish
    logger.info("Waiting for scraper to finish")
    scraper.wait()

    logger.info("Grabbing results")
    results = scraper.get_results()

    with open("kennel-list.json", "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    sys.exit(main())
