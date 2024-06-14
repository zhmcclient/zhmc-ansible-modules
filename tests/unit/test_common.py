#!/usr/bin/env python
# Copyright 2023 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Unit tests for the 'module_utils.common' Python module.
"""


import re
import pytest

from plugins.module_utils import common


COMMON_PARSE_HMC_HOST_TESTCASES = [
    # Testcases for test_partition_create_check_mode_partition()
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - in_hmc_host (str or list of str): Input hmc_host
    # - exp_hmc_host (str): Expected hmc_host
    # - exp_exc_type: Expected exception type, or None for no exc. expected.
    # - exp_exc_pattern: Expected exception message pattern, or None for no
    #   exception expected.

    (
        "hmc_host parameter as IP address string",
        '10.11.12.13',
        '10.11.12.13',
        None,
        None,
    ),
    (
        "hmc_host parameter as hostname string",
        'myhmc',
        'myhmc',
        None,
        None,
    ),

    (
        "hmc_host parameter as list with one IP address string",
        ['10.11.12.13'],
        ['10.11.12.13'],
        None,
        None,
    ),
    (
        "hmc_host parameter as list with one hostname string",
        ['myhmc'],
        ['myhmc'],
        None,
        None,
    ),
    (
        "hmc_host parameter as list with two items",
        ['10.11.12.13', 'myhmc'],
        ['10.11.12.13', 'myhmc'],
        None,
        None,
    ),

    (
        "hmc_host parameter as stringified list with one IP address string",
        "['10.11.12.13']",
        ['10.11.12.13'],
        None,
        None,
    ),
    (
        "hmc_host parameter as stringified list with one hostname string",
        "['myhmc']",
        ['myhmc'],
        None,
        None,
    ),
    (
        "hmc_host parameter as stringified list with two items",
        "['10.11.12.13', 'myhmc']",
        ['10.11.12.13', 'myhmc'],
        None,
        None,
    ),
    (
        "hmc_host parameter as stringified list with two items - no space",
        "['10.11.12.13','myhmc']",
        ['10.11.12.13', 'myhmc'],
        None,
        None,
    ),
    (
        "hmc_host parameter as stringified list with two items - more spaces",
        "[ '10.11.12.13',  'myhmc' ]",
        ['10.11.12.13', 'myhmc'],
        None,
        None,
    ),
    (
        "hmc_host parameter as stringified list with two items - diff. quotes",
        '["10.11.12.13", \'myhmc\']',
        ['10.11.12.13', 'myhmc'],
        None,
        None,
    ),
]


@pytest.mark.parametrize(
    "desc, in_hmc_host, exp_hmc_host, exp_exc_type, exp_exc_pattern",
    COMMON_PARSE_HMC_HOST_TESTCASES)
def test_common_parse_hmc_host(
        desc, in_hmc_host, exp_hmc_host, exp_exc_type, exp_exc_pattern):
    """
    Test the parse_hmc_host() function.
    """

    if exp_exc_type:
        with pytest.raises(exp_exc_type) as exc_info:

            # The code to be tested
            common.parse_hmc_host(in_hmc_host)

        exc_msg = str(exc_info.value)
        if exp_exc_pattern:
            assert re.match(exp_exc_pattern, exc_msg)

    else:

        # The code to be tested
        hmc_host = common.parse_hmc_host(in_hmc_host)

        assert hmc_host == exp_hmc_host
