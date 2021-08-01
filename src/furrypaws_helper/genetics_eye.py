import logging

from furrypaws_helper.genetics_base import BaseGenetics

logger = logging.getLogger(__name__)


"""
https://www.furry-paws.com/stats/breed/genetics
#0	Eye Color	
PP/Pp/Py - Normal eye color
pp/py - Eye color ignores merle
yy - Blue eyes

https://www.furry-paws.com/help/article/introduction-to-fp-genetics
Do genetics affect eye colors? How can I get a dog with brown/amber/blue eyes?
Eye colors of dogs on here are tied directly to the coat color genes. This means the eye color your dog gets assigned depends on what alleles are present in the dog's color gene string. Not all breeds have the same possible coat colors, and some are quite limited, thus not all breeds can have all eye colors. Eye colors are as follows:
Brown - "B" allele in pair 3 (BB/Bb, black dogs)
Amber - "bb" in pair 3 or "dd" in pair 4 (chocolate/diluted dogs)
Blue - "M" allele in pair 8 (MM/Mm, merle dogs)
"""


class EyeColorGenetics(BaseGenetics):
    type_ = "eye color"

    def summarize(self):
        if "P" in self.genomes[0]:
            if "M" in self.genomes[8]:
                summary = "Blue eyes"
            elif self.genomes[3] == 'bb' or self.genomes[4] == 'dd':
                summary = "Amber eyes"
            elif "B" in self.genomes[3]:
                summary = "Brown eyes"
            else:
                summary = "WTF"
            summary += " (Normal eye color)"
        elif "p" in self.genomes[0]:
            if self.genomes[3] == 'bb' or self.genomes[4] == 'dd':
                summary = "Amber eyes"
            elif "B" in self.genomes[3]:
                summary = "Brown eyes"
            else:
                summary = "WTF"
            summary += " (Eye color ignores merle)"
        else:
            return "Blue eyes"

        return summary
