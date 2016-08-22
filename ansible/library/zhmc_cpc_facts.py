#!/usr/bin/python

import requests.packages.urllib3
import zhmcclient
requests.packages.urllib3.disable_warnings()


EXAMPLES = '''
# Gather facts about all CPCs:
- zhmc_cpc_facts:
    auth_hmc: 192.168.111.7
    auth_userid: admin
    auth_password: 1234
    detailed: true

- debug:
    var: cpcs
'''


def zhmc_cpc_facts(data):

    auth_hmc = data['auth_hmc']
    auth_userid = data['auth_userid']
    auth_password = data['auth_password']
    cpc_name = data['cpc_name']
    detailed = data['detailed']
    changed = False

    try:
        session = zhmcclient.Session(auth_hmc, auth_userid, auth_password)
        client = zhmcclient.Client(session)
        if detailed is None:
            detailed = False
        if cpc_name:
            cpc = client.cpcs.find(name=cpc_name, full_properties=detailed)
            result = cpc.properties
        else:
            cpcs= client.cpcs.list(detailed)
            cpc_list = list()
            for cpc in cpcs:
                cpc_list.append(cpc.properties)
            result = cpc_list

        session.logoff()
        return False, changed, result

    except zhmcclient.Error as exc:
        session.logoff()
        return True, False, str(exc)


def main():

    fields = {
        "auth_hmc": {"required": True, "type": "str"},
        "auth_userid": {"required": True, "type": "str"},
        "auth_password": {"required": True, "type": "str"},
        "cpc_name": {"required": False, "type": "str"},
        "detailed": {"required": False, "type": "bool"}
    }

    module = AnsibleModule(argument_spec=fields)
    is_error, has_changed, result = zhmc_cpc_facts(module.params)

    if not is_error:
         module.exit_json(changed=has_changed, ansible_facts=dict(cpcs=result))
    else:
         module.fail_json(msg="Error retrieving CPC facts: " + result)

# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()

