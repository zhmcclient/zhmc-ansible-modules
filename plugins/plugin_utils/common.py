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
Common support for all non-module plugins of this collection.
"""

from ansible.plugins.action import ActionBase


class NoLogActionBase(ActionBase):
    """
    Base class for action plugin classes that treats the return value of the
    called Ansible module as a no_log value.

    This class replaces the default Ansible action plugin
    (ansible.legacy.normal).

    Use this class as follows to protect the return value of module "zhmc_xxx":

    In plugins/action/zhmc_xxx.py:

        from ..plugin_utils.common import NoLogActionBase

        class ActionModule(NoLogActionBase):
            pass
    """

    # This action plugin does not need Ansible's temp-directory/file-transfer
    # machinery set up on the target host (localhost).
    TRANSFERS_FILES = False

    def run(self, tmp=None, task_vars=None):
        """
        This method is called before the Ansible module is called.
        It calls the Ansible module and treats its return value as a no_log
        value.
        """

        result = super(NoLogActionBase, self).run(tmp, task_vars)

        module_return = self._execute_module(
            module_name=self._task.action,
            module_args=self._task.args,
            task_vars=task_vars)

        result.update(module_return)

        # This special variable causes Ansible to treat the returned value
        # as a no_log value.
        result['_ansible_no_log'] = True

        return result
