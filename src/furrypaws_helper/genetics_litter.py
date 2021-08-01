import logging

from furrypaws_helper.genetics_base import BaseGenetics

logger = logging.getLogger(__name__)


"""
https://www.furry-paws.com/stats/breed/genetics

#14	Litter Size	
Any L - Medium litter (4-8 puppies)
l, but no L - Small litter (1-3 puppies)
lala - Large litter (9-12 puppies)
"""


class LitterSizeGenetics(BaseGenetics):
    type_ = "litter size"

    def summarize(self):
        if "L" in self.alleles[14]:
            return "Medium litter (4-8 puppies)"
        elif 'l' in self.alleles[14]:
            return "Small litter (1-3 puppies)"
        elif self.genomes[14] == "lala":
            return "Large litter (9-12 puppies)"
        else:
            return "WTF"
