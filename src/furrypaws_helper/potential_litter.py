import json
import logging
import sys
from collections import defaultdict

from furrypaws_helper import setup_logging
from furrypaws_helper.genetics_health import HealthGenetics
from furrypaws_helper.genetics_litter import LitterSizeGenetics

logger = logging.getLogger(__name__)


class PotentialLitter(object):
    def __init__(self, dad_genotype, mom_genotype):
        self.dad = LitterSizeGenetics(dad_genotype)
        self.mom = LitterSizeGenetics(mom_genotype)
        self.litter = self.breed()

    def breed(self):
        dad_alleles = self.dad.alleles
        mom_alleles = self.mom.alleles

        pup_genomes = []
        for alleles in zip(dad_alleles, mom_alleles):
            (d, m) = alleles
            output = defaultdict(int)
            for i in range(2):
                for j in range(2):
                    genome = "".join(sorted([d[i], m[j]]))
                    output[genome] += 1
            pup_genomes.append({key: 25 * value for (key, value) in output.items()})

        health_slice = pup_genomes[17:41]
        expected_defects = [sum([key.count("h") * value for (key, value) in genome.items()]) / 100.0
                            for genome in health_slice]

        ratings = []
        for i in range(0, 24, 6):
            score = sum(expected_defects[i:i + 6])
            for (rating, min_count) in HealthGenetics.threshholds:
                if score >= min_count:
                    ratings.append(rating)
                    break

        litter = {
            "size-genome": mom_alleles[14],
            "litter-size": self.mom.get_summary(),
            "genomes": pup_genomes,
            "defects-map": expected_defects,
            "avg-total-defects": sum(expected_defects),
            "avg-health-score": "".join(ratings),
        }

        return litter


def main():
    setup_logging(logging.DEBUG)

    logger.info("Reading kennel list")
    with open("kennel-list.json", "r") as f:
        kennel = json.load(f)

    logger.info("Sorting breedable dogs")
    dogs = {}
    for dog in kennel:
        breedable = dog.get("breedable", False)
        if not breedable:
            continue

        breed = dog.get("breed", None)
        sex = dog.get("sex", None)
        if breed not in dogs:
            dogs[breed] = {}
        if sex not in dogs[breed]:
            dogs[breed][sex] = []
        dogs[breed][sex].append(dog)

    out_litters = []
    for (breed, alldogs) in sorted(dogs.items()):
        logger.info("Processing breed: %s" % breed)
        females = alldogs.get("Female", [])
        males = alldogs.get("Male", [])

        if not females:
            logger.info("No breedable females.  Skipping")
            continue

        if not males:
            logger.info("No breedable males.  Skipping")
            continue

        for bitch in females:       # Hey, don't blame me, it's the correct term!
            logger.info("Processing: %s" % bitch.get("name", None))
            mom_genotype = bitch.get("genotype", "")
            litters = []
            for stud in males:
                dad_genotype = stud.get("genotype", "")
                litters.append(PotentialLitter(dad_genotype, mom_genotype).litter)

            litters = sorted(litters, key=lambda x: x.get("avg-health-score", 9999.99))
            bitch["potential-litters"] = litters
            out_litters.append[bitch]

        with open("potential-litters.json", "w") as f:
            json.dump(out_litters, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    sys.exit(main())
