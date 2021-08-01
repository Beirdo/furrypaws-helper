import logging
import sys

from furrypaws_helper.exceptions import BadGenotype
from furrypaws_helper.genetics_coat import CoatColorGenetics
from furrypaws_helper.genetics_eye import EyeColorGenetics
from furrypaws_helper.genetics_health import HealthGenetics
from furrypaws_helper.genetics_litter import LitterSizeGenetics
from furrypaws_helper.genetics_stats import StatBoostGenetics

logger = logging.getLogger(__name__)


class Genotype(object):
    def __init__(self, text=None):
        self.text = ""
        self.genome_list = []
        self.genomes = {}
        self.summary = {}
        self.alleles = []
        self.set_text(text)

    def set_text(self, text):
        self.text = text.strip()
        self.summarize()

    def summarize(self):
        genomes = str(self.text).strip().split()
        if len(genomes) != 41:
            raise BadGenotype("Genotypes must have 41 genomes, not %d" % len(genomes))
        self.genome_list = genomes
        self.genomes = {
            "eye-color": EyeColorGenetics(genomes),
            "coat-color": CoatColorGenetics(genomes),
            "litter-size": LitterSizeGenetics(genomes),
            "stat-boost": StatBoostGenetics(genomes),
            "health": HealthGenetics(genomes),
        }
        self.summary = {key: value.get_summary() for (key, value) in self.genomes.items()}
        self.alleles = self.genomes["health"].alleles

    def get_summary(self):
        return self.summary


if __name__ == "__main__":
    for line in sys.stdin:
        genotype = Genotype(line)
        print(genotype.get_summary())