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
from typing import Generator, List, Tuple

logging.basicConfig(level=logging.INFO)


#################### Specific part of Borderless option #####################


def find_positions_for_one_site_borderless(
    text: str, Enzyme: Tuple[re.Pattern, int]
) -> List[Tuple[int, int]]:
    """
    Find all positions of a specific pattern (RESite) in a given text using regular expressions.

    Parameters:
        text (str): The text to search in.
        Enzyme (Tuple[str, int]): The restriction enzyme site to search for, with the length of give_site or accept_site
        depend of the

    Examples:
        >>> find_positions_for_one_site_borderless("777777GA7TA7TC1717GA7TA7TC", (re.compile("GA.TA.TC"), 4))
        [[6, 4], [18, 4]]
    """
    regex, offset = Enzyme
    return [[m.start(), offset] for m in regex.finditer(text)]


def find_all_pos_borderless(
    text: str,
    ligation_site_list: List[Tuple[str, int]],
) -> List[int]:
    """
    Find all positions of a specific pattern (RESite) in a given text using regular expressions.

    Examples:
        >>> find_all_pos_borderless("777777GA7TA7TC1717GAATTCFFFFFF", [(re.compile("GAATTC"), 5), (re.compile("GA.TA.TC"), 4)])
        [[6, 4], [18, 5], [30, 0]]
    """
    AllSite = []
    for TupleRegex in ligation_site_list:
        AllSite += find_positions_for_one_site_borderless(text, TupleRegex)
    AllSite = AllSite + [[len(text), 0]]

    return sorted(AllSite, key=lambda x: x[0])


def IndexFragList_borderless(all_index_list, seed_size):
    """
    Find fragments position from a given list of indices

    If the fragment is shorter than the seed size, it is discarded
    If the fragment is longer than the seed size, it is added to the list

    The border corresponding to ligation site are discared

    Examples:
        >>> IndexFragList_borderless([[5, 4], [18, 5], [30, 0]], 6)
        [[9, 18], [23, 30]]
    """
    ListFragListIndex = []
    i = 0
    previous_position = 0

    # Skip border corresponding to ligation site in the list
    for i, value in enumerate(all_index_list):

        previous_border_len = all_index_list[i - 1][1]
        current_position = all_index_list[i][0]

        # Update value
        Start = int(previous_position + previous_border_len)
        End = current_position

        # Add fragment to the list if it is long enough
        if (End - Start) >= seed_size:
            ListFragListIndex.append([Start, End])

        # Update value :
        previous_position = current_position

    return ListFragListIndex


def index_list_single_borderless(
    sequence: str, ligation_site_list: List[Tuple[str, int]], seed_size
) -> List[List[int]]:
    """
    _summary_ : Find index position of fragments produce by digestion of
    sequences according to seed size

    :param sequence: _description_
    :param ligation_site_list: _description_
    :param seed_size: _description_
    :return: _description_
    """
    IndexPositions = find_all_pos_borderless(sequence, ligation_site_list)
    FragmentList = IndexFragList_borderless(IndexPositions, seed_size)
    return FragmentList


def index_list_borderless(
    Sequence: str,
    ligation_site_list,
    seed_size,
) -> List[str]:
    """
    _summary_ : Retrieve the index of the fragment sequence using the ligation
    sites and the seed size and without border (ligation site)

    :param seed_size: Minimal lenght of fragment
    :return: List of sequence fragment

    Examples:
        >>> index_list_borderless(["111111GAATTC222222", "111GAATTC222222"], [(re.compile("GAATTC"), 6)], 0)
        ([[0, 6], [12, 18]], [[0, 3], [9, 15]])
    """
    ListFragmentFor = index_list_single_borderless(
        Sequence[0], ligation_site_list, seed_size
    )
    ListFragmentRev = index_list_single_borderless(
        Sequence[1], ligation_site_list, seed_size
    )

    return ListFragmentFor, ListFragmentRev


############################# End Borderless ##################################


###############################  Classic part #################################


def find_positions_for_one_site(
    text: str, Enzyme: Tuple[str, int]
) -> List[int]:
    """
    Find all positions of a specific pattern (RESite) in a given text using regular expressions.

    Parameters:
        text (str): The text to search in.
        Enzyme (Tuple[str, int]): The restriction enzyme site to search for, with the length of give_site or accept_site
        depend of the

    Examples:
        >>> find_positions_for_one_site("AAGAATTCAA", (re.compile("GAATTC"), 5))
        [7]
        >>> find_positions_for_one_site("AAAAAGAATTCAAAAAGAATTCAAAAAGAATTC", (re.compile("GAATTC"), 5))
        [10, 21, 32]
        >>> find_positions_for_one_site("777777GA7TA7TC1717GA7TA7TC", (re.compile("GA.TA.TC"), 4))
        [10, 22]
    """
    return [
        int(match.start() + Enzyme[1])
        for match in re.finditer(Enzyme[0], text)
    ]


