import logging

from furrypaws_helper.genetics_base import BaseGenetics

logger = logging.getLogger(__name__)

"""
https://www.furry-paws.com/stats/breed/genetics

#17-22	Hip Rating	
Quantitative Trait Behavior where each hh is a defect
0 defects - Excellent Rating
1-2 defects - Good Rating
3-4 defects - Fair Rating
5+ defects - Poor Rating

#23-28	Elbow Rating	
Quantitative Trait Behavior where each hh is a defect
0 defects - Excellent Rating
1-2 defects - Good Rating
3-4 defects - Fair Rating
5+ defects - Poor Rating

#29-34	Eye Rating	
Quantitative Trait Behavior where each hh is a defect
0 defects - Excellent Rating
1-2 defects - Good Rating
3-4 defects - Fair Rating
5+ defects - Poor Rating

#35-40	Ear Rating	
Quantitative Trait Behavior where each hh is a defect
0 defects - Excellent Rating
1-2 defects - Good Rating
3-4 defects - Fair Rating
5+ defects - Poor Rating
"""


class HealthGenetics(BaseGenetics):
    type_ = "health"
    threshholds = [("P", 5), ("F", 3), ("G", 1), ("E", 0)]
    types = ["HH", "Hh", "hh"]

    def summarize(self):
        blocks = []
        for i in range(17, 41, 6):
            blocks.append(self.genomes[i:i + 6])
        health_slice = self.genomes[17:41]

        ratings = []
        for block in blocks:
            defects = block.count("hh")
            for (rating, min_count) in self.threshholds:
                if defects >= min_count:
                    ratings.append(rating)
                    break

        healths = {type_: health_slice.count(type_) for type_ in self.types}
        healths = list(map(lambda x: "%d%s" % (x[1], x[0]), filter(lambda x: x[1] > 0, sorted(healths.items()))))

        return " ".join(["".join(ratings)] + healths)
