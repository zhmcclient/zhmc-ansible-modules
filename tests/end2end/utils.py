#!/usr/bin/env python
# Copyright 2017,2020 IBM Corp. All Rights Reserved.
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
Utility functions for end2end testing.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import warnings
import pytest


def mock_ansible_module(ansible_mod_cls, params, check_mode):
    """
    Prepare the mocked AnsibleModule object for the end2end test.

    Note: Since this is a mocked object, the argument_spec defined in the
    module is not applied, and the params must be the defaulted set of
    all parameters in the module's argument_spec.
    """
    mod_obj = ansible_mod_cls.return_value  # the mocked object
    mod_obj.params = params
    mod_obj.check_mode = check_mode
    mod_obj.fail_json.configure_mock(side_effect=SystemExit(1))
    mod_obj.exit_json.configure_mock(side_effect=SystemExit(0))
    return mod_obj


def get_failure_msg(mod_obj):
    """
    Return the module failure message, as a string (i.e. the 'msg' argument
    of the call to fail_json()).
    If the module succeeded, return None.
    """

    def func(msg):
        return msg

    if not mod_obj.fail_json.called:
        return None
    call_args = mod_obj.fail_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


class End2endTestWarning(UserWarning):
    """
    Python warning indicating an issue with an end2end test.
    """
    pass


def skip_warn(msg):
    """
    Issue an End2endTestWarning and skip the current pytest testcase with the
    specified message.
    """
    warnings.warn(msg, End2endTestWarning, stacklevel=2)
    pytest.skip(msg)


def set_resource_property(resource, name, value):
    """
    Set a property on a zhmcclient resource to a value and return the current
    value (retrieved freshly from the HMC).

    Parameters:

      resource (zhmcclient.BaseResource): The resource (e.g. LPAR).
      name (string): Name of the property.
      value (object): New value for the property.

    Returns:
      object: Old value of the property.

    Raises:
      zhmcclient.CeasedExistence: The resource no longer exists.
      zhmcclient.Error: Any zhmcclient exception can happen, except
        OperationTimeout and StatusTimeout.
    """
    resource.pull_full_properties()
    old_value = resource.get_property(name)
    resource.update_properties({name: value})
    return old_value


def get_hmc_auth(session):
    """
    Create and return the hmc_auth input parameter for testing ibm_zhmc Ansible
    modules from an HMC session.

    Parameters:

      session (zhmcclient.Session): HMC session object, providing all the data
        for the return value.

    Returns:

      dict: Dictionary with items that can be used for the hmc_auth input
      parameter for testing ibm_zhmc Ansible modules.
    """
    userid = session.userid
    password = session._password  # pylint: disable=protected-access
    ca_certs = session.verify_cert \
        if isinstance(session.verify_cert, str) else None
    verify = bool(session.verify_cert)
    hmc_auth = dict(userid=userid, password=password, ca_certs=ca_certs,
                    verify=verify)
    return hmc_auth
