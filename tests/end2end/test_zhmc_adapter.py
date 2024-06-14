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
End2end tests for zhmc_adapter module.
"""


import uuid
import copy
import pytest
from unittest import mock
import re
import random
from pprint import pformat
import requests.packages.urllib3
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
from zhmcclient.testutils import dpm_mode_cpcs  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_adapter
from .utils import mock_ansible_module, get_failure_msg

requests.packages.urllib3.disable_warnings()

DEBUG = False  # Print debug messages
DEBUG_LOG = False  # Write log file

LOG_FILE = 'zhmc_adapter.log' if DEBUG_LOG else None

# Adapter properties that are present only for certain adapter families.
# Key: property name with hyphens
# Value: Tuple of adapter families that have the property
ADAPTER_FAMILY_COND_PROPS = {
    'card-location':
        ('ficon', 'osa', 'roce', 'crypto', 'accelerator', 'cna', 'nvme'),
    'port-count': ('ficon', 'osa', 'roce', 'hipersockets', 'cna'),
    'network-port-uris': ('osa', 'roce', 'hipersockets', 'cna'),
    'storage-port-uris': ('ficon'),
    'maximum-transmission-unit-size': ('hipersockets'),
    'configured-capacity':
        ('ficon', 'osa', 'roce', 'hipersockets', 'accelerator', 'cna'),
    'used-capacity':
        ('ficon', 'osa', 'roce', 'hipersockets', 'accelerator', 'cna'),
    'allowed-capacity':
        ('ficon', 'osa', 'roce', 'hipersockets', 'accelerator', 'cna'),
    'maximum-total-capacity':
        ('ficon', 'osa', 'roce', 'hipersockets', 'accelerator', 'cna'),
    'channel-path-id': ('ficon', 'osa', 'hipersockets'),
    'crypto-number': ('crypto'),
    'crypto-type': ('crypto'),
    'udx-loaded': ('crypto'),
    'tke-commands-enabled': ('crypto'),
    'ssd-is-installed': ('nvme'),
    'ssd-capacity': ('nvme'),
    'ssd-model-number': ('nvme'),
    'ssd-serial-number': ('nvme'),
    'ssd-subsystem-vendor-id': ('nvme'),
    'ssd-vendor-id': ('nvme'),
    'network-ports': ('osa'),
}

# Adapter properties that have been added in certain HMC versions.
# Key: property name with hyphens
# Value: HMC version that added the property, as list of major(int), minor(int)
ADAPTER_HMC_COND_PROPS = {
    'ssd-is-installed': [2, 15],
    'ssd-capacity': [2, 15],
    'ssd-model-number': [2, 15],
    'ssd-serial-number': [2, 15],
    'ssd-subsystem-vendor-id': [2, 15],
    'ssd-vendor-id': [2, 15],
    'network-ports': [2, 16],
}

# Adapter properties that are present in other conditions not checked.
ADAPTER_OTHER_COND_PROPS = (
    'network-ports',  # Only on CPCs in classic mode
)

# Artificial adapter properties (added by the module).
ADAPTER_ARTIFICIAL_PROPS = (
    'ports',
)


def setup_adapter(hd, cpc, name, properties):
    """
    Create a new Hipersocket adapter on the specified CPC, for test purposes.

    Parameters:
      hd(zhmcclient.testutils.HMCDefinition): HMC definition context.
      cpc(zhmcclient.Cpc): CPC on which the adapter will be created.
      name(string): Adapter name. Must not exist yet.
      properties(dict): Input properties for Adapter.create_hipersocket(),
        with property names using HMC notation (with dashes).
    """
    props = copy.deepcopy(properties)
    props['name'] = name

    adapter_id = None
    try:

        try:
            adapter = cpc.adapters.create_hipersocket(props)
            adapter_id = adapter.prop('adapter-id')
        except zhmcclient.HTTPError as exc:
            if exc.http_status == 403 and exc.reason == 1:
                # User is not permitted to create adapters
                pytest.skip("HMC user {u!r} is not permitted to create "
                            "test adapter on CPC {c!r}".
                            format(u=hd.userid, c=cpc.name))
            else:
                raise

        if DEBUG:
            print("Debug: setup_adapter: Created test adapter {n!r} with "
                  "adapter-id {i!r}".
                  format(n=adapter.name, i=adapter_id))

    except zhmcclient.Error as exc:
        if adapter_id:
            teardown_adapter(cpc, adapter_id)
        pytest.skip("Error in HMC operation during test adapter setup: {e}".
                    format(e=exc))

    return adapter


def teardown_adapter(cpc, adapter_id):
    """
    Delete a Hipersocket adapter created for test purposes by setup_adapter().

    The adapter is looked up by adapter-id. If the adapter was already deleted
    by the test code, that is tolerated.

    Parameters:
      cpc(zhmcclient.Cpc): The CPC of the adapter.
      adapter_id(string): The adapter-id property of the adapter.
    """

    try:
        # We invalidate the name cache of our client, because the adapter
        # was possibly deleted by the Ansible module and not through our
        # client instance.
        cpc.adapters.invalidate_cache()
        adapter = cpc.adapters.find(**{'adapter-id': adapter_id})
    except zhmcclient.NotFound:
        return

    try:
        adapter.delete()
    except zhmcclient.Error as exc:
        print("Warning: Deleting test adapter with adapter-id {a!r} on CPC "
              "{c!r} failed with: {e} - please clean it up manually!".
              format(a=adapter_id, c=cpc.name, e=exc))
    else:
        if DEBUG:
            print("Debug: teardown_adapter: Deleted test adapter {n!r} with "
                  "adapter-id {i!r}".
                  format(n=adapter.name, i=adapter_id))


def unique_adapter_name():
    """
    Return a unique adapter name.
    """
    adapter_name = 'zhmc_test_{u}'.format(
        u=str(uuid.uuid4()).replace('-', ''))
    return adapter_name


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, adapter_properties) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, adapter):
        return changed, adapter

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_adapter_props(act_props, exp_props, hmc_version_info, where):
    """
    Assert the actual properties of a adapter.

    Parameters:
      act_props(dict): Actual adapter props to verify (with dashes).
      exp_props(dict): Expected adapter properties (with dashes).
      hmc_version_info(list(int,int)): Major and minor HMC version.
      where(string): Indicator about the testcase for assertion messages.
    """

    assert isinstance(act_props, dict), where  # Dict of User role props
    adapter_family = act_props.get('adapter-family', None)

    # Assert presence of properties in the output
    for prop_name in zhmc_adapter.ZHMC_ADAPTER_PROPERTIES:
        prop_name_hmc = prop_name.replace('_', '-')
        if prop_name_hmc in ADAPTER_OTHER_COND_PROPS:
            continue
        if prop_name_hmc in ADAPTER_HMC_COND_PROPS:
            if hmc_version_info < ADAPTER_HMC_COND_PROPS[prop_name_hmc]:
                continue
        if prop_name_hmc in ADAPTER_FAMILY_COND_PROPS:
            if not adapter_family:
                # In check mode, we don't get the 'adapter-family' property,
                # so we have to skip this property.
                continue
            if adapter_family not in ADAPTER_FAMILY_COND_PROPS[prop_name_hmc]:
                continue
        where_prop = where + \
            ", property {p!r} missing in adapter properties {pp!r}". \
            format(p=prop_name_hmc, pp=act_props)
        assert prop_name_hmc in act_props, where_prop

    # Assert the expected property values for non-artificial properties
    for prop_name in exp_props:
        prop_name_hmc = prop_name.replace('_', '-')
        if prop_name_hmc in ADAPTER_ARTIFICIAL_PROPS:
            continue
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

    # Assert type of the artificial properties in the output
    assert 'ports' in act_props, where
    port_props_list = act_props['ports']
    if port_props_list is not None:
        assert isinstance(port_props_list, list), where  # List of ports
        for port_props in port_props_list:
            assert isinstance(port_props, dict), where  # Dict of port props


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@pytest.mark.parametrize(
    "adapter_family", [
        pytest.param('hipersockets', id="adapter_family=hipersockets"),
        pytest.param('osa', id="adapter_family=osa"),
        pytest.param('ficon', id="adapter_family=ficon"),
        pytest.param('roce', id="adapter_family=roce"),
        pytest.param('crypto', id="adapter_family=crypto"),
        pytest.param('accelerator', id="adapter_family=accelerator"),
        pytest.param('nvme', id="adapter_family=nvme"),
        pytest.param('cna', id="adapter_family=cna"),
        pytest.param('coupling', id="adapter_family=coupling"),
        pytest.param('ism', id="adapter_family=ism"),
        pytest.param('zhyperlink', id="adapter_family=zhyperlink"),
    ]
)
@mock.patch("plugins.modules.zhmc_adapter.AnsibleModule", autospec=True)
def test_zhmc_adapter_facts(
        ansible_mod_cls, adapter_family, check_mode,
        dpm_mode_cpcs):  # noqa: F811, E501
    """
    Test the zhmc_adapter module with state=facts on DPM mode CPCs.
    """
    if not dpm_mode_cpcs:
        pytest.skip("HMC definition does not include any CPCs in DPM mode")

    for cpc in dpm_mode_cpcs:
        assert cpc.dpm_enabled

        session = cpc.manager.session
        hd = session.hmc_definition
        hmc_host = hd.host
        hmc_auth = dict(userid=hd.userid, password=hd.password,
                        ca_certs=hd.ca_certs, verify=hd.verify)

        faked_session = session if hd.mock_file else None

        hmc_version = cpc.manager.console.prop('version')
        hmc_version_info = [int(x) for x in hmc_version.split('.')]

        # Determine a random existing adapter of the desired type to test.
        all_adapters = cpc.adapters.list(
            additional_properties=['adapter-family'])
        adapters = [a for a in all_adapters
                    if a.get_property('adapter-family') == adapter_family]
        if len(adapters) == 0:
            pytest.skip("CPC '{c}' has no adapters of family '{t}'".
                        format(c=cpc.name, t=adapter_family))
        adapter = random.choice(adapters)

        # The adapter object provides the expected property values, so
        # we pull full properties to make sure all are tested.
        adapter.pull_full_properties()

        where = f"adapter '{adapter.name}'"

        # Prepare module input parameters (must be all required + optional)
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'cpc_name': cpc.name,
            'name': adapter.name,
            'match': None,
            'state': 'facts',
            'properties': None,
            'log_file': LOG_FILE,
            '_faked_session': faked_session,
        }

        # Prepare mocks for AnsibleModule object
        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_adapter.main()
        exit_code = exc_info.value.args[0]

        # Assert module exit code
        assert exit_code == 0, \
            "{w}: Module failed with exit code {e} and message:\n{m}". \
            format(w=where, e=exit_code, m=get_failure_msg(mod_obj))

        # Assert module output
        changed, output_props = get_module_output(mod_obj)
        assert changed is False, \
            "{w}: Module returned changed={c}". \
            format(w=where, c=changed)
        assert_adapter_props(
            output_props, adapter.properties, hmc_version_info, where)


# Input properties for zhmcclient create_hipersocket() for a standard
# Hipersocket adapter, using property names with hyphens.
STD_HIPERSOCKET_CREATE_PROPS_HMC = {
    # 'name': provided in test code
    'description': "zhmc test hipersocket adapter",
    'port-description': "zhmc test hipersocket port",
    'maximum-transmission-unit-size': 16,
}

# Input properties for the zhmc_adapter module for a standard
# Hipersocket adapter, using property names with underscores.
STD_HIPERSOCKET_CREATE_PROPS = {
    # 'name': provided in separate input parameter
    'type': 'hipersockets',
    'description': STD_HIPERSOCKET_CREATE_PROPS_HMC['description'],
    'maximum_transmission_unit_size':
        STD_HIPERSOCKET_CREATE_PROPS_HMC['maximum-transmission-unit-size'],
}

# Expected properties for the output of the zhmc_adapter module for a standard
# Hipersocket adapter, using property names with hyphens.
STD_HIPERSOCKET_EXP_PROPS_HMC = {
    # 'name': compared separately
    'type': 'hipersockets',
    'description': STD_HIPERSOCKET_CREATE_PROPS_HMC['description'],
    'maximum-transmission-unit-size':
        STD_HIPERSOCKET_CREATE_PROPS_HMC['maximum-transmission-unit-size'],
    'detected-card-type': 'hipersockets',
    'adapter-family': 'hipersockets',
    'port-count': 1,
}

# Update 1 for the tests
HIPERSOCKET_UPDATE1_INPUT_PROPS = {
    'description': "zhmc new descripion",
}
HIPERSOCKET_UPDATE1_EXP_PROPS_HMC = dict(STD_HIPERSOCKET_EXP_PROPS_HMC)
for pname, pvalue in HIPERSOCKET_UPDATE1_INPUT_PROPS.items():
    pname_hmc = pname.replace('_', '-')
    HIPERSOCKET_UPDATE1_EXP_PROPS_HMC[pname_hmc] = pvalue

ADAPTER_STATES_TESTCASES = [
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - initial_props (dict): HMC-formatted properties for initial adapter,
    #   or None for no initial adapter.
    # - input_state (string): 'state' input parameter for zhmc_adapter module.
    #   Must be one of: present, absent, set.
    # - input_name (string): 'name' input parameter for zhmc_adapter
    #   module. '{name}' syntax can be used to refer to a generated unique name.
    #   to refer to property values.
    # - input_match (dict): 'match' input parameter for zhmc_adapter
    #   module, or None if not to be provided. '{prop-name}' syntax can be used
    #   to refer to property values.
    # - input_props (dict): 'properties' input parameter for zhmc_adapter
    #   module.
    # - exp_props (dict): Expected properties of the 'adapter' output of the
    #   zhmc_adapter module when expecting success, or None when expecting
    #   failure.
    # - exp_changed (bool): Expected 'changed' flag of the zhmc_adapter module
    #   when expecting success, or None when expecting failure.
    # - exp_msg_pattern (string): Pattern for expected failure message, or
    #   None when expecting success.

    (
        "state=present with non-existing adapter",
        None,
        'present',
        '{name}',
        None,
        STD_HIPERSOCKET_CREATE_PROPS,
        STD_HIPERSOCKET_EXP_PROPS_HMC,
        True,
        None,
    ),
    (
        "state=present with existing adapter, no properties changed",
        STD_HIPERSOCKET_CREATE_PROPS_HMC,
        'present',
        '{name}',
        None,
        None,
        STD_HIPERSOCKET_EXP_PROPS_HMC,
        False,
        None,
    ),
    (
        "state=present with existing adapter and property update",
        STD_HIPERSOCKET_CREATE_PROPS_HMC,
        'present',
        '{name}',
        None,
        HIPERSOCKET_UPDATE1_INPUT_PROPS,
        HIPERSOCKET_UPDATE1_EXP_PROPS_HMC,
        True,
        None,
    ),
    (
        "state=set without match with existing adapter",
        STD_HIPERSOCKET_CREATE_PROPS_HMC,
        'set',
        '{name}',
        None,
        HIPERSOCKET_UPDATE1_INPUT_PROPS,
        HIPERSOCKET_UPDATE1_EXP_PROPS_HMC,
        True,
        None,
    ),
    (
        "state=set without match with non-existing adapter",
        None,
        'set',
        '{name}',
        None,
        HIPERSOCKET_UPDATE1_INPUT_PROPS,
        None,
        None,
        "NotFound: Could not find Adapter .*",
    ),
    (
        "state=set with match by adapter-id of existing adapter without rename",
        STD_HIPERSOCKET_CREATE_PROPS_HMC,
        'set',
        '{name}',
        {'adapter_id': '{adapter-id}'},
        HIPERSOCKET_UPDATE1_INPUT_PROPS,
        HIPERSOCKET_UPDATE1_EXP_PROPS_HMC,
        True,
        None,
    ),
    (
        "state=set with match by adapter-id of existing adapter with rename",
        STD_HIPERSOCKET_CREATE_PROPS_HMC,
        'set',
        '{name}_new',
        {'adapter_id': '{adapter-id}'},
        HIPERSOCKET_UPDATE1_INPUT_PROPS,
        HIPERSOCKET_UPDATE1_EXP_PROPS_HMC,
        True,
        None,
    ),
    (
        "state=set with match by adapter-id of existing adapter with rename "
        "to another existing adapter",
        STD_HIPERSOCKET_CREATE_PROPS_HMC,
        'set',
        '{existing}',
        {'adapter_id': '{adapter-id}'},
        HIPERSOCKET_UPDATE1_INPUT_PROPS,
        None,
        None,
        "HTTPError: 400,8: An adapter with the name specified .*",
    ),
    (
        "state=set with match by adapter-id of non-existing adapter",
        STD_HIPERSOCKET_CREATE_PROPS_HMC,
        'set',
        '{name}',
        {'adapter_id': 'foo'},
        HIPERSOCKET_UPDATE1_INPUT_PROPS,
        None,
        None,
        "NotFound: Could not find Adapter .*",
    ),
    (
        "state=set with match by object-id of existing adapter without rename",
        STD_HIPERSOCKET_CREATE_PROPS_HMC,
        'set',
        '{name}',
        {'object_id': '{object-id}'},
        HIPERSOCKET_UPDATE1_INPUT_PROPS,
        HIPERSOCKET_UPDATE1_EXP_PROPS_HMC,
        True,
        None,
    ),
    (
        "state=set with match by object-id of existing adapter with rename",
        STD_HIPERSOCKET_CREATE_PROPS_HMC,
        'set',
        '{name}_new',
        {'object_id': '{object-id}'},
        HIPERSOCKET_UPDATE1_INPUT_PROPS,
        HIPERSOCKET_UPDATE1_EXP_PROPS_HMC,
        True,
        None,
    ),
    (
        "state=absent with existing adapter",
        STD_HIPERSOCKET_CREATE_PROPS_HMC,
        'absent',
        '{name}',
        None,
        None,
        None,
        True,
        None,
    ),
    (
        "state=absent with non-existing adapter",
        None,
        'absent',
        '{name}',
        None,
        None,
        None,
        False,
        None,
    ),
]


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@pytest.mark.parametrize(
    "desc, initial_props, input_state, input_name, input_match, input_props, "
    "exp_props, exp_changed, exp_msg_pattern",
    ADAPTER_STATES_TESTCASES)
@mock.patch("plugins.modules.zhmc_adapter.AnsibleModule", autospec=True)
def test_zhmc_adapter_states(
        ansible_mod_cls,
        desc, initial_props, input_state, input_name, input_match, input_props,
        exp_props, exp_changed, exp_msg_pattern,
        check_mode, dpm_mode_cpcs):  # noqa: F811, E501
    """
    Test the zhmc_adapter module with state=absent/present on DPM mode CPCs,
    with Hipersocket adapters.
    """
    if not dpm_mode_cpcs:
        pytest.skip("HMC definition does not include any CPCs in DPM mode")

    for cpc in dpm_mode_cpcs:
        assert cpc.dpm_enabled

        session = cpc.manager.session
        hd = session.hmc_definition
        hmc_host = hd.host
        hmc_auth = dict(userid=hd.userid, password=hd.password,
                        ca_certs=hd.ca_certs, verify=hd.verify)

        faked_session = session if hd.mock_file else None

        hmc_version = cpc.manager.console.prop('version')
        hmc_version_info = [int(x) for x in hmc_version.split('.')]

        all_adapters = cpc.adapters.list()
        existing_adapter = random.choice(all_adapters)

        # Create an adapter name that does not exist
        unique_name = unique_adapter_name()
        input_name = input_name.replace('{name}', unique_name)
        input_name = input_name.replace('{existing}', existing_adapter.name)

        initial_adapter = None
        initial_adapter_id = None
        input_match2 = None
        module_adapter_id = None
        try:
            # Create initial adapter, if specified so
            if initial_props:
                initial_adapter = setup_adapter(
                    hd, cpc, unique_name, initial_props)
                # The adapter object provides the expected property values, so
                # we pull full properties to make sure all are tested.
                initial_adapter.pull_full_properties()
                initial_adapter_id = initial_adapter.prop('adapter-id')

                # Process the {prop-name} values in the 'match' parameter
                if input_match is not None:
                    input_match2 = {}
                    for pname, pvalue in input_match.items():
                        m = re.search(r'\{(.*?)\}', pvalue)
                        if m:
                            pn = m.group(1)
                            pv = initial_adapter.prop(pn)
                            if pv is None:
                                # In mock environments, some properties (e.g.
                                # 'adapter-id' and 'object-id') are None.
                                # Skip the test in that case.
                                # TODO: Remove the skip once implemented.
                                pytest.skip("Property {pn} is None".
                                            format(pn=pn))
                            pvalue = pvalue.replace('{' + pn + '}', pv)
                        input_match2[pname] = pvalue

            where = f"adapter '{unique_name}'"

            if DEBUG:
                print("Debug: Input parms: match={m}, name={n}".
                      format(m=input_match2, n=input_name))

            # Prepare module input parameters (must be all required + optional)
            params = {
                'hmc_host': hmc_host,
                'hmc_auth': hmc_auth,
                'cpc_name': cpc.name,
                'name': input_name,
                'match': input_match2,
                'state': input_state,
                'properties': input_props,
                'log_file': LOG_FILE,
                '_faked_session': faked_session,
            }

            # Prepare mocks for AnsibleModule object
            mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

            # Exercise the code to be tested
            with pytest.raises(SystemExit) as exc_info:
                zhmc_adapter.main()
            exit_code = exc_info.value.args[0]

            if exit_code != 0:
                msg = get_failure_msg(mod_obj)
                if msg.startswith('HTTPError: 403,1'):
                    pytest.skip("HMC user '{u}' is not permitted to create "
                                "test adapter".
                                format(u=hd.userid))
                assert exp_msg_pattern is not None, \
                    "{w}: Module should have succeeded but failed with exit " \
                    "code {e} and message:\n{m}". \
                    format(w=where, e=exit_code, m=msg)
                assert re.search(exp_msg_pattern, msg), \
                    "{w}: Module failed as expected, but the error message " \
                    "is unexpected:\n{m}".format(w=where, m=msg)
            else:
                assert exp_msg_pattern is None, \
                    "{w}: Module should have failed but succeeded. Expected " \
                    "failure message pattern:\n{em!r} ". \
                    format(w=where, em=exp_msg_pattern)

                changed, output_props = get_module_output(mod_obj)
                if changed != exp_changed:
                    initial_props_sorted = \
                        dict(sorted(
                            initial_props.items(), key=lambda x: x[0])) \
                        if initial_props is not None else None
                    input_props_sorted = \
                        dict(sorted(input_props.items(), key=lambda x: x[0])) \
                        if input_props is not None else None
                    output_props_sorted = \
                        dict(sorted(output_props.items(), key=lambda x: x[0])) \
                        if output_props is not None else None
                    raise AssertionError(
                        "Unexpected change flag returned: actual: {0}, "
                        "expected: {1}\n"
                        "Initial partition properties:\n{2}\n"
                        "Module input properties:\n{3}\n"
                        "Resulting partition properties:\n{4}".
                        format(changed, exp_changed,
                               pformat(initial_props_sorted, indent=2),
                               pformat(input_props_sorted, indent=2),
                               pformat(output_props_sorted, indent=2)))

                # In case the module itself has created the adapter, we need
                # to clean it up later, and get its adapter ID for that.
                module_adapter_id = output_props.get('adapter-id', None)

                # Add 'name' to the expected properties. It will always be
                # the specified 'name' property (both in rename and non-rename
                # cases).
                if exp_props:
                    exp_props2 = dict(exp_props)
                    exp_props2['name'] = input_name
                else:
                    exp_props2 = None

                if input_state in ('present', 'set'):
                    assert_adapter_props(
                        output_props, exp_props2, hmc_version_info, where)
                else:
                    assert output_props == {}

        finally:
            if initial_adapter_id:
                teardown_adapter(cpc, initial_adapter_id)
            if module_adapter_id:
                teardown_adapter(cpc, module_adapter_id)
