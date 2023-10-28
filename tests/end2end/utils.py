#!/usr/bin/env python
# Copyright 2017-2020 IBM Corp. All Rights Reserved.
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

import os
import time
import logging
import warnings
import pytest
import zhmcclient


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


def setup_logging(enable_logging, testfunc_name, log_file=None):
    """
    Set up logging for end2end testcases.

    If enable_logging is True, two loggers are created and enabled for logging
    to the specified log_file:
      * A logger named "zhmcclient.hmc" for logging the HMC interactions.
        That logger is used by the zhmcclient package.
      * A logger named testfunc_name for logging additional information the
        test function may need to log. This logger is returned.
    Because this setup function is called for each invocation of a test
    function, it ends up being called multiple times within the same Python
    process. Therefore, the loggers are set up only when they do not exist yet.

    If enable_logging is False, the same two loggers are created and logging
    is disabled on them by setting the log level to NOTSET. The testfunc_name
    logger is also returned in this case.

    Returns:
        logging.Logger: Logger for testfunc_name
    """
    # log level and format for both loggers
    log_level = logging.DEBUG
    log_format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    datetime_format = '%Y-%m-%d %H:%M:%S %Z'
    log_converter = time.gmtime

    zhmcclient_logger = logging.getLogger(zhmcclient.HMC_LOGGER_NAME)
    testfunc_logger = logging.getLogger(testfunc_name)

    if enable_logging:
        assert log_file

        abs_log_file = os.path.abspath(log_file)

        zhmcclient_handler = None
        for handler in zhmcclient_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                bfn = handler.baseFilename  # pylint: disable=no-member
                abs_handler_file = os.path.abspath(bfn)
                if abs_handler_file == abs_log_file:
                    zhmcclient_handler = handler
                    break
        if not zhmcclient_handler:
            zhmcclient_handler = logging.FileHandler(log_file)
            zhmcclient_logger.addHandler(zhmcclient_handler)

        testfunc_handler = None
        for handler in testfunc_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                bfn = handler.baseFilename  # pylint: disable=no-member
                abs_handler_file = os.path.abspath(bfn)
                if abs_handler_file == abs_log_file:
                    testfunc_handler = handler
                    break
        if not testfunc_handler:
            testfunc_handler = logging.FileHandler(log_file)
            testfunc_logger.addHandler(testfunc_handler)

        logging.Formatter.converter = log_converter
        formatter = logging.Formatter(
            log_format, datefmt=datetime_format)

        zhmcclient_handler.setFormatter(formatter)
        testfunc_handler.setFormatter(formatter)

        zhmcclient_logger.setLevel(log_level)
        testfunc_logger.setLevel(log_level)

    else:
        zhmcclient_logger.setLevel(logging.NOTSET)
        testfunc_logger.setLevel(logging.NOTSET)

    return testfunc_logger


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
