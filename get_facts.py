#!/usr/bin/env python
#
# Get facts for a partition via the Ansible API 2.0.

import sys
import os
from collections import namedtuple
from pprint import pprint
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible.errors import AnsibleError


Options = namedtuple('Options',
                     ['connection', 'module_path', 'forks', 'become',
                      'become_method', 'become_user', 'check', 'diff'])


class ResultCallback(CallbackBase):
    """
    Ansible callbacks that store the results in the object.
    """

    def __init__(self):
        self.status_ok = []
        self.status_failed = []
        self.status_unreachable = []

    def v2_runner_on_ok(self, result):
        """
        Called when a task completes successfully.
        """
        host_name = result._host.get_name()
        task_name = result._task.get_name()
        result = result._result
        status = dict(host_name=host_name, task_name=task_name, result=result)
        self.status_ok.append(status)

        print("Host '%s', Task '%s': Ok" % (host_name, task_name))
        if task_name == 'debug':
            # TODO: The output of the debug module does not get printed by the
            # module itself, so we print it here. Find out why the debug module
            # does not print.
            print("Debug result:")
            pprint(result)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        """
        Called when a task fails.
        """
        host_name = result._host.get_name()
        task_name = result._task.get_name()
        status = dict(host_name=host_name, task_name=task_name,
                      result=result._result)
        self.status_failed.append(status)

        print("Host '%s', Task '%s': Failed" % (host_name, task_name))

    def v2_runner_on_unreachable(self, result, ignore_errors=False):
        """
        Called when a task fails because the host is unreachable.
        """
        host_name = result._host.get_name()
        task_name = result._task.get_name()
        status = dict(host_name=host_name, task_name=task_name,
                      result=result._result)
        self.status_unreachable.append(status)

        print("Host '%s', Task '%s': Host unreachable" %
              (host_name, task_name))


def rc_msg(rc):
    """
    Return error message for a TaskQueueManager.run() return code.
    """

    messages = {
        TaskQueueManager.RUN_ERROR: "Play failed",
        TaskQueueManager.RUN_FAILED_HOSTS: "Play failed on some hosts",
        TaskQueueManager.RUN_UNREACHABLE_HOSTS: "Unreachable hosts",
        TaskQueueManager.RUN_FAILED_BREAK_PLAY: "Play failed (breaking)",
    }

    if rc == TaskQueueManager.RUN_UNKNOWN_ERROR:
        return "Unknown error"

    msg_strings = []
    for mask in messages:
        if rc & mask:
            msg_strings.append(messages[mask])
    return ', '.join(msg_strings)


def main():

    my_dir = os.path.dirname(sys.argv[0])
    zhmc_module_dir = os.path.join(my_dir, 'zhmc_ansible_modules')
    zhmc_playbooks_dir = os.path.join(my_dir, 'playbooks')
    inventory_file = '/etc/ansible/hosts'

    options = Options(connection='local', module_path=[zhmc_module_dir],
                      forks=100, become=None, become_method=None,
                      become_user=None, check=False, diff=False)
    passwords = dict(vault_pass=None)
    results_callback = ResultCallback()
    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources=[inventory_file])
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    # The playbook source
    play_source = dict(
        name="Get facts for a Z partition",
        hosts='localhost',
        gather_facts='no',
        vars_files=[
            os.path.join(zhmc_playbooks_dir, 'vars.yml'),
            os.path.join(zhmc_playbooks_dir, 'vault.yml'),
        ],
        tasks=[
            dict(
                name="Get partition facts",
                action=dict(
                    module='zhmc_partition',
                    args=dict(
                        hmc_host="{{hmc_host}}",
                        hmc_auth="{{hmc_auth}}",
                        cpc_name="{{cpc_name}}",
                        name="{{partition_name}}",
                        state='facts',
                    ),
                ),
                register='part1_result',
            ),
            dict(
                action=dict(
                    module='debug',
                    args=dict(
                        msg="Gathered facts for partition "
                            "'{{part1_result.partition.name}}': "
                            "status='{{part1_result.partition.status}}'",
                    ),
                ),
            ),
        ],
    )

    play = Play().load(
        play_source,
        variable_manager=variable_manager,
        loader=loader)

    tqm = None
    try:

        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            options=options,
            passwords=passwords,
            stdout_callback=results_callback,
        )

        try:
            rc = tqm.run(play)
        except AnsibleError as exc:
            print("Error: AnsibleError: %s" % exc)
            return 2

        if rc == TaskQueueManager.RUN_OK:
            return 0
        elif rc & TaskQueueManager.RUN_FAILED_HOSTS:
            status_list = results_callback.status_failed
            assert len(status_list) == 1
            status = status_list[0]
            host_name = status['host_name']
            task_name = status['task_name']
            result = status['result']
            try:
                msg = result['msg']
            except Exception:
                print("Internal error: Unexpected format of result: %r" %
                      result)
                return 2
            print("Error: Task '%s' failed on host '%s': %s" %
                  (task_name, host_name, msg))
            return 1
        elif rc & TaskQueueManager.RUN_UNREACHABLE_HOSTS:
            status_list = results_callback.status_unreachable
            assert len(status_list) == 1
            status = status_list[0]
            host_name = status['host_name']
            task_name = status['task_name']
            result = status['result']
            try:
                msg = result['msg']
            except Exception:
                print("Internal error: Unexpected format of result: %r" %
                      result)
                return 2
            print("Error: Task '%s' failed because host '%s' is unreachable: "
                  "%s" % (task_name, host_name, msg))
            return 1
        else:
            print("Internal error: Unexpected rc=%s: %s" % (rc, rc_msg(rc)))
            return 2

    finally:
        if tqm is not None:
            tqm.cleanup()

    return 0


if __name__ == '__main__':
    sys.exit(main())
