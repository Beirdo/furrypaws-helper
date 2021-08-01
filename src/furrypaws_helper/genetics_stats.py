import logging

from furrypaws_helper.genetics_base import BaseGenetics

logger = logging.getLogger(__name__)


"""
https://www.furry-paws.com/stats/breed/genetics

#15	Stat Boost	
Can be agi, con, int, spd, stm, str. Random hierarchy.

#16	Extra Stat Boost	
Only effects puppy with use of a Level 3 Breeder. Can be agi, con, int, spd, stm, str. Random hierarchy.
"""


class StatBoostGenetics(BaseGenetics):
    type_ = "stats boost"

    def summarize(self):
        summary = []
        for index in [15, 16]:
            alleles = self.alleles[index]
            if alleles[0] == alleles[1]:
                summary.append(alleles[0])
            else:
                summary.append("/".join(alleles))

        return ", ".join(summary)