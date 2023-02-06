#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
import requests
import copy
import traceback


DOCUMENTATION = r"""
---
module: truenas_tunable
author: "Casey Link <unnamedrambler@gmail.com>"
short_description: Manage TrueNAS system tunables
description:
  - Manage TrueNAS system tunables
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
  name:
    description:
      - The name of the tunable
    type: str
    required: true
  value:
    description:
      - The value of the tunable, required if state is 'present'
    type: str
  comment:
    description:
      - The comment of the tunable
    type: str
  type:
    description:
      - The type of the tunable
    choices: ["SYSCTL", "RC", "LOADER"]
    type: str
  enabled:
    description:
      - Whether the tunable is enabled or not
    type: bool

requirements:
  - "python >= 3.7"
"""
EXAMPLES = r"""
- name: add wireguard interface
  truenas_tunable:
    url: https://example.com
    password: example
    state: present
    name:  wireguard_interfaces
    value: wg0
    type: SYSCTL
    comment: The primary wireguard interface

- name: remove wireguard interface
  truenas_tunable:
    url: https://example.com
    password: example
    state: present
    name:  wireguard_interfaces
    type: SYSCTL
    state: absent
"""


def without(d, key):
    new_d = copy.deepcopy(d)
    new_d.pop(key)
    return new_d


API_ENDPOINT = "%(hostname)s/api/v2.0"


class TruenasApi(object):
    def __init__(self, hostname, username, password):
        self.auth_tuple = (username, password)
        self.api_endpoint = API_ENDPOINT % {"hostname": hostname}
        self.headers = {"Content-Type": "application/json"}

    def _result(self, r):
        if r.ok:
            try:
                return r.json()
            except:
                return r.text
        raise ValueError(r)

    def _strip(self, resource):
        if resource[0] == "/":
            return resource[1:]

    def _uri(self, resource):
        return "%s/%s/" % (self.api_endpoint, self._strip(resource))

    def post(self, resource, data=None):
        uri = self._uri(resource)
        r = requests.post(uri, json=data, headers=self.headers, auth=self.auth_tuple)
        return self._result(r)

    def put(self, resource, data=None):
        uri = self._uri(resource)
        r = requests.put(uri, json=data, headers=self.headers, auth=self.auth_tuple)
        return self._result(r)

    def delete(self, resource):
        uri = self._uri(resource)
        r = requests.delete(uri, headers=self.headers, auth=self.auth_tuple)
        return self._result(r)

    def get(self, resource, data=None):
        uri = self._uri(resource)
        r = requests.get(uri, headers=self.headers, auth=self.auth_tuple)
        return self._result(r)


def match_tunable(tunables, type, var):
    for t in tunables:
        if t["var"] == var and t["type"] == type:
            return t
    return None


def check_drift_tunable(tunable, params):
    keys = ["var", "value", "type", "comments", "enabled"]


def create_tunable(client, params):
    payload = dict(
        comment=params["comment"],
        enabled=params["enabled"],
        type=params["type"],
        value=params["value"],
        var=params["name"],
    )
    return client.post("/tunable", payload)


def update_tunable(client, tunable, params):
    payload = dict(
        comment=params["comment"],
        enabled=params["enabled"],
        type=params["type"],
        value=params["value"],
        var=params["name"],
    )
    tunable_plain = without(tunable, "id")
    if tunable_plain == payload:
        return None
    else:
        tid = tunable["id"]
        return client.put(f"/tunable/id/{tid}", payload)


def delete_tunable(client, tunable):
    tid = tunable["id"]
    return client.delete(f"/tunable/id/{tid}")


def run_module():
    module_args = dict(
        url=dict(type="str", required=True),
        user=dict(type="str", default="root"),
        password=dict(type="str", required=True, no_log=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        enabled=dict(type="bool", default=True),
        comment=dict(type="str", required=False, default=""),
        name=dict(type="str", required=True),
        value=dict(type="str"),
        type=dict(type="str", choices=["SYSCTL", "RC", "LOADER"], default="enabled"),
    )
    module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=False  # TODO ?
    )

    try:
        client = TruenasApi(
            module.params["url"], module.params["user"], module.params["password"]
        )
        tunables = client.get("/tunable")
    except Exception as e:
        print(e)
        module.fail_json(
            msg="Error fetching truenas tunables: %s" % to_native(e),
            exception=traceback.format_exc(),
        )
        return

    state = module.params["state"]
    try:
        tunable = match_tunable(tunables, module.params["type"], module.params["name"])

        if state == "present":
            if module.params["value"] is None:
                module.fail_json(
                    msg="one of the following params is requried on state=present: value"
                )
                return
            if tunable is None:
                response = create_tunable(client, module.params)
            else:
                response = update_tunable(client, tunable, module.params)
            changed = response is not None
            result = dict(changed=changed, message="tunable set")
            module.exit_json(**result)
        elif state == "absent":
            if tunable is None:
                result = dict(changed=False, message="tunable not present")
                module.exit_json(**result)
            else:
                response = delete_tunable(client, tunable)
                result = dict(changed=True, message="tunable removed")
                module.exit_json(**result)

    except Exception as e:
        print(e)
        module.fail_json(
            msg="Error setting truenas tunable %s %s: %s"
            % (module.params["type"], module.params["name"], to_native(e)),
            exception=traceback.format_exc(),
        )


def main():
    run_module()


if __name__ == "__main__":
    main()
