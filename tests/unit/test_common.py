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
from copy import deepcopy
from collections.abc import Sequence, Mapping, Set
from types import ModuleType
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


COMMON_PARAMS_DEEPCOPY_TESTCASES = [
    # Testcases for test_common_params_deepcopy()
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - in_params (dict): Input params

    (
        "Empty dict",
        {}
    ),
    (
        "Dict with string keys and immutable values",
        {
            'int': 1,
            'float': 1.1,
            'complex': (1.1 + 1.1j),
            'short str': 'foo',
            'long str': 'foo' * 100,
            'tuple int': (1, 2),
            'short bytes': b'foo',
            'long bytes': b'foo' * 100,
            'bool': True,
            'frozenset': frozenset({1, 2, 3}),
            'none': None,
        }
    ),
    (
        "Dict with string keys and mutable values",
        {
            'dict': {'a': 1},
            'list': ['a', 'b'],
            'set': ('a', 'b'),
        }
    ),
    (
        "Dict with string keys and values that cannot be deepcopy()'ed",
        {
            'module': re,
        }
    ),
]

# Types used in the testcases that are mutable
MUTABLE_TYPES = (list, dict, set)

# Types used in the testcases on which deepcopy() fails
DEEPCOPY_FAILS_TYPES = (ModuleType, )


def assert_disparate_equal(obj_a, obj_b):
    """
    Assert that obj_a and obj_b are equal but not identical (except when
    immutable).

    obj_a and obj_b must not have dependency loops.

    In other words, assert that the two objects are separate deep copies.
    """

    # Depending on the type, this checks for value equality or just same object
    assert obj_a == obj_b

    # Immutable types may be identical, mutable types must be disparate.
    if isinstance(obj_a, MUTABLE_TYPES):
        assert id(obj_a) != id(obj_b)

    # params_deepcopy() does not copy types where deepcopy() fails.
    if isinstance(obj_a, DEEPCOPY_FAILS_TYPES):
        assert id(obj_a) == id(obj_b)

    # For collections, check the items recursively
    if isinstance(obj_a, Sequence) and not isinstance(obj_a, (str, bytes)):
        for i, value_a in enumerate(obj_a):
            value_b = obj_b[i]
            assert_disparate_equal(value_a, value_b)
    elif isinstance(obj_a, Mapping):
        for key, value_a in obj_a.items():
            value_b = obj_b[key]
            assert_disparate_equal(value_a, value_b)
    elif isinstance(obj_a, Set):
        sorted_a = sorted(obj_a)
        sorted_b = sorted(obj_b)
        for i, value_a in enumerate(sorted_a):
            value_b = sorted_b[i]
            assert_disparate_equal(value_a, value_b)


@pytest.mark.parametrize(
    "desc, in_params",
    COMMON_PARAMS_DEEPCOPY_TESTCASES)
def test_common_params_deepcopy(desc, in_params):
    # pylint: disable=unused-argument
    """
    Test the params_deepcopy() function.
    """

    # The code to be tested
    params = common.params_deepcopy(in_params)

    assert_disparate_equal(params, in_params)


COMMON_BLANKED_PARAMS_TESTCASES = [
    # Testcases for test_common_blanked_params()
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - in_params (dict): Input params. Must not be None
    # - blanked_properties (list): Properties to be blanked out, may be None

    (
        "Params without hmc_auth or properties",
        {
            'state': 'bla',
        },
        None
    ),
    (
        "Params with hmc_auth that does not have sensitive items",
        {
            'state': 'bla',
            'hmc_auth': {'userid': 'user'},
        },
        None
    ),
    (
        "Params with hmc_auth that does have all sensitive items",
        {
            'state': 'bla',
            'hmc_auth': {
                'userid': 'user',
                'password': 'pass',
                'session_id': 'sid',
            },
        },
        None
    ),
    (
        "Params with properties but without blanked props specified",
        {
            'state': 'bla',
            'properties': {
                'name': 'foo',
            },
        },
        None
    ),
    (
        "Params with properties being None",
        {
            'state': 'bla',
            'properties': None,
        },
        None
    ),
    (
        "Params with properties with different blanked props specified",
        {
            'state': 'bla',
            'properties': {
                'name': 'foo',
            },
        },
        ['password']
    ),
    (
        "Params with properties with one blanked props specified",
        {
            'state': 'bla',
            'properties': {
                'name': 'foo',
                'password': 'pass',
            },
        },
        ['password']
    ),
    (
        "Params with properties with one blanked prop and excess blanked prop",
        {
            'state': 'bla',
            'properties': {
                'name': 'foo',
                'password': 'pass',
            },
        },
        ['password', 'extra']
    ),
]

BLANKED_PROPS_HMC_AUTH = ['password', 'session_id']


