import json
import logging
import sys

from laracna.scraper import Scraper

from furrypaws_helper.config import FurryConfig

logger = logging.getLogger(__name__)


def eat_response(code, body):
    print(code, body)
    return (None, [])


def kennel_response(code, body):
    print(code, body)
    # parse the kennel page, return no response, but a list of dog pages to hit
    return (None, [])


def dog_response(code, body):
    print(code, body)
    # parse the dog page, return the data item as a response, and no chain
    return (None, [])


callbacks = {
    "login": eat_response,
    "kennel-list": kennel_response,
    "dog": dog_response,
}


def main():
    config = FurryConfig()
    scraper = Scraper(callbacks=callbacks)
    scraper.scrape()

    # Login to the page, using credentials in ~/.furrypaws
    login_form_data = config.get_login_form_data()
    scraper.queue(**login_form_data)

    # And start scraping from the "overview" page to get all of the dogs listed
    scraper.queue(url="https://www.furry-paws.com/kennel/overview", type_="kennel-list")

    # Wait for scraper to finish
    scraper.wait()
    results = scraper.get_results()

    with open("kennel-list.json", "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    sys.exit(main())
