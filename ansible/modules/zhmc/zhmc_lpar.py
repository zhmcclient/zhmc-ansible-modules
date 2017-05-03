#!/usr/bin/python

from ansible.module_utils.basic import *
import requests.packages.urllib3

import zhmcclient

requests.packages.urllib3.disable_warnings()

def zhmc_activate(data):

    auth_hmc = data['auth_hmc']
    auth_userid = data['auth_userid']
    auth_password = data['auth_password']
    cpc_name = data['cpc_name']
    lpar_name = data['lpar_name']
    load_address = data['load']
    changed = False

    try:
        session = zhmcclient.Session(auth_hmc, auth_userid, auth_password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        lpar = cpc.lpars.find(name=lpar_name)

        if lpar.properties['status'] in ["not-activated"]:
            result = lpar.activate()
            lpar = cpc.lpars.find(name=lpar_name)
            changed = True
        if lpar.properties['status'] not in ["operating"] and load_address:
            result = lpar.load(load_address)
            changed = True
        session.logoff()
        return False, changed, result

    except zhmcclient.Error as exc:
        session.logoff()
        return True, False, str(exc)

def zhmc_deactivate(data):

    auth_hmc = data['auth_hmc']
    auth_userid = data['auth_userid']
    auth_password = data['auth_password']
    cpc_name = data['cpc_name']
    lpar_name = data['lpar_name']
    changed = False
    result = "Nothing"

    try:
        session = zhmcclient.Session(auth_hmc, auth_userid, auth_password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        lpar = cpc.lpars.find(name=lpar_name)

        if lpar.properties['status'] in ["operating", "not-operating", "exceptions" ]:
            result = lpar.deactivate()
            changed = True
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
        "cpc_name": {"required": True, "type": "str"},
        "lpar_name": {"required": True, "type": "str"},
        "load": {"required": False, "type": "str"},
        "state": {
            "required": True,
            "choices": ['activated', 'deactivated'],
             "type": 'str'
         }
    }

    choice_map = {
        "activated": zhmc_activate,
        "deactivated": zhmc_deactivate,
    }

    module = AnsibleModule(argument_spec=fields)
    is_error, has_changed, result = choice_map.get(module.params['state'])(module.params)

    if not is_error:
         module.exit_json(changed=has_changed, meta=result)
    else:
#         module.fail_json(msg="Error activating LPAR", meta=result)
         module.fail_json(msg="Error activating LPAR: " + result)

if __name__ == '__main__':
    main()

