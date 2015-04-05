#!/usr/bin/env python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: foreman_compute_profile
short_description: Manage Foreman Compute Profiles using Foreman API v2
description:
- Create and delete Foreman Compute Profiles using Foreman API v2
options:
  name:
    description: Name of Compute Profile
    required: true
    default: null
    aliases: []
  state:
    description: State of Compute Profile
    required: false
    default: present
    choices: ["present", "absent"]
  foreman_host:
    description: Hostname or IP address of Foreman
    required: false
    default: 127.0.0.1
  foreman_port:
    description: Port of Foreman API
    required: false
    default: 443
  foreman_user:
    description: Username to be used to authenticate on Foreman
    required: true
    default: null
  foreman_pass:
    description: Password to be used to authenticate user on Foreman
    required: true
    default: null
notes:
- Requires the python-foreman package to be installed. See https://github.com/Nosmoht/python-foreman.
author: Thomas Krahn
'''

EXAMPLES = '''
- name: Ensure Extra Large Compute Profile is present
  foreman_compute_profile:
    name: 4-Extra-Large
    state: present
    foreman_user: admin
    foreman_pass: secret
'''

try:
    from foreman.foreman import *
except ImportError:
    foremanclient_found = False
else:
    foremanclient_found = True

def ensure(module):
    changed = False
    # Set parameters
    name = module.params['name']
    state = module.params['state']
    foreman_host = module.params['foreman_host']
    foreman_port = module.params['foreman_port']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']

    theforeman = Foreman(hostname=foreman_host,
                         port=foreman_port,
                         username=foreman_user,
                         password=foreman_pass)

    data = {}
    data['name'] = name

    try:
        profile = theforeman.search_compute_profile(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get compute profile: ' + e.message)

    if not profile and state == 'present':
        try:
            theforeman.create_compute_profile(data=data)
            changed = True
        except ForemanError as e:
            module.fail_json(msg='Could not create compute profile: ' + e.message)

    if profile and state == 'absent':
        try:
            theforeman.delete_compute_profile(id=profile.get('id'))
            changed = True
        except ForemanError as e:
            module.fail_json(msg='Could not delete compute profile: ' + e.message)

    return changed

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(Type='str', required=True),
            state=dict(Type='str', Default='present', choices=['present', 'absent']),
            foreman_host=dict(Type='str', Default='127.0.0.1'),
            foreman_port=dict(Type='str', Default='443'),
            foreman_user=dict(Type='str', required=True),
            foreman_pass=dict(Type='str', required=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required')

    changed = ensure(module)
    module.exit_json(changed=changed, name=module.params['name'])

# import module snippets
from ansible.module_utils.basic import *
main()
