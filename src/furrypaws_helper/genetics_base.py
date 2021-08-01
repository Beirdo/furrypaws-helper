import logging

from furrypaws_helper.exceptions import BadGenome

logger = logging.getLogger(__name__)

"""
https://www.furry-paws.com/stats/breed/genetics

#0	Eye Color
    PP/Pp/Py - Normal eye color
    pp/py - Eye color ignores merle
    yy - Blue eyes

#1	Dominant black/Brindle	
    KK/KKbr/Kk - Overrides agouti pattern on pair #6, gives solid black coat
    KbrKbr/Kbrk - Gives brindled coat
    kk - Allows expression of pattern on pair #6 in coat

#2	Red Extension/Masking	
    EmEm/EmE/Eme - Allows black in coat, has a black mask. Mask only shown when pair #1 is not KK.
    EE/Ee - Allows black in coat, no mask
    ee - No black in coat (only red), no mask

#3	Chocolate	
    BB/Bb - Black pigment
    bb - All black pigment turns into chocolate

#4	Dilution	
    DD/Dd - No dilution
    dd - Dilution. All black pigment turns into blue, all chocolate pigment turns into mouse grey.

#5	Silvering	
    SlSl/Slsl - causes "silvering." Masks all other colour and makes the dog solid white.
    slsl - no silvering

#6	Agouti	
    Any ay - Sable pattern
    aw, but no ay - Grizzle pattern
    at, but no ay, aw - Tanpoint pattern
    asa, but no ay, aw, at - Saddle pattern
    a but no ay, aw, at, asa - Recessive solid black

#7	White	
    Any S - no modifications
    si, but no S - Irish white
    sp, but no si, S - Piebald white
    sw, but no sp, si, S - extreme piebald white

#8	Merling	
    MM/Mm - Black areas are merled
    mm - No merling

#9	Roaning	
    RR/Rr - White areas are roaned
    rr - No roaning

#10	Ticking	
    Any T - Ticking, only shows up on dogs with no S in Pair #7
    ts but no T - Dalmatian spots
    ti but no T, Ts - No Ticking or spots

#11	Color Intensity	
    Any C - Normal red pigment
    cch, but no C - Red lightened to fawn
    ce, but no C or cch - Red lightened to cream
    cw, but no ce, c, C - Red lightened to silver

#12	Greying	
    GG/Gg - Turns black into steel blue and chocolate into faded brown
    gg - No greying

#13	Light Undersides	
    UU/Uu - Light undersides
    uu - Not light undersides

#14	Litter Size	
    Any L - Medium litter (4-8 puppies)
    l, but no L - Small litter (1-3 puppies)
    lala - Large litter (9-12 puppies)

#15	Stat Boost	
    Can be agi, con, int, spd, stm, str. Random hierarchy.

#16	Extra Stat Boost	
    Only effects puppy with use of a Level 3 Breeder. Can be agi, con, int, spd, stm, str. Random hierarchy.

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


class BaseGenetics(object):
    type_ = None
    possible_alleles = [
        ["P", "p", "y"],  # 0 - Eye Color
        ["Kbr", "K", "k"],  # 1 - Dominant black/Brindle
        ["Em", "E", "e"],  # 2 - Red Extension/Masking
        ["B", "b"],  # 3 - Chocolate
        ["D", "d"],  # 4 - Dilution
        ["Sl", "sl"],  # 5 - Silvering
        ["Ay", "aw", "at", "asa", "a"],  # 6 - Agouti
        ["S", "si", "sp", "sw"],  # 7 - White
        ["M", "m"],  # 8 - Merling
        ["R", "r"],  # 9 - Roaning
        ["T", "ts", "t"],  # 10 - Ticking
        ["C", "cch", "ce", "cw", "c"],  # 11 - Color Intensity (red)
        ["G", "g"],  # 12 - Greying
        ["U", "u"],  # 13 - Light Undersides
        ["L", "la", "l"],  # 14 - Litter Size
        ["agi", "cha", "con", "int", "spd", "stm", "str"],  # 15 - Stat Boost
        ["agi", "cha", "con", "int", "spd", "stm", "str"],  # 16 - Extra Stat Boost
        ["H", "h"],  # 17 - Hip Rating
        ["H", "h"],  # 18 - Hip Rating
        ["H", "h"],  # 19 - Hip Rating
        ["H", "h"],  # 20 - Hip Rating
        ["H", "h"],  # 21 - Hip Rating
        ["H", "h"],  # 22 - Hip Rating
        ["H", "h"],  # 23 - Elbow Rating
        ["H", "h"],  # 24 - Elbow Rating
        ["H", "h"],  # 25 - ELbow Rating
        ["H", "h"],  # 26 - Elbow Rating
        ["H", "h"],  # 27 - Elbow Rating
        ["H", "h"],  # 28 - Elbow Rating
        ["H", "h"],  # 29 - Eye Rating
        ["H", "h"],  # 30 - Eye Rating
        ["H", "h"],  # 31 - Eye Rating
        ["H", "h"],  # 32 - Eye Rating
        ["H", "h"],  # 33 - Eye Rating
        ["H", "h"],  # 34 - Eye Rating
        ["H", "h"],  # 35 - Ear Rating
        ["H", "h"],  # 36 - Ear Rating
        ["H", "h"],  # 37 - Ear Rating
        ["H", "h"],  # 38 - Ear Rating
        ["H", "h"],  # 39 - Ear Rating
        ["H", "h"],  # 40 - Ear Rating
    ]

    def __init__(self, genomes):
        self.alleles = self.split_genomes(genomes)
        self.genomes = ["".join(pair) for pair in self.alleles]
        self.summary = self.summarize()

    def get_summary(self):
        return self.summary

    def summarize(self):
        raise NotImplementedError("summarize not implemented in %s" % self.__class__.__name__)

    def split_genomes(self, genomes):
        pairs = []
        for (index, genome) in enumerate(genomes):
            orig_genome = str(genome)
            genome = str(genome)
            pair = []
            # print("index: %d, genome: '%s'" % (index, genome))
            for allele in self.possible_alleles[index]:
                while allele in genome:
                    pair.append(allele)
                    genome = genome.replace(allele, "", 1)
                    # print("index: %d  allele: %s, genome: '%s'" % (index, allele, genome))
            # print("index: %d, pair: %s" % (index, pair))
            if len(pair) != 2:
                raise BadGenome(
                    "Bad genome: Index %d (%s) has %d recognized alleles" % (index, orig_genome, len(pair)))
            pairs.append(sorted(pair))
        return pairs
