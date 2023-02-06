#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
import copy
import traceback
from ansible_collections.ramblurr.truenas.plugins.module_utils.api import TruenasApi

DOCUMENTATION = r"""
---
module: truenas_cron
author: "Casey Link <unnamedrambler@gmail.com>"
short_description: Manage TrueNAS system crons
description:
  - Manage TrueNAS system crons
options:
  state:
    description:
      - Indicate desired state of the target.
    default: present
    choices: ['present', 'absent']
    type: str
  url:
    description:
      - The url of the TrueNAS instance
    type: str
    required: true
  user:
    description:
      - The user to auth as to the TrueNAS instance
    type: str
    default: root
  password:
    description:
      - The password to auth as to the TrueNAS instance
    type: str
    required: true
  description:
    description:
      - The description of the cron task
    type: str
    required: true
  command:
    description:
      - The command to run, required if state is 'present'
    type: str
  user:
    description:
      - The run as user of the cron task
    type: str
  hide_stdout:
    description:
      - Whether stdout is hidden or not
    type: bool
  hide_stderr:
    description:
      - Whether stderr is hidden or not
    type: bool
  schedule:
    description: ''
    suboptions:
      minute:
        type: str
      hour:
        type: str
      dom:
        type: str
      month:
        type: str
      dow:
        type: str
    type: dict

requirements:
  - "python >= 3.7"
"""
EXAMPLES = r"""
- name: run script on schedule
  truenas_cron:
    url: https://mytruenas.com
    password: example
    state: present
    description: run a script
    command: /root/some-script
    hide_stdout: true
    hide_stderr: true
    schedule:
      minute: "0"
      hour: "0"
      dom: "*"
      month: "*"
      dow: "*"
    user: root

- name: remove a script
  truenas_cron:
    url: https://example.com
    password: example
    state: present
    description: run a script
    state: absent
"""


def without(d, key):
    new_d = copy.deepcopy(d)
    new_d.pop(key)
    return new_d


API_ENDPOINT = "%(hostname)s/api/v2.0"


def match_cron(crons, description):
    for t in crons:
        if t["description"] == description:
            return t
    return None


def create_cron(client, params):
    payload = dict(
        description=params["description"],
        enabled=params["enabled"],
        stdout=params["hide_stdout"],
        stderr=params["hide_stderr"],
        command=params["command"],
        user=params["user"],
        schedule=params["schedule"],
    )
    return client.post("/cronjob", payload)


def update_cron(client, cron, params):
    payload = dict(
        description=params["description"],
        enabled=params["enabled"],
        stdout=params["hide_stdout"],
        stderr=params["hide_stderr"],
        command=params["command"],
        user=params["user"],
        schedule=params["schedule"],
    )
    cron_plain = without(cron, "id")
    if cron_plain == payload:
        return None
    else:
        tid = cron["id"]
        return client.put(f"/cronjob/id/{tid}", payload)


def delete_cron(client, cron):
    tid = cron["id"]
    return client.delete(f"/cronjob/id/{tid}")


def run_module():
    module_args = dict(
        url=dict(type="str", required=True),
        user=dict(type="str", default="root"),
        password=dict(type="str", required=True, no_log=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        enabled=dict(type="bool", default=True),
        hide_stdout=dict(type="bool", default=True),
        hide_stderr=dict(type="bool", default=False),
        description=dict(type="str", required=True),
        command=dict(type="str", required=False, default=""),
        schedule=dict(type="dict", required=False, default=dict()),
    )
    module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=False  # TODO ?
    )

    try:
        client = TruenasApi(
            module.params["url"], module.params["user"], module.params["password"]
        )
        crons = client.get("/cronjob")

    except Exception as e:
        module.fail_json(
            msg="Error fetching truenas crons: %s" % to_native(e),
            exception=traceback.format_exc(),
        )
        return

    state = module.params["state"]
    try:
        cron = match_cron(crons, module.params["description"])

        if state == "present":
            if not all(
                k in module.params
                for k in ["command", "user", "schedule", "description"]
            ):
                module.fail_json(
                    msg="all of the following params are required on state=present: command, user, schedule, description"
                )
                if "schedule" in module.params:
                    if not all(
                        k in module.params["schedule"]
                        for k in ["minute", "hour", "dow", "month", "dom"]
                    ):
                        module.fail_json(
                            msg="all of the following params are required on state=present: schedule.minute, schedule.hour, schedule.dow, schedule.month, schedule.dom"
                        )
                return
            if cron is None:
                response = create_cron(client, module.params)
            else:
                response = update_cron(client, cron, module.params)
            changed = response is not None
            result = dict(changed=changed, message="cron set")
            module.exit_json(**result)
        elif state == "absent":
            if cron is None:
                result = dict(changed=False, message="cron not present")
                module.exit_json(**result)
            else:
                response = delete_cron(client, cron)
                result = dict(changed=True, message="cron removed")
                module.exit_json(**result)

    except Exception as e:
        module.fail_json(
            msg="Error setting truenas cron '%s': %s"
            % (module.params["description"], to_native(e)),
            exception=traceback.format_exc(),
        )


def main():
    run_module()


if __name__ == "__main__":
    main()