def find_all_pos(
    text: str, ligation_site_list: List[Tuple[re.Pattern, int]]
) -> List[int]:
    """
    Find all positions of a specific pattern (RESite) in a given text using regular expressions.

    Examples:
        >>> find_all_pos("777777GA7TA7TC1717GAATTCFFFFFF", [(re.compile("GAATTC"), 5), (re.compile("GA.TA.TC"), 4)])
        [[6, 4], [18, 5], [30, 0]]
    """
    AllSite = [0] + list(
        map(int, find_positions_for_one_site(text, ligation_site_list[0]))
    )
    if len(ligation_site_list) > 1:
        for TupleRegex in ligation_site_list[1:]:
            AllSite += list(
                map(int, find_positions_for_one_site(text, TupleRegex))
            )
    AllSite = [0] + AllSite + [len(text)]
    AllSite.sort()
    return AllSite


def IndexFragList(index_list, seed_size):
    """
    _summary_ : Find the index of the fragment which respect the minimum seed
    size

    """
    ListFragListIndex = []
    for i in range(len(index_list)):
        if i > 0:
            frag_size = index_list[i] - index_list[i - 1]
            if frag_size > seed_size:
                FragIndex = [index_list[i - 1], index_list[i]]
                ListFragListIndex.append(FragIndex)
    return ListFragListIndex


def index_list_single(
    sequence: str, ligation_site_list: List[Tuple[str, int]], seed_size
) -> List[List[int]]:
    """
    _summary_ : Find index position of fragments produce by digestion of
    sequences according to seed size
    """
    IndexPositions = find_all_pos(sequence, ligation_site_list)
    FragmentList = IndexFragList(IndexPositions, seed_size)
    return FragmentList


def index_list(
    Sequence: List[str],
    ligation_site_list: List[Tuple[re.Pattern, int]],
    seed_size,
) -> Tuple[List[List[int]]]:
    """
    _summary_ : Find the index of the fragment for forward and
    reverse sequences

    Examples:
        >>> index_list(["111111GAATTC222222", "111GAATTC222222"], [(re.compile("GAATTC"), 3)], 0)
        ([[0, 9], [9, 18]], [[0, 6], [6, 15]])
    """
    ListFragmentFor = index_list_single(
        Sequence[0], ligation_site_list, seed_size
    )
    ListFragmentRev = index_list_single(
        Sequence[1], ligation_site_list, seed_size
    )

    return ListFragmentFor, ListFragmentRev


################################ Mode All #####################################


def Create_Pairs_All(
    Sequence, seed_size, ligation_site_list, indexation
) -> Generator:
    """
    Create all possible pairs of fragments from given sequences.

    Parameters:
        Sequence (List[str]): List containing forward and reverse sequences.
        seed_size (int): Minimum size of the fragment to be considered.
        ligation_site_list (List[Tuple[re.Pattern, int]]): List of ligation sites with regex patterns and offsets.

    Yields:
        List: A list containing:
            - A unique identifier for the pair.
            - Information about the first fragment and which sequence it comes from (forward or reverse).
            - Information about the second fragment and which sequence it comes from (forward or reverse).
    """
    ListFragmentFor, ListFragmentRev = indexation(
        Sequence, ligation_site_list, seed_size
    )
    AllFrag = ListFragmentFor + ListFragmentRev
    NbFragFor = len(ListFragmentFor)
    for i, fragI in enumerate(AllFrag):
        for j, fragJ in enumerate(AllFrag):
            if i < j:
                if i < NbFragFor:
                    WhichFragFor = 0
                    SenseFor = 1
                else:
                    WhichFragFor = 1
                    SenseFor = -1
                if j < NbFragFor:
                    WhichFragRev = 0
                    SenseRev = -1
                else:
                    WhichFragRev = 1
                    SenseRev = 1

                Num = str(i) + str(j)
                if ((fragI[1] - fragI[0]) > seed_size) and (
                    (fragJ[1] - fragJ[0]) > seed_size
                ):
                    yield [
                        Num,
                        [fragI, WhichFragFor, SenseFor],
                        [fragJ, WhichFragRev, SenseRev],
                    ]


def processing_All(
    Name, Sequence, Quality, ligation_site_list, seed_size, indexation
):
    """
    Process the sequences to generate buffers for forward and reverse reads.

    Parameters:
        Name (str): Name of the read.
        Sequence (List[str]): List containing forward and reverse sequences.
        Quality (List[str]): List containing quality scores for forward and reverse sequences.
        seed_size (int): Minimum size of the fragment to be considered.
        ligation_site_list (List[Tuple[re.Pattern, int]]): List of ligation sites with regex patterns and offsets.

    Returns:
        Tuple[List[str], List[str]]: Buffers for forward and reverse reads with new names and sequences.
    """
    bufferF = []
    bufferR = []

    for BlocDePairs in Create_Pairs_All(
        Sequence, seed_size, ligation_site_list, indexation
    ):
        # Conservation of sense Forward and Reverse
        PremiereSeq = BlocDePairs[1][1]
        SenseFor = BlocDePairs[1][2]
        DeuxiemeSeq = BlocDePairs[2][1]
        SenseRev = BlocDePairs[2][2]

        # If you want understand this, see the comment after :
        NewName = str(Name.split(" ")[0]) + ":" + str(BlocDePairs[0])
        bufferF.append(
            f"{NewName}\n{Sequence[PremiereSeq][BlocDePairs[1][0][0]:BlocDePairs[1][0][1]][::SenseFor]}\n+\n{Quality[PremiereSeq][BlocDePairs[1][0][0]:BlocDePairs[1][0][1]][::SenseFor]}\n"
        )

        bufferR.append(
            f"{NewName}\n{Sequence[DeuxiemeSeq][BlocDePairs[2][0][0]:BlocDePairs[2][0][1]][::SenseRev]}\n+\n{Quality[DeuxiemeSeq][BlocDePairs[2][0][0]:BlocDePairs[2][0][1]][::SenseRev]}\n"
        )

    return bufferF, bufferR


