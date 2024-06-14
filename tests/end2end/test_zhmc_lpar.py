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
End2end tests for zhmc_lpar module.
"""


import random
import pdb
import re

import pytest
from unittest import mock
import requests.packages.urllib3
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
from zhmcclient.testutils import classic_mode_cpcs  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_lpar
from plugins.module_utils.common import ensure_lpar_inactive, \
    ensure_lpar_active, ensure_lpar_loaded, pull_lpar_status
from .utils import mock_ansible_module, get_failure_msg, skip_warn, \
    setup_logging, set_resource_property


requests.packages.urllib3.disable_warnings()

# Print debug messages in tests
DEBUG = False

# Logging for zhmcclient HMC interactions and test functions
LOGGING = False
LOG_FILE = 'test_zhmc_lpar.log'

# LPAR properties that are not always present, but only under certain
LPAR_CONDITIONAL_PROPS = (
    'cpc-name',  # added in ?
    'se-version',  # added in ?
    'is-sub-capacity-boost-active',  # added in ?
    'is-secure-execution-enabled',  # added in ?
    'is-ziip-capacity-boost-active',  # added in ?
    'speed-boost',  # added in ?
    'ziip-boost',  # added in ?
    'has-important-unviewed-operating-system-messages',  # added in ?
    'last-used-load-type',  # added in ?
    'last-used-load-address',  # added in ?
    'last-used-load-parameter',  # added in ?
    'last-used-secure-boot',  # added in ?
    'last-used-world-wide-port-name',  # added in ?
    'last-used-logical-unit-number',  # added in ?
    'last-used-disk-partition-id',  # added in ?
    'last-used-operating-system-specific-load-parameters',  # added in ?
    'last-used-boot-record-location-cylinder',  # added in ?
    'last-used-boot-record-location-head',  # added in ?
    'last-used-boot-record-location-record',  # added in ?
    'last-used-boot-record-location-volume-label',  # added in ?
    'last-used-device-type',  # added in ?
    'last-used-load-program-type',  # added in ?
    'last-used-operation-type',  # added in ?
    'last-used-disk-partition-id-automatic',  # added in ?
    'last-used-boot-record-logical-block-address',  # added in ?
    'last-used-clear-indicator',  # added in ?
    'absolute-processing-capping',  # added in ?
    'partition-identifier',  # added in ?
    'processor-usage',  # added in ?
    'number-general-purpose-processors',  # added in ?
    'number-reserved-general-purpose-processors',  # added in ?
    'number-general-purpose-cores',  # added in ?
    'number-reserved-general-purpose-cores',  # added in ?
    'number-icf-processors',  # added in ?
    'number-reserved-icf-processors',  # added in ?
    'number-icf-cores',  # added in ?
    'number-reserved-icf-cores',  # added in ?
    'number-ifl-processors',  # added in ?
    'number-reserved-ifl-processors',  # added in ?
    'number-ifl-cores',  # added in ?
    'number reserved-ifl-cores',  # added in ?
    'number-ziip-processors',  # added in ?
    'number-reserved-ziip-processors',  # added in ?
    'number-ziip-cores',  # added in ?
    'number-reserved-ziip-cores',  # added in ?
    'absolute-aap-capping',  # added in ?
    'absolute-ifl-capping',  # added in ?
    'absolute-ziip-capping',  # added in ?
    'absolute-cf-capping',  # added in ?
    'initial-vfm-storage',  # added in ?
    'maximum-vfm-storage',  # added in ?
    'current-vfm-storage',  # added in ?
    'zaware-hostname',  # added in ?
    'zaware-master-userid',  # added in ?
    'zaware-master-pw',  # added in ?
    'zaware-network-info',  # added in ?
    'zaware-gateway-info',  # added in ?
    'zaware-dns-info',  # added in ?
    'ssc-hostname',  # added in ?
    'ssc-master-userid',  # added in ?
    'ssc-master-pw',  # added in ?
    'ssc-network-info',  # added in ?
    'ssc-gateway-info',  # added in ?
    'ssc-dns-info',  # added in ?
    'storage-central-allocation',  # added in ?
    'storage-expanded-allocation',  # added in ?
    'assigned-certificate-uris',  # added in ?
)
# LPAR properties that are never returned.
LPAR_WRITEONLY_PROPS = (
    'zaware-master-pw',
    'ssc-master-pw',
)

# Artificial LPAR properties (added by the module).
LPAR_ARTIFICIAL_PROPS = ()


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, properties) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, lpar):
        return changed, lpar

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_lpar_props(act_props, exp_props, where):
    """
    Assert the actual properties of an LPAR.

    Parameters:
      act_props(dict): Actual LPAR props to verify (with dashes).
      exp_props(dict): Expected LPAR properties (with dashes).
      where(string): Indicator about the testcase for assertion messages.
    """

    assert isinstance(act_props, dict), where  # Dict of User role props

    # Assert the expected property values
    for prop_name in exp_props:
        prop_name_hmc = prop_name.replace('_', '-')
        exp_value = exp_props[prop_name]
        act_value = act_props[prop_name]
        # For list properties, ignore the order of list items:
        if prop_name in ('acceptable-status',):
            exp_value = set(exp_value)
            act_value = set(act_value)
        where_prop = where + \
            ", Unexpected value of property {p!r}: Expected: {e!r}, " \
            "Actual: {a!r}". \
            format(p=prop_name_hmc, e=exp_value, a=act_value)
        assert act_value == exp_value, where_prop


def ensure_lpar_status(logger, lpar, iap, status):
    """
    Ensure that the LPAR is in the desired status, in order to prepare or
    clean up end2end tests.
    """
    if status == 'not-activated':
        ensure_lpar_inactive(logger, lpar, check_mode=False)
        status = pull_lpar_status(lpar)
        assert status == 'not-activated'
    elif status == 'not-operating':
        op_mode = iap.get_property('operating-mode')
        assert op_mode not in ('ssc', 'zaware'), (
            "Invalid testcase definition: LPAR {ln!r} has operating mode "
            "{om!r} and thus cannot be put into 'not-operating' status".
            format(ln=lpar.name, om=op_mode))
        saved_auto_load = iap.get_property('load-at-activation')
        iap.update_properties({'load-at-activation': False})
        ensure_lpar_active(
            logger, lpar, check_mode=False,
            activation_profile_name=lpar.name, timeout=60, force=True)
        iap.update_properties({'load-at-activation': saved_auto_load})
        status = pull_lpar_status(lpar)
        assert status == 'not-operating'
    else:
        assert status == 'operating', (
            "Invalid testcase definition: ensure_lpar_status() does not "
            "support getting LPAR {ln!r} into status {s!r}".
            format(ln=lpar.name, s=status))

        ensure_lpar_loaded(
            logger, lpar, check_mode=False, activation_profile_name=lpar.name,
            load_address=None, load_parameter=None, clear_indicator=True,
            store_status_indicator=False, timeout=60, force=True)
        status = pull_lpar_status(lpar)
        assert status == 'operating'


LPAR_STATE_TESTCASES = [
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - lpar_mode (string): Activation mode of the LPAR.
    # - ap_type (string): Type of activation profile to be used for
    #   activation_profile_name parm in Lpar.activate(): 'image', 'wrongimage',
    #   'load', None.
    # - nap_type (string): Type of activation profile to be used for
    #   'next-activation-profile-name' prop of LPAR: 'image', 'wrongimage',
    #   'load'.
    # - auto_load (bool): Value for 'load-at-activation' in image profile.
    # - initial_status (string): Initial status for LPAR.
    # - input_state (string): 'state' input parameter for zhmc_lpar module.
    # - input_kwargs (dict): additional input parameters for zhmc_lpar module.
    # - exp_msg (string): Expected message pattern in case of module failure,
    #   or None for module success.
    # - exp_status (string): Expected value of the 'status' property of the
    #   LPAR after the module succeeded or failed.
    # - exp_result (dict): HMC-formatted properties for expected properties in
    #   the module result after the module succeeded.
    # - exp_changed (bool): Boolean for expected 'changed' flag.
    # - run: Indicates whether the test should be run, or 'pdb' for debugger.

    (
        "Inactive general LPAR w/o auto-load, state=inactive, default parms, "
        "next profile is image",
        'general',
        None,
        'image',
        False,
        'not-activated',
        'inactive',
        dict(),
        None,
        'not-activated',
        {},
        False,
        True,
    ),
    (
        "Inactive general LPAR with auto-load, state=inactive, default parms, "
        "next profile is image",
        'general',
        None,
        'image',
        True,
        'not-activated',
        'inactive',
        dict(),
        None,
        'not-activated',
        {},
        False,
        True,
    ),
    (
        "Inactive general LPAR w/o auto-load, state=active, default parms, "
        "next profile is image",
        'general',
        None,
        'image',
        False,
        'not-activated',
        'active',
        dict(),
        None,
        'not-operating',
        {
            'status': 'not-operating',
        },
        True,
        True,
    ),
    (
        "Inactive general LPAR with auto-load, state=active, default parms, "
        "next profile is image",
        'general',
        None,
        'image',
        True,
        'not-activated',
        'active',
        dict(),
        None,
        'operating',
        {
            'status': 'operating',
        },
        True,
        True,
    ),
    (
        "Inactive general LPAR w/o auto-load, state=loaded, default parms, "
        "next profile is image",
        'general',
        None,
        'image',
        False,
        'not-activated',
        'loaded',
        dict(),
        None,
        'operating',
        {
            'status': 'operating',
        },
        True,
        True,
    ),
    (
        "Inactive general LPAR with auto-load, state=loaded, default parms, "
        "next profile is image",
        'general',
        None,
        'image',
        True,
        'not-activated',
        'loaded',
        dict(),
        None,
        'operating',
        {
            'status': 'operating',
        },
        True,
        True,
    ),
    (
        "Active general LPAR state=reset_clear, default parms",
        'general',
        None,
        'image',
        False,
        'not-operating',
        'reset_clear',
        dict(),
        None,
        'not-operating',
        {},
        True,
        True,
    ),
    (
        "Active general LPAR state=reset_normal, default parms",
        'general',
        None,
        'image',
        False,
        'not-operating',
        'reset_normal',
        dict(),
        None,
        'not-operating',
        {},
        True,
        True,
    ),
    (
        "Active general LPAR state=inactive, default parms",
        'general',
        None,
        'image',
        False,
        'not-operating',
        'inactive',
        dict(),
        None,
        'not-activated',
        {},
        True,
        True,
    ),

    (
        "Inactive Linux LPAR w/o auto-load, state=inactive, default parms, "
        "next profile is image",
        'linux-only',
        None,
        'image',
        False,
        'not-activated',
        'inactive',
        dict(),
        None,
        'not-activated',
        {},
        False,
        True,
    ),
    (
        "Inactive Linux LPAR with auto-load, state=inactive, default parms, "
        "next profile is image",
        'linux-only',
        None,
        'image',
        True,
        'not-activated',
        'inactive',
        dict(),
        None,
        'not-activated',
        {},
        False,
        True,
    ),
    (
        "Inactive Linux LPAR w/o auto-load, state=active, default parms, "
        "next profile is image",
        'linux-only',
        None,
        'image',
        False,
        'not-activated',
        'active',
        dict(),
        None,
        'not-operating',
        {
            'status': 'not-operating',
        },
        True,
        True,
    ),
    (
        "Inactive Linux LPAR with auto-load, state=active, default parms, "
        "next profile is image",
        'linux-only',
        None,
        'image',
        True,
        'not-activated',
        'active',
        dict(),
        None,
        'operating',
        {
            'status': 'operating',
        },
        True,
        True,
    ),
    (
        "Inactive Linux LPAR w/o auto-load, state=loaded, default parms, "
        "next profile is image",
        'linux-only',
        None,
        'image',
        False,
        'not-activated',
        'loaded',
        dict(),
        None,
        'operating',
        {
            'status': 'operating',
        },
        True,
        True,
    ),
    (
        "Inactive Linux LPAR with auto-load, state=loaded, default parms, "
        "next profile is image",
        'linux-only',
        None,
        'image',
        True,
        'not-activated',
        'loaded',
        dict(),
        None,
        'operating',
        {
            'status': 'operating',
        },
        True,
        True,
    ),
    (
        "Active Linux LPAR state=reset_clear, default parms",
        'linux-only',
        None,
        'image',
        False,
        'not-operating',
        'reset_clear',
        dict(),
        None,
        'not-operating',
        {},
        True,
        True,
    ),
    (
        "Active Linux LPAR state=reset_normal, default parms",
        'linux-only',
        None,
        'image',
        False,
        'not-operating',
        'reset_normal',
        dict(),
        None,
        'not-operating',
        {},
        True,
        True,
    ),
    (
        "Active Linux LPAR state=inactive, default parms",
        'linux-only',
        None,
        'image',
        False,
        'not-operating',
        'inactive',
        dict(),
        None,
        'not-activated',
        {},
        True,
        True,
    ),

    (
        "Inactive SSC LPAR, state=loaded, default parms, "
        "next profile is image",
        'ssc',
        None,
        'image',
        False,
        'not-activated',
        'loaded',
        dict(),
        None,
        'operating',
        {
            'status': 'operating',
        },
        True,
        True,
    ),
]


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        # pytest.param(True, id="check_mode=True"),
    ]
)
@pytest.mark.parametrize(
    "desc, lpar_mode, ap_type, nap_type, auto_load, initial_status, "
    "input_state, input_kwargs, exp_msg, exp_status, exp_result, exp_changed, "
    "run",
    LPAR_STATE_TESTCASES)
@mock.patch("plugins.modules.zhmc_lpar.AnsibleModule", autospec=True)
def test_zhmc_lpar_state(
        ansible_mod_cls,
        desc, lpar_mode, auto_load, ap_type, nap_type, initial_status,
        input_state, input_kwargs, exp_msg, exp_status, exp_result, exp_changed,
        run,
        check_mode,
        classic_mode_cpcs):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name, unused-argument
    """
    Test the zhmc_lpar module with different initial and target state.

    Note: These tests require that the following properties are present in the
    HMC inventory file for the CPC item of the HMC that is tested against:

    * 'loadable_lpars' - The names of LPARs for some operating modes, that
      properly reach the 'operating' status when activated under auto-load
      conditions. If this item is missing, all tests will be skipped.
      If the entries for certain operating modes are missing, the tests
      for these operating modes are skipped.

    * 'load_profiles' - The names of load profiles that can be used to properly
      load the corresponding LPARs in 'loadable_lpars'. If this item is
      missing, all tests will be skipped. If the entries for certain operating
      modes are missing, the load-profile related tests for these operating
      modes are skipped.

    Example::

        A01:
          . . .
          cpcs:
            P0000A01:           # <- CPC item of the HMC that is tested against
              machine_type: "3931"
              machine_model: "A01"
              dpm_enabled: false
              loadable_lpars:   # <- specific entry for this test
                general: "LP01"      # key: operating mode, value: LPAR name
                linux-only: "LP02
                ssc: "LP03"
              load_profiles:    # <- specific entry for this test
                general: "LP01LOAD"  # key: op. mode, value: load profile name
                linux-only: "LP02LOAD"
                ssc: "LP03LOAD"

    """
    if not classic_mode_cpcs:
        pytest.skip("HMC definition does not include any CPCs in classic mode")

    if not run:
        skip_warn("Testcase is disabled in testcase definition")

    logger = setup_logging(LOGGING, 'test_zhmc_lpar_state', LOG_FILE)

    for cpc in classic_mode_cpcs:
        assert not cpc.dpm_enabled

        session = cpc.manager.session
        hd = session.hmc_definition
        hmc_host = hd.host
        hmc_auth = dict(userid=hd.userid, password=hd.password,
                        ca_certs=hd.ca_certs, verify=hd.verify)

        faked_session = session if hd.mock_file else None

        # The following has no check since classic_mode_cpcs only contains
        # CPCs that have such an item:
        hd_cpc = hd.cpcs[cpc.name]

        try:
            loadable_lpars = hd_cpc['loadable_lpars']
        except KeyError:
            pytest.skip("Inventory file entry for HMC nickname {h!r} does not "
                        "have a 'loadable_lpars' property in its entry for "
                        "CPC {c!r}".
                        format(h=hd.nickname, c=cpc.name))
        try:
            load_profiles = hd_cpc['load_profiles']
        except KeyError:
            pytest.skip("Inventory file entry for HMC nickname {h!r} does not "
                        "have a 'load_profiles' property in its entry for "
                        "CPC {c!r}".
                        format(h=hd.nickname, c=cpc.name))

        try:
            lpar_name = loadable_lpars[lpar_mode]
        except (KeyError, TypeError):
            pytest.skip("Inventory file entry for HMC nickname {h!r} does not "
                        "have an entry for operating mode {om!r} in its "
                        "'loadable_lpars' property for CPC {c!r}".
                        format(h=hd.nickname, c=cpc.name, om=lpar_mode))

        # Find the image profile corresponding to the LPAR, and the other
        # (wrong) image profile names for specific tests with that.
        iap_name = lpar_name
        all_iaps = cpc.image_activation_profiles.list()
        lpar_iaps = [_iap for _iap in all_iaps if _iap.name == lpar_name]
        if len(lpar_iaps) >= 1:
            iap = lpar_iaps[0]
        else:
            pytest.skip("Image activation profile {p!r} does not exist on "
                        "CPC {c}.".format(c=cpc.name, p=iap_name))
        wrong_iap_names = [_iap.name for _iap in all_iaps
                           if _iap.name != lpar_name]

        if ap_type == 'image':
            ap_name = lpar_name
        if ap_type == 'wrongimage':
            ap_name = random.choice(wrong_iap_names)
        elif ap_type == 'load':
            try:
                ap_name = load_profiles[lpar_mode]
            except (KeyError, TypeError):
                pytest.skip("Inventory file entry for HMC nickname {h!r} does "
                            "not have an entry for operating mode {om!r} in "
                            "its 'load_profiles' property for CPC {c!r}".
                            format(h=hd.nickname, c=cpc.name, om=lpar_mode))
        else:
            assert ap_type is None
            ap_name = None

        if nap_type == 'image':
            nap_name = lpar_name
        elif nap_type == 'wrongimage':
            nap_name = random.choice(wrong_iap_names)
        else:
            assert nap_type == 'load'
            try:
                nap_name = load_profiles[lpar_mode]
            except (KeyError, TypeError):
                pytest.skip("Inventory file entry for HMC nickname {h!r} does "
                            "not have an entry for operating mode {om!r} in "
                            "its 'load_profiles' property for CPC {c!r}".
                            format(h=hd.nickname, c=cpc.name, om=lpar_mode))

        try:
            lpar = cpc.lpars.find(name=lpar_name)
        except zhmcclient.NotFound:
            pytest.skip("LPAR {p!r} does not exist on CPC {c}.".
                        format(c=cpc.name, p=lpar_name))

        if ap_type == 'load' or nap_type == 'load':
            lap_name = load_profiles[lpar_mode]
            try:
                cpc.load_activation_profiles.find(name=lap_name)
            except zhmcclient.NotFound:
                pytest.skip("Load activation profile {p!r} does not exist on "
                            "CPC {c}.".format(c=cpc.name, p=lap_name))

        op_mode = iap.get_property('operating-mode')
        assert op_mode == lpar_mode, (
            "Incorrect testcase definition: Operating mode {om!r} in image "
            "activation profile {p!r} on CPC {c} does not match the "
            "lpar_mode {lm!r} of the testcase".
            format(c=cpc.name, p=iap_name, om=op_mode, lm=lpar_mode))

        msg = ("Testing on CPC {c} with LPAR {p!r}".
               format(c=cpc.name, p=lpar.name))
        print(msg)
        logger.info(msg)

        if run == 'pdb':
            pdb.set_trace()

        logger.info("Preparation: Ensuring that LPAR %r has status %r",
                    lpar.name, initial_status)
        ensure_lpar_status(logger, lpar, iap, initial_status)

        logger.info("Preparation: Setting 'next-activation-profile-name' = %r "
                    "in LPAR %r", nap_name, lpar.name)
        saved_nap_name = set_resource_property(
            lpar, 'next-activation-profile-name', nap_name)

        logger.info("Preparation: Setting 'load-at-activation' = %r in image "
                    "profile %r", auto_load, iap.name)
        saved_auto_load = set_resource_property(
            iap, 'load-at-activation', auto_load)

        where = f"LPAR {lpar_name!r}"

        try:
            logger.info("Test: LPAR %r with initial status %r, module parms: "
                        "state: %r, activation_profile_name: %r, "
                        "additional parms: %r)",
                        lpar.name, initial_status, input_state, ap_name,
                        input_kwargs)

            # Prepare module input parameters (must be all required + optional)
            params = {
                'hmc_host': hmc_host,
                'hmc_auth': hmc_auth,
                'cpc_name': cpc.name,
                'name': lpar_name,
                'state': input_state,
                'select_properties': None,
                'activation_profile_name': ap_name,
                'load_address': input_kwargs.get('load_address', None),
                'load_parameter': input_kwargs.get('load_parameter', None),
                'clear_indicator': input_kwargs.get('clear_indicator', True),
                'store_status_indicator': input_kwargs.get(
                    'store_status_indicator', False),
                'timeout': input_kwargs.get('timeout', 60),
                'force': input_kwargs.get('force', False),
                'os_ipl_token': input_kwargs.get('os_ipl_token', None),
                'properties': input_kwargs.get('properties', None),
                'log_file': LOG_FILE,
                '_faked_session': faked_session,
            }

            mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

            with pytest.raises(SystemExit) as exc_info:

                # Exercise the code to be tested
                zhmc_lpar.main()

            exit_code = exc_info.value.args[0]

            status = pull_lpar_status(lpar)
            assert status == exp_status, (
                "LPAR {ln!r} has unexpected status {s!r} after module "
                "return (exit code: {e!r}). Expected status: {es!r}".
                format(ln=lpar_name, e=exit_code, s=status, es=exp_status))

            if exit_code != 0:
                msg = get_failure_msg(mod_obj)
                if msg.startswith('HTTPError: 403,1'):
                    pytest.skip("HMC user {u!r} is not permitted to access "
                                "test LPAR {ln!r}".
                                format(u=hd.userid, ln=lpar_name))
                assert exp_msg is not None, (
                    "Module should have succeeded on LPAR {ln!r} but failed "
                    "with exit code {e} and message:\n{m}".
                    format(ln=lpar_name, e=exit_code, m=msg))
                assert re.search(exp_msg, msg), (
                    "Module failed as expected on LPAR {ln!r}, but the error "
                    "message is unexpected:\n{m}".format(ln=lpar_name, m=msg))
            else:
                assert exp_msg is None, (
                    "Module should have failed on LPAR {ln!r} but succeeded. "
                    "Expected failure message pattern:\n{em!r} ".
                    format(ln=lpar_name, em=exp_msg))

                changed, result = get_module_output(mod_obj)
                if changed != exp_changed:
                    raise AssertionError(
                        "Unexpected change flag returned: actual: {0}, "
                        "expected: {1}\n".
                        format(changed, exp_changed))
                assert_lpar_props(result, exp_result, where)

        finally:
            logger.info("Cleanup: Ensuring that LPAR %r is inactive",
                        lpar.name)
            ensure_lpar_status(logger, lpar, iap, 'not-activated')

            logger.info("Cleanup: Setting 'next-activation-profile-name' = %r "
                        "in LPAR %r", saved_nap_name, lpar.name)
            set_resource_property(
                lpar, 'next-activation-profile-name', saved_nap_name)

            logger.info("Cleanup: Setting 'load-at-activation' = %r in image "
                        "profile %r", saved_auto_load, iap.name)
            set_resource_property(iap, 'load-at-activation', saved_auto_load)


LPAR_FACTS_TESTCASES = [
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - select_properties (list): Input for select_properties module parm
    # - exp_prop_names (list): Names of expected properties in module
    #   result (HMC-formatted) in case of module success. The module may
    #   return more then those listed.
    # - not_prop_names (list): Names of unexpected properties in module
    #   result (HMC-formatted) in case of module success. The module must
    #   not return those listed.
    # - exp_msg (string): Expected message pattern in case of module failure,
    #   or None for module success.
    # - exp_changed (bool): Boolean for expected 'changed' flag.
    # - run: Indicates whether the test should be run, or 'pdb' for debugger.

    (
        "Default input parms = full properties",
        None,
        [
            'name',
            'object-uri',
            'description',
            'status',
            'activation-mode',
        ],
        [],
        None,
        False,
        True,
    ),
    (
        "select empty list of properties",
        [],
        [
            'name',             # always returned
            'object-uri',       # always returned
        ],
        [
            'description',
            'status',
            'activation-mode',
        ],
        None,
        False,
        True,
    ),
    (
        "select one property",
        ['description'],
        [
            'name',
            'object-uri',
            'description',
        ],
        [
            'status',
            'activation-mode',
        ],
        None,
        False,
        True,
    ),
    (
        "select two properties",
        ['description', 'status'],
        [
            'name',
            'object-uri',
            'description',
            'status',
        ],
        [
            'activation-mode',
        ],
        None,
        False,
        True,
    ),
    (
        "select property with underscore",
        ['activation_mode'],
        [
            'name',
            'object-uri',
            'activation-mode',
        ],
        [
            'description',
            'status',
        ],
        None,
        False,
        True,
    ),
    (
        "select property with hyphen",
        ['activation-mode'],
        [
            'name',
            'object-uri',
            'activation-mode',
        ],
        [
            'description',
            'status',
        ],
        None,
        False,
        True,
    ),
]


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@pytest.mark.parametrize(
    "desc, select_properties, exp_prop_names, not_prop_names, "
    "exp_msg, exp_changed, run",
    LPAR_FACTS_TESTCASES)
@mock.patch("plugins.modules.zhmc_lpar.AnsibleModule", autospec=True)
def test_zhmc_lpar_facts(
        ansible_mod_cls,
        desc, select_properties, exp_prop_names, not_prop_names,
        exp_msg, exp_changed, run,
        check_mode, classic_mode_cpcs):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name, unused-argument
    """
    Test the zhmc_lpar module with state=facts.

    The test LPARs can be in any status.
    """
    if not classic_mode_cpcs:
        pytest.skip("HMC definition does not include any CPCs in classic mode")

    if not run:
        skip_warn("Testcase is disabled in testcase definition")

    logger = setup_logging(LOGGING, 'test_zhmc_lpar_facts', LOG_FILE)

    for cpc in classic_mode_cpcs:
        assert not cpc.dpm_enabled

        session = cpc.manager.session
        hd = session.hmc_definition
        hmc_host = hd.host
        hmc_auth = dict(userid=hd.userid, password=hd.password,
                        ca_certs=hd.ca_certs, verify=hd.verify)

        faked_session = session if hd.mock_file else None

        # Pick any LPAR on the CPC
        lpars = cpc.lpars.list()
        if not lpars:
            pytest.skip(f"No LPARs exist on CPC {cpc.name}.")
        lpar = random.choice(lpars)

        msg = ("Testing on CPC {c} with LPAR {p!r}".
               format(c=cpc.name, p=lpar.name))
        print(msg)
        logger.info(msg)

        if run == 'pdb':
            pdb.set_trace()

        # Prepare module input parameters (must be all required + optional)
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'cpc_name': cpc.name,
            'name': lpar.name,
            'state': 'facts',
            'select_properties': select_properties,
            'activation_profile_name': None,
            'load_address': None,
            'load_parameter': None,
            'clear_indicator': True,
            'store_status_indicator': False,
            'timeout': 60,
            'force': False,
            'os_ipl_token': None,
            'properties': None,
            'log_file': LOG_FILE,
            '_faked_session': faked_session,
        }

        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        with pytest.raises(SystemExit) as exc_info:

            # Exercise the code to be tested
            zhmc_lpar.main()

        exit_code = exc_info.value.args[0]

        if exit_code != 0:
            msg = get_failure_msg(mod_obj)
            if msg.startswith('HTTPError: 403,1'):
                pytest.skip("HMC user {u!r} is not permitted to access "
                            "test LPAR {ln!r}".
                            format(u=hd.userid, ln=lpar.name))
            assert exp_msg is not None, (
                "Module should have succeeded on LPAR {ln!r} but failed "
                "with exit code {e} and message:\n{m}".
                format(ln=lpar.name, e=exit_code, m=msg))
            assert re.search(exp_msg, msg), (
                "Module failed as expected on LPAR {ln!r}, but the error "
                "message is unexpected:\n{m}".format(ln=lpar.name, m=msg))
        else:
            assert exp_msg is None, (
                "Module should have failed on LPAR {ln!r} but succeeded. "
                "Expected failure message pattern:\n{em!r} ".
                format(ln=lpar.name, em=exp_msg))

            changed, lpar_properties = get_module_output(mod_obj)
            if changed != exp_changed:
                raise AssertionError(
                    "Unexpected change flag returned: actual: {0}, "
                    "expected: {1}\n".
                    format(changed, exp_changed))

            # Check the presence and absence of properties in the result
            lpar_prop_names = list(lpar_properties.keys())
            for pname in exp_prop_names:
                assert pname in lpar_prop_names
            for pname in not_prop_names:
                assert pname not in lpar_prop_names
