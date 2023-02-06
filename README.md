# truenas Collection for Ansible

This collection maintains truenas related modules maintained by Casey Link (ramblurr).

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
  truenas_tunable: 
    url: http://example.com
    password: example
    name: wireguard_interfaces
    value: wg0
    type: RC
```

## Author

This collection was created in 2020 by [Casey Link](https://outskirtslabs.com)