"""
    For comprehensive explanation :

    BlocDePairs =   [Num,
                    [[StartIndex, EndIndex], CommingFromForwardOrReverse, ReverseOrNot],
                    [[StartIndex, EndIndex], CommingFCommingFromForwardOrReverseromReverse, ReverseOrNot]]


    bufferF = NewName
              Sequence[CommingFromForwardOrReverse][Index_Fragment][ReverseOrNot]
              +
              Qualitie[CommingFromForwardOrReverse][Index_Fragment][ReverseOrNot]
"""


################################ Mode FR #####################################


def Create_Pairs_Fr(
    fragments: List[List[int]],
) -> Generator[List[str | List[int]], None, None]:
    """
    Create pairs of forward and reverse fragments.

    Parameters:
        fragments (List[List[List[int]]]): List containing forward and reverse fragments. Each fragment is a list of start and end indices.

    Yields:
        List: A list containing:
            - A unique identifier for the pair.
            - The forward fragment indices.
            - The reverse fragment indices.

    """
    forward_fragments = fragments[0]
    reverse_fragments = fragments[1]

    for i, index_f_frag in enumerate(forward_fragments):
        for j, index_r_frag in enumerate(reverse_fragments):
            Num = str(i) + str(j)
            yield [Num, index_f_frag, index_r_frag]


def processing_Fr(
    TNom, TSeq, TQual, ligation_site_list, seed_size, indexation
) -> Tuple[List[str], List[str]]:
    """
    Process the sequences to generate buffers for forward and reverse reads based on fragment pairs.

    Parameters:
        item (Tuple[List[str], List[str], List[str]]): A tuple containing:
            - List of names.
            - List of sequences (forward and reverse).
            - List of quality scores (forward and reverse).
        ligation_site_list (List[Tuple[re.Pattern, int]]): List of ligation sites with regex patterns and offsets.
        seed_size (int): Minimum size of the fragment to be considered.

    Returns:
        Tuple[List[str], List[str]]: Buffers for forward and reverse reads with new names and sequences.
    """
    bufferF = []
    bufferR = []

    ListFrag = indexation(TSeq, ligation_site_list, seed_size)

    Currents_Pairs = Create_Pairs_Fr(ListFrag)

    for Current_Pair in Currents_Pairs:
        Num, index_f_frag, index_r_frag = Current_Pair

        NewName = str(TNom.split(" ")[0]) + ":" + str(Num)
        bufferF.append(
            f"{NewName}\n{TSeq[0][index_f_frag[0]:index_f_frag[1]]}\n+\n{TQual[0][index_f_frag[0]:index_f_frag[1]]}\n"
        )
        bufferR.append(
            f"{NewName}\n{TSeq[1][index_r_frag[0]:index_r_frag[1]]}\n+\n{TQual[1][index_r_frag[0]:index_r_frag[1]]}\n"
        )

    return bufferF, bufferR


################################ Common #####################################


def process_items(
    Input_Buffer,
    Output_buffer,
    ligation_site_list,
    seed_size,
    buffer_size,
    mode,
    borderless,
):
    """
    _summary_ : Process the sequences to generate FastQ sequences paired
    """
    BigBufferF = []
    BigBufferR = []

    if borderless:
        indexation = index_list_borderless
    else:
        indexation = index_list

    if mode == "all":
        Treatment = processing_All
    else:
        Treatment = processing_Fr

    while True:
        try:
            Items = Input_Buffer.get()
            if Items is None:
                break

            for item in Items:
                # Run the synchronous processing in a separate process
                bufferF, bufferR = Treatment(
                    item[0][0],
                    item[1],
                    item[2],
                    ligation_site_list,
                    seed_size,
                    indexation,
                )

                BigBufferF.extend(bufferF)
                BigBufferR.extend(bufferR)

                if len(BigBufferF) > buffer_size:
                    Output_buffer.put([BigBufferF, BigBufferR])
                    BigBufferF = []
                    BigBufferR = []

        except Exception as e:
            logging.error(f"Error in process items : {e}")

    if BigBufferF or BigBufferR:
        Output_buffer.put([BigBufferF, BigBufferR])
    Output_buffer.put(None)
