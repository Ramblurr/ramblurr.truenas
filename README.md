# TrueNAS Collection for Ansible
[![](https://img.shields.io/badge/license-AGPL--v3--or--later-blue)](./LICENSE)

This collection maintains TrueNAS related modules maintained by Casey Link (ramblurr).

## Usage

Install this collection locally:

    ansible-galaxy collection install ramblurr.truenas -p ./collections

Then you can use the roles from the collection in your playbooks:

```yaml
---
- hosts: all

collections:
- ramblurr.truenas

tasks:
- name: set tunable
  ramblurr.truenas.truenas_tunable: 
    url: http://example.com
    password: example
    name: wireguard_interfaces
    value: wg0
    type: RC

- name: run script on schedule
  ramblurr.truenas.truenas_cron:
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
```

## License

```
Copyright (C) 2020-2023 Casey Link https://outskirtslabs.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
