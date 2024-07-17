# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module containing the constants referenced by methods and functions defined in the controls module. This module
is not directly referenced by end users.
"""

IOT_RESPONSE_SUCCESS = 'success'
IOT_RESPONSE_ERROR = 'error'

WS_DEFAULT_PORT = 443
WS_MQTT_CONNECTION_TIMEOUT = 30
WS_MQTT_DEFAULT_MAX_TIMEOUT = 30
WS_MQTT_WAIT_TIME_INTERVAL = 0.1
WS_MQTT_MESSAGE_WAIT_TIME_INTERVAL = 0.1

CONTROL_REQUEST_ACTION_ACK = 'control-request-ack'
CONTROL_REQUEST_ACTION_RESULT = 'control-result'
