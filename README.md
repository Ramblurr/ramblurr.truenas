# FreeNAS Collection for Ansible

This collection maintains FreeNAS related modules maintained by Casey Link (ramblurr).

## Usage

Install this collection locally:

    ansible-galaxy collection install geerlingguy.k8s -p ./collections

Then you can use the roles from the collection in your playbooks:

```yaml
---
- hosts: all

collections:
- ramblurr.freenas

tasks:
- name: set tunable
  freenas_tunable: 
    url: http://example.com
    password: example
    name: wireguard_interfaces
    value: wg0
    type: RC
```

## Author

This collection was created in 2020 by [Casey Link](https://outskirtslabs.com)
