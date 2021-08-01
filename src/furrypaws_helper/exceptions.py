import logging

logger = logging.getLogger(__name__)


class BadGenotype(RuntimeError):
    pass


class BadGenome(RuntimeError):
    pass