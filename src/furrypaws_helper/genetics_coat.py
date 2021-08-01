import logging

from furrypaws_helper.genetics_base import BaseGenetics

logger = logging.getLogger(__name__)

"""
https://www.furry-paws.com/stats/breed/genetics

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
    
https://www.furry-paws.com/help/article/fp-color-genetics
"""


class CoatColorGenetics(BaseGenetics):
    type_ = "coat color"

    def summarize(self):
        summary = ""
        try:
            # Check for solid black
            solid_black = "K" in self.alleles[1]

            # Check for brindle
            brindled = not solid_black and "Kbr" in self.alleles[1]

            # Check for agouti
            agouti = not solid_black and (brindled or self.genomes[1] == "kk")

            black_mask = agouti and "Em" in self.alleles[2]

            non_solid_black = "E" in self.genomes[2] and not black_mask

            red_based = self.genomes[2] == "ee"
            if red_based:
                solid_black = False
                non_solid_black = False
                agouti = False

            # Sable ("Ay"), Grizzle ("aw"), Points ("at"), Saddle ("asa"), Recessive Solid Black ("a")
            recessive_solid_black = False
            if agouti:
                if self.genomes[6] == "aa":
                    solid_black = True
                    brindled = False
                    black_mask = False
                    recessive_solid_black = True
                    agouti = False
                elif "Ay" in self.alleles[6]:
                    agouti = "Sable"
                elif "aw" in self.alleles[6]:
                    agouti = "Grizzle"
                elif "at" in self.alleles[6]:
                    agouti = "Points"
                elif "asa" in self.alleles[6]:
                    agouti = "Saddle"
                else:
                    agouti = False

            black_color = "Black"

            if self.genomes[3] == "bb":
                black_color = "Chocolate"

            if self.genomes[4] == "dd":
                if black_color == "Black":
                    black_color = "Blue"
                else:
                    black_color = "Isabella"

            mask_color = black_color

            if "G" in self.alleles[12]:
                if black_color == "Black":
                    black_color = "Steel Blue"
                elif black_color == "Chocolate":
                    black_color = "Faded Brown"
                elif black_color == "Blue":
                    black_color = "Faded Blue"
                else:
                    black_color = "Faded Isabella"

            merled = "M" in self.alleles[8]
            if merled and black_color == "Black":
                black_color = "Blue"

            """
            How about all those shades of red?
            The shades of red are controlled by the "Color Intensity" (Pair #11) locus. "C" is the most dominant, causing 
            the color "Red." "cch" is the next most dominant, causing the color "Fawn" on dogs, or "Tan" when occurring in 
            the "Points" marking. "ce" is the next dominant, causing the color "Cream," and "cw" is the most recessive, 
            causing "Silver" only when homozygous ("cwcw"). Shades of red will only appear if the dog is "ee" in the second
            locus, or if the Agouti set is active (Kbr or k most dominant in the first pair).
            """
            red_color = None

            if red_based or agouti:
                if "C" in self.alleles[11]:
                    red_color = "Red"
                elif "cch" in self.alleles[11]:
                    if agouti == "Points":
                        red_color = "Tan"
                    else:
                        red_color = "Fawn"
                elif "ce" in self.alleles[11]:
                    red_color = "Cream"
                elif self.genomes[11] == "cwcw":
                    red_color = "Silver"

            """
            What about Irish, Piebald, Extreme piebald?
            These are white markings on your dog. The "White" (Pair #7) locus controls the appearance of white patterns. 
            There are four alleles possible in this locus. The most dominant allele is "S" and causes a dog to have no 
            white markings (self colored, in real life terms). "si" is the second most dominant in the set, causing 
            "Irish" markings. "sp" is the third most dominant, creating a "Piebald" dog. Finally, "sw" is the least 
            dominant allele, causing the "Extreme Piebald" whiting when appearing homozygously in a dog ("swsw"). Whiting 
            levels appear alongside the colors and markings above.
            """

            white_color = False
            if "S" in self.alleles[7]:
                white_color = False
            elif "si" in self.alleles[7]:
                white_color = "Irish"
            elif "sp" in self.alleles[7]:
                white_color = "Piebald"
            elif self.genomes[7] == "swsw":
                white_color = "Extreme Piebald"

            roaning = False
            ticking = False
            if white_color:
                if "R" in self.alleles[9]:
                    roaning = "Roaning"

                if "T" in self.alleles[10]:
                    ticking = "Ticking"
                    roaning = False
                elif 'ts' in self.alleles[10]:
                    ticking = "Dalmation Spots"

            undersides = "U" in self.alleles[13]

            silvering = "Sl" in self.alleles[5]

            if silvering:
                summary = "Solid White"
                return

            if brindled:
                summary += "Brindle "

            if solid_black or non_solid_black:
                summary += black_color
            elif red_color:
                summary += red_color

            if merled:
                summary += " Merle"

            if white_color:
                summary += " and White (%s)" % white_color

            with_ = False
            if agouti:
                agouti_color = black_color
                if agouti == "Points":
                    agouti_color = red_color
                summary += " with %s %s" % (agouti_color, agouti)
                with_ = True

            if black_mask:
                if not with_:
                    summary += " with"
                    with_ = True
                else:
                    summary += " and"

                if black_color != mask_color:
                    summary += " %s" % mask_color
                summary += " Mask"

            if roaning:
                if not with_:
                    summary += " with"
                    with_ = True
                else:
                    summary += " and"
                summary += " Roaning"

            if ticking:
                if not with_:
                    summary += " with"
                    with_ = True
                else:
                    summary += " and"
                summary += " %s" % ticking

            if undersides:
                if not with_:
                    summary += " with"
                    with_ = True
                else:
                    summary += " and"
                summary += " Light Undersides"

        finally:
            return summary
