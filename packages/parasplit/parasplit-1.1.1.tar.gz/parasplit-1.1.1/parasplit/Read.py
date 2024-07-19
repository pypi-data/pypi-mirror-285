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
import subprocess

logging.basicConfig(level=logging.INFO)


def StopSignal(Queue, NumThreadFrag):
    """
    _summary_ : Add a stop signal to the queue for each thread
    """
    for _ in range(NumThreadFrag):
        Queue.put(None)


def read_fastq_gzip_simultaneously_MyWay(
    fileA: str, fileB: str, Queue, num_threads, NumThreadFrag
    ):
    """
    _summary_ : Read two fastq files simultaneously, decompress them with pigz,
    take a couple a read and put them into a queue by block
    """
    # Use pigz to decompress the input files
    procA = subprocess.Popen(
        ["pigz", "-dc", "-p", str(num_threads), fileA],
        stdout=subprocess.PIPE,
        text=True,
    )
    procB = subprocess.Popen(
        ["pigz", "-dc", "-p", str(num_threads), fileB],
        stdout=subprocess.PIPE,
        text=True,
    )

    Stacker = []
    try:
        while True:
            NomA = (procA.stdout.readline()).rstrip()
            seqA = (procA.stdout.readline()).rstrip()
            procA.stdout.readline()  # Skip +
            qualA = (procA.stdout.readline()).rstrip()

            NomB = (procB.stdout.readline()).rstrip()
            seqB = (procB.stdout.readline()).rstrip()
            procB.stdout.readline()  # Skip +
            qualB = (procB.stdout.readline()).rstrip()

            if not seqA or not seqB:
                break

            Stacker.append([[NomA, NomB], [seqA, seqB], [qualA, qualB]])

            if len(Stacker) > 10:
                Queue.put(Stacker)
                Stacker = []

        if len(Stacker) > 0:
            Queue.put(Stacker)
        Queue.put(None)

    except Exception as e:
        logging.error(f"Error in TakeOneItem: {e}")

    finally:
        StopSignal(Queue, NumThreadFrag)
        procA.wait()
        procB.wait()
