#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017 Andrew Nelson
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: zabbix_ack
short_description: Acknowledge Zabbix Events
description:
   - Acknowledge Zabbix events.  Work derived from zabbix_host module.
version_added: "2.0"
author:
    - "Andrew Nelson"
requirements:
    - "python >= 2.6"
    - zabbix-api
options:
    server_url:
        description:
            - Url of Zabbix server, with protocol (http or https).
        required: true
        aliases: [ "url" ]
    login_user:
        description:
            - Zabbix user name, used to authenticate against the server.
        required: true
    login_password:
        description:
            - Zabbix user password.
        required: true
    eventid:
        description:
            - Event ID to acknowledge.
        required: true
    message:
        description:
            - Message to insert in acknowledgement.
        required: false
    close_event:
        description:
            - Weather or not to tell Zabbix to cloe the event.
            - Boolean value
        required: false
    timeout:
        description:
            - The timeout of API request (seconds).
        default: 10
'''

EXAMPLES = '''
- name: Create a new host or update an existing host's info
  local_action:
    module: zabbix_ack
    server_url: http://monitor.example.com
    login_user: username
    login_password: password
    eventid: 1234
    message: This event is fixed
    close: yes
'''

import copy

try:
    from zabbix_api import ZabbixAPI

    HAS_ZABBIX_API = True
except ImportError:
    HAS_ZABBIX_API = False

from ansible.module_utils.basic import AnsibleModule


class Event(object):
    def __init__(self, module, zbx):
        self._module = module
        self._zapi = zbx

    def ack(self, eventid, message, close_event):
        if close_event:
            action=1
        else:
            action=0

        try:
            result = self._zapi.event.acknowledge({'eventids': eventid, 'message': message,
                            'action': action})
            self._module.exit_json(changed=True, result="Acknowledged eventid: %d" % (eventid))

        except Exception as e:
            self._module.fail_json(msg="Failed to acknowledge event %d : %s" % (eventid, e))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(type='str', required=True, aliases=['url']),
            login_user=dict(type='str', required=True),
            login_password=dict(type='str', required=True, no_log=True),
            eventid=dict(type='int', required=True),
            message=dict(type='str', required=True),
            close_event=dict(type='bool', required=False, default=False),
            timeout=dict(type='int', default=10)
        ),
        supports_check_mode=False
    )

    if not HAS_ZABBIX_API:
        module.fail_json(msg="Missing required zabbix-api module (check docs or install with: pip install zabbix-api)")

    server_url = module.params['server_url']
    login_user = module.params['login_user']
    login_password = module.params['login_password']
    eventid = module.params['eventid']
    message = module.params['message']
    close_event = module.params['close_event']
    timeout = module.params['timeout']


    zbx = None
    # login to zabbix
    try:
        zbx = ZabbixAPI(server_url, timeout=timeout)
        zbx.login(login_user, login_password)
    except Exception as e:
        module.fail_json(msg="Failed to connect to Zabbix server: %s" % e)

    event = Event(module, zbx)
    event.ack(eventid,message,close_event)

if __name__ == '__main__':
    main()