@pytest.mark.parametrize(
    "desc, in_params, blanked_properties",
    COMMON_BLANKED_PARAMS_TESTCASES)
def test_common_blanked_params(desc, in_params, blanked_properties):
    # pylint: disable=unused-argument
    """
    Test the blanked_params() function.
    """

    saved_params = common.params_deepcopy(in_params)

    # The code to be tested
    act_params = common.blanked_params(in_params, blanked_properties)

    # Check that the input parameters have not been changed
    assert_disparate_equal(in_params, saved_params)

    # Check that all dict items are still there.
    in_keys = sorted(in_params.keys())
    act_keys = sorted(act_params.keys())
    assert act_keys == in_keys

    # Check that the 'hmc_auth' item, if present, has its sensitive items
    # blanked out.
    if 'hmc_auth' in act_params:
        hmc_auth = act_params['hmc_auth']
        for pname in BLANKED_PROPS_HMC_AUTH:
            if pname in hmc_auth:
                assert hmc_auth[pname] == common.BLANKED_OUT

    # Check that the 'properties' item, if present, has its sensitive items
    # blanked out.
    if 'properties' in act_params and act_params['properties'] and \
            blanked_properties:
        properties = act_params['properties']
        for pname in blanked_properties:
            if pname in properties:
                assert properties[pname] == common.BLANKED_OUT


COMMON_BLANKED_DICT_TESTCASES = [
    # Testcases for test_common_blanked_dict()
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - in_dict (dict): Input dict. Must not be None
    # - blanked_properties (list): Prop to be blanked out. Must not be None

    (
        "Empty dict and empty blanked props",
        {},
        []
    ),
    (
        "Empty dict and one excess blanked prop",
        {},
        ['foo']
    ),
    (
        "Dict and empty blanked props",
        {
            'p1': 'v1',
            'p2': None,
        },
        []
    ),
    (
        "Dict and one matching blanked prop",
        {
            'p1': 'v1',
            'p2': None,
        },
        ['p1']
    ),
    (
        "Dict and one matching and one excess blanked prop",
        {
            'p1': 'v1',
            'p2': None,
        },
        ['p1', 'foo']
    ),
]


@pytest.mark.parametrize(
    "desc, in_dict, blanked_properties",
    COMMON_BLANKED_DICT_TESTCASES)
def test_common_blanked_dict(desc, in_dict, blanked_properties):
    # pylint: disable=unused-argument
    """
    Test the blanked_dict() function.
    """

    saved_dict = deepcopy(in_dict)

    # The code to be tested
    act_dict = common.blanked_dict(in_dict, blanked_properties)

    # Check that the input dict has not been changed
    assert_disparate_equal(in_dict, saved_dict)

    # Check that the returned dict did not get additional keys
    for pname in act_dict.keys():
        assert pname in in_dict

    # Check that the specified items have been blanked out, and that all other
    # items have unchanged values.
    for pname, in_value in in_dict.items():
        assert pname in act_dict
        act_value = act_dict[pname]
        if pname in blanked_properties:
            assert act_value == common.BLANKED_OUT
        else:
            assert act_value == in_value


COMMON_REMOVED_DICT_TESTCASES = [
    # Testcases for test_common_removed_dict()
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - in_dict (dict): Input dict. Must not be None
    # - removed_properties (list): Properties to be removed. Must not be None

    (
        "Empty dict and empty removed props",
        {},
        []
    ),
    (
        "Empty dict and one excess removed prop",
        {},
        ['foo']
    ),
    (
        "Dict and empty removed props",
        {
            'p1': 'v1',
            'p2': None,
        },
        []
    ),
    (
        "Dict and one matching removed prop",
        {
            'p1': 'v1',
            'p2': None,
        },
        ['p1']
    ),
    (
        "Dict and one matching and one excess removed prop",
        {
            'p1': 'v1',
            'p2': None,
        },
        ['p1', 'foo']
    ),
]


@pytest.mark.parametrize(
    "desc, in_dict, removed_properties",
    COMMON_REMOVED_DICT_TESTCASES)
def test_common_removed_dict(desc, in_dict, removed_properties):
    # pylint: disable=unused-argument
    """
    Test the removed_dict() function.
    """

    saved_dict = deepcopy(in_dict)

    # The code to be tested
    act_dict = common.removed_dict(in_dict, removed_properties)

    # Check that the input dict has not been changed
    assert_disparate_equal(in_dict, saved_dict)

    # Check that the returned dict did not get additional keys
    for pname in act_dict.keys():
        assert pname in in_dict

    # Check that the specified items have been removed, and that all other
    # items have unchanged values.
    for pname, in_value in in_dict.items():
        if pname in removed_properties:
            assert pname not in act_dict
        else:
            assert act_dict[pname] == in_value
