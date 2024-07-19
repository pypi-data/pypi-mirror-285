"""
This script is a the samcut project, designed to process paired-end FASTQ files by fragmenting DNA sequences at specified restriction enzyme sites.

Copyright © 2024 Samir Bertache

SPDX-License-Identifier: AGPL-3.0-or-later

===============================================================================

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import re
from typing import List, Tuple
import sys
from Bio.Restriction import RestrictionBatch
from Bio.Seq import Seq

logging.basicConfig(level=logging.INFO)


###############################  Common part #################################

def CaseAdaptation(List_Enzyme):
    """
    Case sensitive enzymes adaptation
    """
    for i, enzyme in enumerate(List_Enzyme):
        if enzyme == "hindiii":
            List_Enzyme[i] = "HindIII"
        elif enzyme == "dpnii":
            List_Enzyme[i] = "DpnII"
        elif enzyme == "bglii":
            List_Enzyme[i] = "BglII"
        elif enzyme == "mboi":
            List_Enzyme[i] = "MboI"
        elif enzyme == "arima":
            # Double enzyme 
            List_Enzyme[i] = "DpnII"
            List_Enzyme.append("HinfI")
    return List_Enzyme


def FindLigaSite(
    List_Enzyme: List[str], borderless: bool = False
) -> List[Tuple[re.Pattern, int]]:
    """
    This function finds the ligation sites for a given list of enzymes and
    their length.

    Parameters:
    List_Enzyme (List[str]): A list of enzymes for which to find the ligation
    sites.

    borderless (bool, optional): If True, the total length of the give and
                                        accept sites is used.
                                 If False, only the length of the give site
                                        is used. Default is False.

    Returns:
    List[Tuple[re.Pattern, int]]: A list of tuples, where each tuple contains
                                    a compiled regular expression
                                    pattern for the ligation site and the length
                                    of the site.
    """
    restriction_batch = RestrictionBatch(List_Enzyme)
    give_list = []
    accept_list = []
    ligation_site_list = []

    for enz in restriction_batch:
        site = enz.elucidate()
        fw_cut = site.find("^")
        rev_cut = site.find("_")

        # Purify give site
        give_site = site[:rev_cut].replace("^", "")
        while give_site[0] == "N":
            give_site = give_site[1:]
        give_list.append(give_site)

        # Purify accept site
        accept_site = site[fw_cut + 1:].replace("_", "")
        while accept_site[-1] == "N":
            accept_site = accept_site[:-1]
        accept_list.append(accept_site)

    # Find ligation site
    for give_site in give_list:
        for accept_site in accept_list:
            ligation_site = (give_site + accept_site).replace("N", ".")
            compiled_regex = re.compile(ligation_site)

            # Use total lenght for borderless
            if borderless:
                length = len(give_site) + len(accept_site)
            else:
                length = len(give_site)
            ligation_site_list.append((compiled_regex, length))pip

            # If ligation site is not palindromic
            reverse_complement_site = str(
                Seq(ligation_site).reverse_complement()
            )

            if ligation_site != reverse_complement_site:
                compiled_reverse_regex = re.compile(reverse_complement_site)
                # Use lenght of accept site for reverse complement site
                if borderless:
                    length = len(give_site) + len(accept_site)
                else:
                    length = len(accept_site)
                ligation_site_list.append((compiled_reverse_regex, length))

    return ligation_site_list


def SearchInDataBase(ListEnzyme, borderless=False):
    """
    _summary_ : Search enzyme in database and retrieve ligation site
    """
    if ListEnzyme == "No restriction enzyme found":
        print(ListEnzyme)
        sys.exit(0)
    else:
        if borderless:
            print("Mode Borderless")
        ligation_site_list = CaseAdaptation(ligation_site_list)
        ligation_site_list = FindLigaSite(ListEnzyme.split(","), borderless)
        print(f"Ligation sites: {ligation_site_list}", flush=True)
        return ligation_site_list


def Partitionning(num_threads):
    TWrite = num_threads // 4
    TRead = num_threads // 8
    TFrag = num_threads - (TWrite * 2) - (TRead * 2)
    return TWrite, TRead, TFrag
