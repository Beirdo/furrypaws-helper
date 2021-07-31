import logging

logger = logging.getLogger(__name__)


def setup_logging(level=logging.INFO):
    log_format = "%(asctime)s: %(levelname)s [%(threadName)s] - %(message)s"

    formatter = logging.Formatter(log_format)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)

    # noinspection PyTypeChecker
    root_logger = logging.getLogger(None)
    root_logger.setLevel(level)
    root_logger.addHandler(handler)

