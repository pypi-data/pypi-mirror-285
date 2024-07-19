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

import gzip
import os
import pytest
from parasplit.main import cut

@pytest.fixture(scope="module")
def setup_test_environment():
    # Ensure that the output directory for test exists
    os.makedirs("test/output_data", exist_ok=True)
    yield
    # Add any necessary post-test clean-up here


def check_file_content(output_file, expected_output_file):
    # Check that the content of the output file matches the expected result
    with gzip.open(output_file, "rt") as fA, gzip.open(expected_output_file, "rt") as fB:
        while True:
            nameA = fA.readline().rstrip()
            seqA = fA.readline().rstrip()
            fA.readline()  # Skip the '+'
            qualA = fA.readline().rstrip()

            nameB = fB.readline().rstrip()
            seqB = fB.readline().rstrip()
            fB.readline()  # Skip the '+'
            qualB = fB.readline().rstrip()
            
            assert (seqA == seqB) or (seqA[::-1] == seqB)
            
            if not seqA:
                break   
                
                
def test_process_file(setup_test_environment):
    # Paths to input and output files for the test
    input_file_forward = "test/input_data/R1.fq.gz"
    input_file_reverse = "test/input_data/R2.fq.gz"
    
    expected_output_file_forward_fr = "test/output_data/output_ref_R1.fq.gz"
    expected_output_file_reverse_fr = "test/output_data/output_ref_R2.fq.gz"  
    
    expected_output_file_forward_all = "test/output_data/output_ref_all_R1.fq.gz"
    expected_output_file_reverse_all = "test/output_data/output_ref_all_R2.fq.gz" 
    
    output_file_forward = "test/output_data/output_R1.fq.gz"
    output_file_reverse = "test/output_data/output_R2.fq.gz"

    # Execute your main function with the input files
    cut(
        input_file_forward,
        input_file_reverse,
        output_file_forward,
        output_file_reverse,
        ['DpnII'],
        0,
        "fr",
        4,
        False,
    )

    # Verify that the output file has been created
    assert os.path.exists(output_file_forward)
    assert os.path.exists(output_file_reverse)
    
    # Verify that the content of the output file matches the expected result in "fr" mode 
    check_file_content(output_file_reverse, expected_output_file_reverse_fr)
    check_file_content(output_file_forward, expected_output_file_forward_fr)
    
    
    # Execute your main function with the input files
    cut(
        input_file_forward,
        input_file_reverse,
        output_file_forward,
        output_file_reverse,
        ['DpnII'],
        0,
        "all",
        4,
        False,
    )
    
    # Verify that the content of the output file matches the expected result in "all" mode 
    check_file_content(output_file_reverse, expected_output_file_reverse_all)
    check_file_content(output_file_forward, expected_output_file_forward_all)

    # Clean up: remove the generated output files
    os.remove(output_file_reverse)
    os.remove(output_file_forward)

