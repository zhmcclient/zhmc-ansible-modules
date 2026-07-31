# Copyright 2026 IBM Corp. All Rights Reserved.
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
End2end tests for zhmc_http module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import uuid
from unittest import mock
import pytest
import urllib3
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_http
from .utils import mock_ansible_module, get_failure_msg

urllib3.disable_warnings()

# Print debug messages
DEBUG = False

LOG_FILE = 'zhmc_http.log' if DEBUG else None


def new_urole_name():
    """Return random unique user role name"""
    urole_name = f'test_{uuid.uuid4()}'
    return urole_name


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, response_body) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, response_body):
        return changed, response_body

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_http.AnsibleModule", autospec=True)
def test_zhmc_http_get(
        ansible_mod_cls, check_mode, hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test GET HTTP method
    """
    hd = hmc_session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    client = zhmcclient.Client(hmc_session)
    console = client.consoles.console

    faked_session = hmc_session if hd.mock_file else None

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'method': 'get',
        'uri': '/api/console/user-roles',
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_http.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, (
        f"Module failed with exit code {exit_code} and message:\n"
        f"{get_failure_msg(mod_obj)}")

    # Assert module output
    changed, response_body = get_module_output(mod_obj)
    assert changed is False

    urole_names = [urole['name'] for urole in response_body['user-roles']]

    exp_uroles = console.user_roles.list()
    assert len(exp_uroles) == len(urole_names)
    for exp_urole in exp_uroles:
        name = exp_urole.name
        assert name in urole_names


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_http.AnsibleModule", autospec=True)
def test_zhmc_http_post(
        ansible_mod_cls, check_mode, hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test POST HTTP method
    """
    hd = hmc_session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    client = zhmcclient.Client(hmc_session)
    console = client.consoles.console

    faked_session = hmc_session if hd.mock_file else None

    urole_name = new_urole_name()

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'method': 'post',
        'uri': '/api/console/user-roles',
        'request_body': {'name': urole_name},
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_http.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, (
        f"Module failed with exit code {exit_code} and message:\n"
        f"{get_failure_msg(mod_obj)}")

    created_urole = None
    try:

        # Assert module output
        changed, response_body = get_module_output(mod_obj)
        assert changed is True

        if check_mode:
            assert response_body is None
        else:
            assert 'object-uri' in response_body
            urole_uri = response_body['object-uri']
            found = False
            uroles = console.user_roles.list()
            for urole in uroles:
                if urole.uri == urole_uri:
                    found = True
                    created_urole = urole
                    assert urole.name == urole_name
                    break
            assert found is True

    finally:
        if created_urole:
            created_urole.delete()


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_http.AnsibleModule", autospec=True)
def test_zhmc_http_delete(
        ansible_mod_cls, check_mode, hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test DELETE HTTP method
    """
    hd = hmc_session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    client = zhmcclient.Client(hmc_session)
    console = client.consoles.console

    faked_session = hmc_session if hd.mock_file else None

    urole_name = new_urole_name()

    created_urole = console.user_roles.create(properties={'name': urole_name})

    try:

        # Prepare module input parameters (must be all required + optional)
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'method': 'delete',
            'uri': created_urole.uri,
            'log_file': LOG_FILE,
            '_faked_session': faked_session,
        }

        # Prepare mocks for AnsibleModule object
        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_http.main()
        exit_code = exc_info.value.args[0]

        # Assert module exit code
        assert exit_code == 0, (
            f"Module failed with exit code {exit_code} and message:\n"
            f"{get_failure_msg(mod_obj)}")

        # Assert module output
        changed, response_body = get_module_output(mod_obj)
        assert changed is True
        assert response_body is None

        if not check_mode:
            uroles = console.user_roles.list(
                filter_args={'object-uri': created_urole.uri})
            assert len(uroles) == 0

    finally:
        # Clean up in case the deletion via module did not work
        if created_urole:
            try:
                created_urole.delete()
            except zhmcclient.HTTPError:
                pass
