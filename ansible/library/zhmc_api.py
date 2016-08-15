#!/usr/bin/python

from ansible.module_utils.basic import *
import requests.packages.urllib3

import zhmcclient

requests.packages.urllib3.disable_warnings()

def zhmc_api_version(data):

    hmc = data['auth_hmc']
    session = zhmcclient.Session(hmc)
    cl = zhmcclient.Client(session)

    result = cl.query_api_version()

    # default: something went wrong
    meta = {'response': result}
    return False, False, meta


def main():

    fields = {
        "auth_hmc": {"required": True, "type": "str"}
    }

    module = AnsibleModule(argument_spec=fields)
    is_error, has_changed, result = zhmc_api_version(module.params)
    if not is_error:
         module.exit_json(changed=has_changed, meta=result)
    else:
         module.fail_json(msg="Error getting zHMC API version", meta=result)

if __name__ == '__main__':  
    main()

