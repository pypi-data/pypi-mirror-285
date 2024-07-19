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

import argparse
import logging
import sys
from multiprocessing import Process, Queue
from typing import List
from .Frag import process_items
from .Read import read_fastq_gzip_simultaneously_MyWay
from .Pretreatment import SearchInDataBase, Partitionning
from .WriteAndControl import OpenOutput, ManagePigzProblems, write_pairs


# Setup logging
logging.basicConfig(level=logging.INFO)


def cut(
    source_forward: str,
    source_reverse: str,
    output_forward: str,
    output_reverse: str,
    list_enzyme: List[str],
    mode,
    seed_size,
    buffer_size: int = 200,
    num_threads: int = 8,
    borderless: bool = False,
) -> None:
    """
    Main function to process sequences based on enzyme restriction sites.

    Parameters:
        source_forward (str): Input file path for forward reads.
        source_reverse (str): Input file path for reverse reads.
        output_forward (str): Output file path for processed forward reads.
        output_reverse (str): Output file path for processed reverse reads.
        list_enzyme (List[str]): List of restriction enzymes.
        mode (str): Mode of pairing fragments, "all" or "fr".
        seed_size (int): Minimum length of fragments to keep.
        buffer_size (int, optional): Size of buffer. Defaults to 200.
        num_threads (int, optional): Number of threads to use for processing. Defaults to 8.
        borderless (bool, optional): Whether to discard ligation sites (borders). Defaults to False.

    Returns:
        None
    """
    # Threads allocations :
    TWrite, TRead, TFrag = Partitionning(num_threads)

    # Take the enzyme list and make the ligation site list
    ligation_site_list = SearchInDataBase(list_enzyme, borderless)

    try:
        # Open output files for writing
        outF, outR = OpenOutput(TWrite, output_forward, output_reverse)

        # Input and Output Queues
        Input_Buffer = Queue()
        Output_buffer = Queue()

        # Process for reading fastq files
        def read_process():
            read_fastq_gzip_simultaneously_MyWay(
                source_forward, source_reverse, Input_Buffer, TRead, TFrag
            )

        # Process for processing items
        def process_process_all():
            process_items(
                Input_Buffer,
                Output_buffer,
                ligation_site_list,
                seed_size,
                buffer_size,
                mode,
                borderless,
            )

        # Process for writing pairs
        def write_process():
            write_pairs(Output_buffer, outF, outR, TFrag)

        # Read fastq files in parallel and asynchronous
        read_p = Process(target=read_process)

        # Choose mode and Create the executor and dispatch work to it
        if mode == "all":
            print("Mode ALL selected")
            process_p_list = [
                Process(target=process_process_all) for _ in range(TFrag)
            ]
        elif mode == "fr":
            print("Mode FR selected")
            process_p_list = [
                Process(target=process_process_all) for _ in range(TFrag)
            ]
        else:
            print(f"Unknown mode: {mode}")
            sys.exit(1)

        # Create asynchronous writing
        write_p = Process(target=write_process)

        # Start processes
        read_p.start()
        for p in process_p_list:
            p.start()
        write_p.start()

        # Wait for all processes to finish
        read_p.join()
        for p in process_p_list:
            p.join()
        write_p.join()

        # Close output files and streams
        ManagePigzProblems(outF, outR, output_forward, output_reverse)

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Terminating...")
        sys.exit(0)


def main_cli():
    parser = argparse.ArgumentParser(
        description="""\
Cutsite script

Features:

    Find and Utilize Restriction Enzyme Sites: Automatically identify ligation sites from provided enzyme names and generate regex patterns to locate these sites in sequences.
    Fragmentation: Split sequences at restriction enzyme sites, creating smaller fragments.
    Multi-threading: Efficiently handle large datasets by utilizing multiple threads for decompression, fragmentation, and compression.
    Custom Modes: Supports different pairing modes for sequence fragments.

Arguments:

    --source_forward (str): Input file path for forward reads. Default is ../data/source_forward.fq.gz.
    --source_reverse (str): Input file path for reverse reads. Default is ../data/source_reverse.fq.gz.
    --output_forward (str): Output file path for processed forward reads. Default is ../data/output_forward.fq.gz.
    --output_reverse (str): Output file path for processed reverse reads. Default is ../data/output_reverse.fq.gz.
    --list_enzyme (str): Comma-separated list of restriction enzymes. Default is No restriction enzyme found.
    --mode (str): Mode of pairing fragments. Options are "all" or "fr". Default is "fr" which means Forward/Reverse.
    --seed_size (int): Minimum length of fragments to keep. Default is 20.
    --num_threads (int): Number of threads to use for processing. Default is 4.
    -b, --borderless: Option to discard ligation sites (borders).
""",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-sf", "--source_forward",
        type=str,
        default="../data/source_forward.fq.gz",
        help="Input file for forward reads",
    )
    parser.add_argument(
        "-sr", "--source_reverse",
        type=str,
        default="../data/source_reverse.fq.gz",
        help="Input file for reverse reads",
    )
    parser.add_argument(
        "-of","--output_forward",
        type=str,
        default="../data/output_forward.fq.gz",
        help="Output file for forward reads",
    )
    parser.add_argument(
        "-or", "--output_reverse",
        type=str,
        default="../data/output_reverse.fq.gz",
        help="Output file for reverse reads",
    )
    parser.add_argument(
        "-le", "--list_enzyme",
        default="No restriction enzyme found",
        type=str,
        help="Restriction Enzyme(s) used separated by coma",
    )
    parser.add_argument(
        "-m", "--mode",
        type=str,
        default="fr",
        help="Mode of modification only : all or fr",
    )
    parser.add_argument(
        "-sz", "--seed_size",
        type=int,
        default="20",
        help="Minimum lengh of fragments conserved",
    )
    parser.add_argument(
        "-nt", "--num_threads", type=int, default="8", help="Number of threads to use"
    )
    parser.add_argument(
        "-b", "--borderless", action="store_true", help="Discard ligation sites (borders)"
    )

    args = parser.parse_args()

    cut(
        source_forward=args.source_forward,
        source_reverse=args.source_reverse,
        output_forward=args.output_forward,
        output_reverse=args.output_reverse,
        mode=args.mode,
        seed_size=args.seed_size,
        num_threads=args.num_threads,
        list_enzyme=args.list_enzyme,
        borderless=args.borderless,
    )
