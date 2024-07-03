# Copyright 2024 IBM Corp. All Rights Reserved.
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
End2end tests for zhmc_versions module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest import mock
import pytest
import urllib3
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_versions
from .utils import mock_ansible_module, get_failure_msg

urllib3.disable_warnings()

# Print debug messages
DEBUG = False

LOG_FILE = 'zhmc_versions.log' if DEBUG else None


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, versions) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, versions):
        return changed, versions

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_versions(
        versions, exp_hmc_api_version, exp_hmc_api_features,
        exp_cpc_props_dict, exp_cpc_api_features_dict):
    """
    Assert the output of the zhmc_versions module.

    Parameters:

      exp_hmc_api_version(dict): Expected HMC APi version info, as the result
        of Client.query_api_version().

      exp_hmc_api_features(list): List of expected HMC API features.

      exp_cpc_props_dict(dict): Expected CPCs and their properties.
        Key: CPC name.
        Value: Dict of expected CPC properties (with hyphens in their names)

      exp_cpc_api_features_dict(dict): Expected CPCs and their API features.
        Key: CPC name.
        Value: List of expected CPC API features.
    """

    # Check against exp_hmc_api_version
    assert versions['hmc_name'] == exp_hmc_api_version['hmc-name']
    hmc_version_str = exp_hmc_api_version['hmc-version']
    hmc_version_info = list(map(int, hmc_version_str.split('.')))
    assert versions['hmc_version'] == hmc_version_str
    assert versions['hmc_version_info'] == hmc_version_info
    api_version_info = [
        exp_hmc_api_version['api-major-version'],
        exp_hmc_api_version['api-minor-version']]
    api_version_str = '{}.{}'.format(*api_version_info)
    assert versions['hmc_api_version'] == api_version_str
    assert versions['hmc_api_version_info'] == api_version_info

    # Check against exp_hmc_api_features
    assert isinstance(versions['hmc_api_features'], list)
    assert set(versions['hmc_api_features']) == set(exp_hmc_api_features)

    # Check against exp_cpc_props_dict and exp_cpc_api_features_dict
    assert len(versions['cpcs']) == len(exp_cpc_props_dict)
    assert len(versions['cpcs']) == len(exp_cpc_api_features_dict)
    for cpc_item in versions['cpcs']:

        assert 'name' in cpc_item
        cpc_name = cpc_item['name']
        assert cpc_name in exp_cpc_props_dict
        exp_cpc_props = exp_cpc_props_dict[cpc_name]
        assert cpc_name in exp_cpc_api_features_dict
        exp_cpc_api_features = exp_cpc_api_features_dict[cpc_name]
        assert cpc_item['name'] == exp_cpc_props['name']
        assert cpc_item['status'] == exp_cpc_props['status']
        assert cpc_item['has_unacceptable_status'] == \
            exp_cpc_props['has-unacceptable-status']
        assert cpc_item['dpm_enabled'] == exp_cpc_props['dpm-enabled']
        se_version_str = exp_cpc_props['se-version']
        se_version_info = list(map(int, se_version_str.split('.')))
        assert cpc_item['se_version'] == se_version_str
        assert cpc_item['se_version_info'] == se_version_info

        assert set(cpc_item['cpc_api_features']) == set(exp_cpc_api_features)


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@pytest.mark.parametrize(
    "cpc_filter", [
        pytest.param('all', id="cpc_filter=all"),
        pytest.param('first', id="cpc_filter=first"),
        pytest.param('none', id="cpc_filter=none"),
    ]
)
@mock.patch("plugins.modules.zhmc_versions.AnsibleModule", autospec=True)
def test_zhmc_versions(
        ansible_mod_cls, cpc_filter, check_mode,
        hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_versions module.
    """

    hd = hmc_session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    client = zhmcclient.Client(hmc_session)
    console = client.consoles.console

    faked_session = hmc_session if hd.mock_file else None

    # Determine the expected results
    exp_hmc_api_version = client.query_api_version()
    exp_hmc_api_features = console.list_api_features()
    exp_cpc_props_dict = {}  # key: CPC name, value: dict of CPC properties
    exp_cpc_api_features_dict = {}  # key: CPC name, value: list of CPC API feat
    if cpc_filter != 'none':
        first_cpc = None
        for cpc in client.cpcs.list():
            exp_cpc_props_dict[cpc.name] = dict(cpc.properties)
            exp_cpc_api_features_dict[cpc.name] = cpc.list_api_features()
            if cpc_filter == 'first':
                first_cpc = cpc
                break

    if cpc_filter == 'all':
        # Note: All optional params need to be provided, so here we set
        # the default explicitly.
        cpc_names = None
    elif cpc_filter == 'none':
        cpc_names = []
    else:
        assert cpc_filter == 'first'
        if first_cpc is None:
            pytest.skip("HMC does not manage any CPCs")
        cpc_names = [first_cpc.name]

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'cpc_names': cpc_names,
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_versions.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, \
        f"Module failed with exit code {exit_code} and message:\n" \
        f"{get_failure_msg(mod_obj)}"

    # Assert module output
    changed, versions = get_module_output(mod_obj)
    assert changed is False

    assert_versions(
        versions, exp_hmc_api_version, exp_hmc_api_features,
        exp_cpc_props_dict, exp_cpc_api_features_dict)
