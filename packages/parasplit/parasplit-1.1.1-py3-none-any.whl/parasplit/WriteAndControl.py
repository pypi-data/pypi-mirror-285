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
import signal
import subprocess
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)


def signal_handler(sig, frame, outF, outR):
    print(f"\nReceived signal {sig}. Terminating gracefully...")
    outF.terminate()  # Terminate the pigz processes
    outR.terminate()
    logging.info("\nProcess termination requested by signal")
    sys.exit(0)


def OpenOutput(TWrite, output_forward, output_reverse):
    # Open output files for writing
    outF = subprocess.Popen(
        ["pigz", "-c", "-p", str(TWrite)],
        stdin=subprocess.PIPE,
        stdout=open(output_forward, "wb"),
    )
    outR = subprocess.Popen(
        ["pigz", "-c", "-p", str(TWrite)],
        stdin=subprocess.PIPE,
        stdout=open(output_reverse, "wb"),
    )

    # Register signal handlers
    signal.signal(
        signal.SIGINT,
        lambda sig, frame: signal_handler(sig, frame, outF, outR),
    )  # Ctrl+C
    signal.signal(
        signal.SIGTSTP,
        lambda sig, frame: signal_handler(sig, frame, outF, outR),
    )  # Ctrl+Z

    return outF, outR


def ManagePigzProblems(outF, outR, output_forward, output_reverse):
    outF.stdin.close()
    outR.stdin.close()
    outF.wait()
    outR.wait()

    stdoutF, stderrF = outF.communicate()
    if stderrF:
        print(
            f"Error in pigz command for file {output_forward}: {stderrF}",
            flush=True,
        )

    stdoutR, stderrR = outR.communicate()
    if stderrR:
        print(
            f"Error in pigz command for file {output_reverse}: {stderrR}",
            flush=True,
        )


def write_pairs(
    Output_buffer,
    outF: subprocess.Popen,
    outR: subprocess.Popen,
    TFrag,
) -> None:
    finished_processes = 0
    while finished_processes < TFrag:
        try:
            data = Output_buffer.get()
            if data is None:
                finished_processes += 1
            else:
                outF.stdin.write("".join(data[0]).encode("utf-8"))
                outR.stdin.write("".join(data[1]).encode("utf-8"))

        except Exception as e:
            logging.error(f"Error in write_pairs: {e}")
