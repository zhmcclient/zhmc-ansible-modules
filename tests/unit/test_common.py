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

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
import pytest
from immutable_views import DictView

from zhmcclient import BaseResource

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
    # pylint: disable=unused-argument
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


class DummyResource(BaseResource):
    """
    Dummy zhmcclient.BaseResource object that can be created without any
    parent or manager objects, for test purposes.

    It is good for accessing its 'properties' property, but not for much more.
    """

    def __init__(self, properties):
        # pylint: disable=super-init-not-called
        self._properties = dict(properties) if properties else {}


COMMON_UNDER_PROPS_TESTCASES = [
    # Testcases for test_common_under_props()
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - input: Input object
    # - exp_result: Expected result object
    # - exp_exc_type: Expected exception type, or None for no exc. expected.

    (
        "Empty plain dict",
        {},
        {},
        None,
    ),
    (
        "Empty DictView",
        DictView({}),
        {},
        None,
    ),
    (
        "Plain dict",
        {
            'prop-name-1': 'value-1',
            'prop_name_2': ['value-2a', 'value_2b'],
        },
        {
            'prop_name_1': 'value-1',
            'prop_name_2': ['value-2a', 'value_2b'],
        },
        None,
    ),
    (
        "Plain dict, 1 level recursive",
        {
            'prop-name-1': 'value-1',
            'prop_name_2': {
                'prop-name-3': 'value-3',
                'prop_name_4': ['value-4a', 'value_4b'],
            },
        },
        {
            'prop_name_1': 'value-1',
            'prop_name_2': {
                'prop_name_3': 'value-3',
                'prop_name_4': ['value-4a', 'value_4b'],
            },
        },
        None,
    ),
    (
        "DictView",
        DictView({
            'prop-name-1': 'value-1',
            'prop_name_2': ['value-2a', 'value_2b'],
        }),
        {
            'prop_name_1': 'value-1',
            'prop_name_2': ['value-2a', 'value_2b'],
        },
        None,
    ),
    (
        "DictView, 1 level recursive",
        DictView({
            'prop-name-1': 'value1',
            'prop_name_2': {
                'prop-name-3': 'value-3',
                'prop_name_4': ['value-4a', 'value_4b'],
            },
        }),
        {
            'prop_name_1': 'value1',
            'prop_name_2': {
                'prop_name_3': 'value-3',
                'prop_name_4': ['value-4a', 'value_4b'],
            },
        },
        None,
    ),
    (
        "List of strings (illegal)",
        ['prop-name-1', 'prop_name_2'],
        None,
        AttributeError,
    ),
]


@pytest.mark.parametrize(
    "desc, input, exp_result, exp_exc_type",
    COMMON_UNDER_PROPS_TESTCASES)
def test_common_under_props(desc, input, exp_result, exp_exc_type):
    # pylint: disable=unused-argument
    """
    Test the underscore_properties() function.
    """

    if exp_exc_type:
        with pytest.raises(exp_exc_type):

            # The code to be tested
            common.underscore_properties(input)

    else:

        # The code to be tested
        result = common.underscore_properties(input)

        assert result == exp_result


COMMON_UNDER_PROPS_LIST_TESTCASES = [
    # Testcases for test_common_under_props_list()
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - input: Input object
    # - exp_result: Expected result object
    # - exp_exc_type: Expected exception type, or None for no exc. expected.

    (
        "Empty list",
        [],
        [],
        None,
    ),
    (
        "List of one zhmcclient.BaseResource object",
        [
            DummyResource({
                'prop-name-1': 'value_1',
                'prop_name_2': ['value-2a', 'value_2b'],
            }),
        ],
        [
            {
                'prop_name_1': 'value_1',
                'prop_name_2': ['value-2a', 'value_2b'],
            },
        ],
        None,
    ),
    (
        "List of one zhmcclient.BaseResource object, 1 level recursive",
        [
            DummyResource({
                'prop-name-1': 'value_1',
                'prop_name_2': {
                    'prop-name-3': 'value_3',
                    'prop_name_4': ['value-4a', 'value_4b'],
                },
            }),
        ],
        [
            {
                'prop_name_1': 'value_1',
                'prop_name_2': {
                    'prop_name_3': 'value_3',
                    'prop_name_4': ['value-4a', 'value_4b'],
                },
            },
        ],
        None,
    ),
    (
        "Single zhmcclient.BaseResource object (illegal)",
        DummyResource({
            'prop-name-1': 'value_1',
            'prop_name_2': 'value-2',
        }),
        None,
        TypeError,
    ),
    (
        "List of strings (illegal)",
        ['prop-name-1', 'prop_name_2'],
        None,
        AttributeError,
    ),
]


@pytest.mark.parametrize(
    "desc, input, exp_result, exp_exc_type",
    COMMON_UNDER_PROPS_LIST_TESTCASES)
def test_common_under_props_list(desc, input, exp_result, exp_exc_type):
    # pylint: disable=unused-argument
    """
    Test the underscore_properties_list() function.
    """

    if exp_exc_type:
        with pytest.raises(exp_exc_type):

            # The code to be tested
            common.underscore_properties_list(input)

    else:

        # The code to be tested
        result = common.underscore_properties_list(input)

        assert result == exp_result


COMMON_HYPHEN_PROPS_TESTCASES = [
    # Testcases for test_common_hyphen_props()
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - input: Input object
    # - exp_result: Expected result object
    # - exp_exc_type: Expected exception type, or None for no exc. expected.

    (
        "Plain dict",
        {
            'prop-name-1': 'value1',
            'prop_name_2': 'value2',
        },
        {
            'prop-name-1': 'value1',
            'prop-name-2': 'value2',
        },
        None,
    ),
    (
        "Plain dict, 1 level recursive",
        {
            'prop-name-1': {
                'prop-name-3': 'value3',
                'prop_name_4': 'value4',
            },
            'prop_name_2': 'value2',
        },
        {
            'prop-name-1': {
                'prop-name-3': 'value3',
                'prop-name-4': 'value4',
            },
            'prop-name-2': 'value2',
        },
        None,
    ),
    (
        "Single zhmcclient.BaseResource object (illegal)",
        DummyResource({
            'prop-name-1': 'value1',
            'prop_name_2': 'value2',
        }),
        None,
        AttributeError,
    ),
    (
        "List of strings (illegal)",
        ['prop-name-1', 'prop_name_2'],
        None,
        AttributeError,
    ),
]


@pytest.mark.parametrize(
    "desc, input, exp_result, exp_exc_type",
    COMMON_HYPHEN_PROPS_TESTCASES)
def test_common_hyphen_props(desc, input, exp_result, exp_exc_type):
    # pylint: disable=unused-argument
    """
    Test the hyphen_properties() function.
    """

    if exp_exc_type:
        with pytest.raises(exp_exc_type):

            # The code to be tested
            common.hyphen_properties(input)

    else:

        # The code to be tested
        result = common.hyphen_properties(input)

        assert result == exp_result
