# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for sending control request of sensors.
"""

import json
import logging
import os
import sys
import time
from typing import Union, Optional
import uuid
import pandas
import requests
from ._constants import IOT_RESPONSE_ERROR, IOT_RESPONSE_SUCCESS, WS_DEFAULT_PORT, WS_MQTT_CONNECTION_TIMEOUT, WS_MQTT_DEFAULT_MAX_TIMEOUT, WS_MQTT_WAIT_TIME_INTERVAL
from ._mqtt import SwitchMQTT
from .._utils._utils import ApiInputs, _with_func_attrs, is_valid_uuid
from ..cache.cache import get_cache, set_cache

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  %(name)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)

global _control_api_endpoint
global _control_ws_host
global _control_ws_port
global _control_ws_username
global _control_ws_password
global _control_ws_max_timeout

_control_api_endpoint = ''
_control_ws_host = ''
_control_ws_port = WS_DEFAULT_PORT
_control_ws_username = ''
_control_ws_password = ''
_control_ws_max_timeout = WS_MQTT_DEFAULT_MAX_TIMEOUT


def set_control_variables(api_endpoint: str, ws_host: str, user_name: str, password: str,
                          ws_port: int = WS_DEFAULT_PORT, max_timeout: int = WS_MQTT_DEFAULT_MAX_TIMEOUT):
    """Set Control Variables

    Set Control Variables needed to enable control request to MQTT Broker when running locally.

    In Production, these are pulled from the deployment environment variables.

    Parameters
    ----------
    api_endpoint : str
        Platform IoT API Endpoint.
    host : str
        Host URL for MQTT connection. This needs to be datacenter specfic URL.
    port : int
        MQTT message broker port. Defaults to 443.
    user_name : str
        Username for MQTT connection
    password: str
        Password for MQTT connection
    max_timeout : int
        Max timeout set for the controls module. Defaults to 30 seconds.
    """
    global _control_api_endpoint
    global _control_ws_host
    global _control_ws_port
    global _control_ws_username
    global _control_ws_password
    global _control_ws_max_timeout

    # Check if endpoint is a valid URL
    if not api_endpoint.startswith('https://'):
        raise ValueError(
            "Invalid IoT API Endpoint. The IoT host should start with 'https://'.")

    # Check if host is a valid URL
    if not ws_host.startswith('wss://'):
        raise ValueError(
            "Invalid IoT Websocket MQTT Host. The IoT host should start with 'wss://'.")

    # Check if user_name and password are not empty
    if not user_name:
        raise ValueError("user_name cannot be empty.")
    if not password:
        raise ValueError("password cannot be empty.")

    # Check if max_timeout is greated than 0
    if max_timeout < 1:
        raise ValueError("max_timeout should be greater than 0.")

    # Set global variables
    _control_api_endpoint = api_endpoint
    _control_ws_host = ws_host
    _control_ws_port = ws_port
    _control_ws_username = user_name
    _control_ws_password = password
    _control_ws_max_timeout = max_timeout


@_with_func_attrs(df_required_columns=['ObjectPropertyId', 'Value', 'TTL'])
@_with_func_attrs(df_optional_columns=['DefaultControlValue', 'ControlName', 'ContinueValue'])
def submit_control_continue(api_inputs: ApiInputs, installation_id: Union[uuid.UUID, str], df: pandas.DataFrame, has_priority: bool, session_id: uuid.UUID, timeout: int = WS_MQTT_CONNECTION_TIMEOUT):
    """Submit control of sensor(s)

    Required fields are:

    - ObjectPropertyId
    - Value
    - TTL

    Optional fields are:
    - DefaultControlValue : if this column is present, after TTL, the sensor will turn into this value.
    - ControlContinue : if this column is present, this needs to verify if it's the first time controlling this or not.

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.
    df : pandas.DataFrame
        List of Sensors for control request.
    has_priority : bool
        Flag if dataframe passes contains has_priority column.
    session_id : uuid.UUID., Optional
        Session Id to reuse when communicating with IoT Endpoint and MQTT Broker
    timeout : int, Optional:
        Default value is 30 seconds. Value must be between 1 and max control timeout set in the control variables.
            When value is set to 0 it defaults to max timeout value.
            When value is above max timeout value it defaults to max timeout value.

    Returns
    -------
    tuple
        control_response  = is the list of sensors that were request to be controlled with status labelling if it was successful or not by the MQTTT message broker
    """
    global _control_api_endpoint
    global _control_ws_host
    global _control_ws_port
    global _control_ws_username
    global _control_ws_password
    global _control_ws_max_timeout

    default_control_value_column = 'DefaultControlValue'

    data_frame = df.copy()

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using the API.")
        return 'Invalid api_inputs.', pandas.DataFrame()

    if not is_valid_uuid(installation_id):
        logger.error("Installation Id is not a valid UUID.")
        return 'Invalid installation_id.', pandas.DataFrame()

    if data_frame.empty:
        logger.error("Dataframe is empty.")
        return 'Empty dataframe.', pandas.DataFrame()

    if timeout < 0:
        logger.error(
            f"Invalid timeout value. Timeout should be between 0 and {_control_ws_max_timeout}. Setting to zero will default to max timeout.")
        return 'Invalid timeout.', pandas.DataFrame()

    if timeout > _control_ws_max_timeout:
        logger.critical(
            f'Timeout is greater than Max Timeout value. Setting timeout to Max Timeout Value instead.')
        timeout = _control_ws_max_timeout

    if timeout == 0:
        timeout = _control_ws_max_timeout

    if not is_valid_uuid(session_id):
        session_id = uuid.uuid4()

    required_columns = getattr(submit_control, 'df_required_columns')
    proposed_columns = data_frame.columns.tolist()

    if not set().issubset(data_frame.columns):
        logger.exception('Missing required column(s): %s', set(
            required_columns).difference(proposed_columns))
        return 'control.submit_control(): dataframe must contain the following columns: ' + ', '.join(
            required_columns), pandas.DataFrame()

    control_cache_key = f"{api_inputs.api_project_id}-submit-control-cache-devtest"

    control_cache_df = get_control_cache(
        api_inputs=api_inputs, key=control_cache_key, scope_id=api_inputs.api_project_id)

    if control_cache_df.empty:
        logger.error('Cache is empty.')
        control_cache_df = pandas.DataFrame(columns=['ObjectPropertyId'])

    # Check if Input Dataframe sensors is present in the Cache (Dictionary of Records)
    # Normalize casing to lowercase for comparison
    data_frame['NormalizedObjectPropertyId'] = data_frame['ObjectPropertyId'].str.lower()
    control_cache_df['NormalizedObjectPropertyId'] = control_cache_df['ObjectPropertyId'].str.lower()

    # Check if each row's ObjectPropertyId in data_frame is in control_cache_df
    data_frame['ExistsInControlCache'] = data_frame['NormalizedObjectPropertyId'].isin(
        control_cache_df['NormalizedObjectPropertyId'])

    # Drop the normalized columns - only used for checking
    data_frame.drop(columns=['NormalizedObjectPropertyId'], inplace=True)
    control_cache_df.drop(columns=['NormalizedObjectPropertyId'], inplace=True)

    # If Present, check if "ContinueValue" column value is present in Input Dataframe
    if 'ContinueValue' in data_frame.columns:
        data_frame['ContinueValuePresent'] = data_frame['ExistsInControlCache'] & data_frame['ContinueValue'].notnull()
        # Replace values in 'Value' column where 'ContinueValuePresent' is True with the value from 'ContinueValue'
        data_frame.loc[data_frame['ContinueValuePresent'],
                       'Value'] = data_frame['ContinueValue']
    else:
        data_frame['ContinueValuePresent'] = False

    df_matrix = data_frame.copy()

    # Drop the ContinueValue, ExistsInControlCache, and ContinueValuePresent columns as no longer needed
    data_frame.drop(
        columns=['ContinueValue', 'ContinueValuePresent', 'ExistsInControlCache'], inplace=True)

    control_columns_required = ['ObjectPropertyId', 'Value', 'TTL', 'Priority']
    data_frame.drop(data_frame.columns.difference(
        control_columns_required), axis=1, inplace=True)

    # We convert these columns to the required payload property names
    data_frame = data_frame.rename(columns={'ObjectPropertyId': 'id',
                                            'Value': 'v', 'TTL': 'dsecs'})

    if has_priority:
        if not 'Priority' in data_frame:
            logger.error(
                f"has_priority is set to True, but the dataframe does not have the column 'Priority'.")
            return 'Missing Priority column', pandas.DataFrame()
        else:
            data_frame = data_frame.rename(columns={'Priority': 'p'})

    json_payload = {
        "sensors": data_frame.to_dict(orient='records'),
        "email": api_inputs.email_address,
        "userid": api_inputs.user_id,
        "sessionId": str(session_id)
    }

    url = f"{_control_api_endpoint}/api/gateway/{str(installation_id)}/log-control-request"

    headers = api_inputs.api_headers.default

    logger.info("Sending Control Request to IoT API: POST %s", url)
    logger.info("Control Request Session Id: %s", str(session_id))
    logger.info("Control Request for User: %s=%s",
                api_inputs.email_address, api_inputs.user_id)

    response = requests.post(url, json=json_payload, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    response_object = json.loads(response.text)

    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.",
                     response.status_code, response.reason)
        logger.error(response_object[IOT_RESPONSE_ERROR])
        return response_status, pandas.DataFrame()
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s',
                     response.request.url)
        return response_status, pandas.DataFrame()

    if not response_object[IOT_RESPONSE_SUCCESS]:
        logger.error(response_object[IOT_RESPONSE_ERROR])
        return response_object[IOT_RESPONSE_SUCCESS], pandas.DataFrame()

    # Proceeds when the control request is successful
    logger.info('IoT API Control Request is Successful.')

    data_frame = df.copy()

    if default_control_value_column in data_frame.columns:
        control_columns_required.append(default_control_value_column)

    data_frame = data_frame.rename(columns={'ObjectPropertyId': 'sensorId',
                                            'Value': 'controlValue', 'TTL': 'duration', 'DefaultControlValue': 'defaultControlValue'})

    if has_priority:
        if not 'Priority' in data_frame:
            logger.error(
                f"The dataframe does not have the column 'Priority'.")
        else:
            data_frame = data_frame.rename(columns={'Priority': 'priority'})

    switch_mqtt = SwitchMQTT(host_address=_control_ws_host, host_port=_control_ws_port,
                             username=_control_ws_username, password=_control_ws_password,
                             session_id=session_id, client_id=api_inputs.user_id, email=api_inputs.email_address,
                             project_id=api_inputs.api_project_id, installation_id=str(installation_id))

    is_connected = switch_mqtt.connect(timeout=timeout)

    if not is_connected:
        logger.info("Could not connect to MQTT Broker.")
        return 'Could not connect to MQTT Broker.', pandas.DataFrame()

    def process_paged_request(df, page_size: int = 20):
        paged_results = pandas.DataFrame()
        total_rows = len(df)
        num_pages = (total_rows + page_size - 1) // page_size

        for page_num in range(num_pages):
            start_idx = page_num * page_size
            end_idx = min((page_num + 1) * page_size, total_rows)

            # Get the data for the current page
            page_data = df.iloc[start_idx:end_idx]

            result = send_control(page_data)
            paged_results = pandas.concat([paged_results, result])

        return paged_results

    def send_control(page_data):
        retry_count = 0
        max_retries = 3
        success_results = pandas.DataFrame()
        missing_results = pandas.DataFrame()

        dataframe_to_control = page_data.copy()

        while retry_count < max_retries:
            success_response, missing_response = switch_mqtt.send_control_request(
                sensors=dataframe_to_control.to_dict(orient='records'))

            if not isinstance(success_response, pandas.DataFrame):
                logger.error(success_response)
                retry_count += 1
                time.sleep(1)
                continue

            if not success_response.empty:
                logger.info("Sensors that were successful in control request:")
                logger.info(success_response.to_string(index=False))
                success_results = pandas.concat(
                    [success_results, success_response])

            if not missing_response.empty:
                logger.error(
                    "Sensors that aren't successful in control request.")
                logger.info(missing_response.to_string(index=False))
                missing_results = pandas.concat(
                    [missing_results, missing_response])

            if missing_response.empty:
                break

            # Discount the successful control requests from the ones going for a retry
            if not success_response.empty:
                dataframe_to_control = dataframe_to_control[~dataframe_to_control['sensorId'].isin(
                    success_response['sensorId'])]

            retry_count += 1
            if retry_count < max_retries:
                time.sleep(1)

        if missing_results.empty:
            success_results['status'] = True
            success_results['writeStatus'] = 'Complete'
            control_result = success_results.copy()
        else:
            control_result = pandas.merge(page_data, missing_results, left_on='sensorId',
                                          right_on='sensorId', how='left', suffixes=('_df1', '_df2'))

            control_result['status'] = control_result['writeStatus'].isnull()

            columns_to_drop = ['controlValue_df2', 'duration_df2',
                               'priority_df2', 'defaultControlValue_df2']

            # Filter columns that exist in the dataframe
            existing_columns_to_drop = [
                col for col in columns_to_drop if col in control_result.columns]

            if existing_columns_to_drop:
                control_result.drop(
                    existing_columns_to_drop, axis=1, inplace=True)

            control_result['status'] = control_result['status'].fillna(True)

            control_result = control_result.rename(columns={
                'controlValue_df1': 'controlValue',
                'duration_df1': 'duration',
                'priority_df1': 'priority',
                'defaultControlValue_df1': 'defaultControlValue'
            })

        logger.info(control_result)
        return control_result

    control_results = process_paged_request(data_frame)
    switch_mqtt.disconnect()

    # Update cache =========
    control_result_matrix = control_results.copy()
    
    control_result_matrix.drop(control_result_matrix.columns.difference(
        ['sensorId']), axis=1, inplace=True)
    control_result_matrix = control_result_matrix.rename(
        columns={'sensorId': 'ObjectPropertyId'})

    # Remove rows where ExistsInControlCache is True and ContinueValuePresent is False
    # These are candidate for stopping control / relinquish cache
    df_matrix = df_matrix[~((df_matrix['ExistsInControlCache'] == True) &
                            (df_matrix['ContinueValuePresent'] == False))]
    df_matrix.drop(
        columns=['Value', 'TTL', 'Priority', 'ContinueValue', 'ContinueValuePresent', 'ExistsInControlCache'], inplace=True)

    # Identify sensorId values in obj_df that are not in df_a['ObjectPropertyId']
    to_update_in_cache = control_result_matrix[~control_result_matrix['ObjectPropertyId'].isin(
        df_matrix['ObjectPropertyId'])]

    # Add missing rows to df_matrix for cache update
    df_matrix = pandas.concat(
        [df_matrix, to_update_in_cache], ignore_index=True)

    # change to dict of records for caching
    dict_of_records = df_matrix.to_dict(orient='records')
    set_control_cache(api_inputs=api_inputs, key=control_cache_key,
                      scope_id=api_inputs.api_project_id, val=dict_of_records)

    return control_results


@_with_func_attrs(df_required_columns=['ObjectPropertyId', 'Value', 'TTL'])
@_with_func_attrs(df_optional_columns=['DefaultControlValue'])
def submit_control(api_inputs: ApiInputs, installation_id: Union[uuid.UUID, str], df: pandas.DataFrame, has_priority: bool, session_id: uuid.UUID, timeout: int = WS_MQTT_CONNECTION_TIMEOUT):
    """Submit control of sensor(s)

    Required fields are:

    - ObjectPropertyId
    - Value
    - TTL
    - DefaultControlValue (Optional)

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.
    df : pandas.DataFrame
        List of Sensors for control request.
    has_priority : bool
        Flag if dataframe passes contains has_priority column.
    session_id : uuid.UUID., Optional
        Session Id to reuse when communicating with IoT Endpoint and MQTT Broker
    timeout : int, Optional:
        Default value is 30 seconds. Value must be between 1 and max control timeout set in the control variables.
            When value is set to 0 it defaults to max timeout value.
            When value is above max timeout value it defaults to max timeout value.

    Returns
    -------
    tuple
        control_response  = is the list of sensors that were request to be controlled with status labelling if it was successful or not by the MQTTT message broker
    """
    global _control_api_endpoint
    global _control_ws_host
    global _control_ws_port
    global _control_ws_username
    global _control_ws_password
    global _control_ws_max_timeout

    default_control_value_column = 'DefaultControlValue'

    data_frame = df.copy()

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using the API.")
        return 'Invalid api_inputs.', pandas.DataFrame()

    if not is_valid_uuid(installation_id):
        logger.error("Installation Id is not a valid UUID.")
        return 'Invalid installation_id.', pandas.DataFrame()

    if data_frame.empty:
        logger.error("Dataframe is empty.")
        return 'Empty dataframe.', pandas.DataFrame()

    if timeout < 0:
        logger.error(
            f"Invalid timeout value. Timeout should be between 0 and {_control_ws_max_timeout}. Setting to zero will default to max timeout.")
        return 'Invalid timeout.', pandas.DataFrame()

    if timeout > _control_ws_max_timeout:
        logger.critical(
            f'Timeout is greater than Max Timeout value. Setting timeout to Max Timeout Value instead.')
        timeout = _control_ws_max_timeout

    if timeout == 0:
        timeout = _control_ws_max_timeout

    if not is_valid_uuid(session_id):
        session_id = uuid.uuid4()

    required_columns = getattr(submit_control, 'df_required_columns')
    proposed_columns = data_frame.columns.tolist()

    if not set().issubset(data_frame.columns):
        logger.exception('Missing required column(s): %s', set(
            required_columns).difference(proposed_columns))
        return 'control.submit_control(): dataframe must contain the following columns: ' + ', '.join(
            required_columns), pandas.DataFrame()

    control_columns_required = ['ObjectPropertyId', 'Value', 'TTL', 'Priority']
    data_frame.drop(data_frame.columns.difference(
        control_columns_required), axis=1, inplace=True)

    # We convert these columns to the required payload property names
    data_frame = data_frame.rename(columns={'ObjectPropertyId': 'id',
                                            'Value': 'v', 'TTL': 'dsecs'})

    if has_priority:
        if not 'Priority' in data_frame:
            logger.error(
                f"has_priority is set to True, but the dataframe does not have the column 'Priority'.")
            return 'Missing Priority column', pandas.DataFrame()
        else:
            data_frame = data_frame.rename(columns={'Priority': 'p'})

    json_payload = {
        "sensors": data_frame.to_dict(orient='records'),
        "email": api_inputs.email_address,
        "userid": api_inputs.user_id,
        "sessionId": str(session_id)
    }

    url = f"{_control_api_endpoint}/api/gateway/{str(installation_id)}/log-control-request"

    headers = api_inputs.api_headers.default

    logger.info("Sending Control Request to IoT API: POST %s", url)
    logger.info("Control Request Session Id: %s", str(session_id))
    logger.info("Control Request for User: %s=%s",
                api_inputs.email_address, api_inputs.user_id)

    response = requests.post(url, json=json_payload, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    response_object = json.loads(response.text)

    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.",
                     response.status_code, response.reason)
        logger.error(response_object[IOT_RESPONSE_ERROR])
        return response_status, pandas.DataFrame()
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s',
                     response.request.url)
        return response_status, pandas.DataFrame()

    if not response_object[IOT_RESPONSE_SUCCESS]:
        logger.error(response_object[IOT_RESPONSE_ERROR])
        return response_object[IOT_RESPONSE_SUCCESS], pandas.DataFrame()

    # Proceeds when the control request is successful
    logger.info('IoT API Control Request is Successful.')

    data_frame = df.copy()

    if default_control_value_column in data_frame.columns:
        control_columns_required.append(default_control_value_column)

    data_frame = data_frame.rename(columns={'ObjectPropertyId': 'sensorId',
                                            'Value': 'controlValue', 'TTL': 'duration', 'DefaultControlValue': 'defaultControlValue'})

    if has_priority:
        if not 'Priority' in data_frame:
            logger.error(
                f"The dataframe does not have the column 'Priority'.")
        else:
            data_frame = data_frame.rename(columns={'Priority': 'priority'})

    switch_mqtt = SwitchMQTT(host_address=_control_ws_host, host_port=_control_ws_port,
                             username=_control_ws_username, password=_control_ws_password,
                             session_id=session_id, client_id=api_inputs.user_id, email=api_inputs.email_address,
                             project_id=api_inputs.api_project_id, installation_id=str(installation_id))

    is_connected = switch_mqtt.connect(timeout=timeout)

    if not is_connected:
        logger.info("Could not connect to MQTT Broker.")
        return 'Could not connect to MQTT Broker.', pandas.DataFrame()

    def process_paged_request(df, page_size: int = 20):
        paged_results = pandas.DataFrame()
        total_rows = len(df)
        num_pages = (total_rows + page_size - 1) // page_size

        for page_num in range(num_pages):
            start_idx = page_num * page_size
            end_idx = min((page_num + 1) * page_size, total_rows)

            # Get the data for the current page
            page_data = df.iloc[start_idx:end_idx]

            result = send_control(page_data)
            paged_results = pandas.concat([paged_results, result])

        return paged_results

    def send_control(page_data):
        retry_count = 0
        max_retries = 3
        success_results = pandas.DataFrame()
        missing_results = pandas.DataFrame()

        dataframe_to_control = page_data.copy()

        while retry_count < max_retries:
            success_response, missing_response = switch_mqtt.send_control_request(
                sensors=dataframe_to_control.to_dict(orient='records'))

            if not isinstance(success_response, pandas.DataFrame):
                logger.error(success_response)
                retry_count += 1
                time.sleep(1)
                continue

            if not success_response.empty:
                logger.info("Sensors that were successful in control request:")
                logger.info(success_response.to_string(index=False))
                success_results = pandas.concat(
                    [success_results, success_response])

            if not missing_response.empty:
                logger.error(
                    "Sensors that aren't successful in control request.")
                logger.info(missing_response.to_string(index=False))
                missing_results = pandas.concat(
                    [missing_results, missing_response])

            if missing_response.empty:
                break

            # Discount the successful control requests from the ones going for a retry
            if not success_response.empty:
                dataframe_to_control = dataframe_to_control[~dataframe_to_control['sensorId'].isin(
                    success_response['sensorId'])]

            retry_count += 1
            if retry_count < max_retries:
                time.sleep(1)

        if missing_results.empty:
            success_results['status'] = True
            success_results['writeStatus'] = 'Complete'
            control_result = success_results.copy()
        else:
            control_result = pandas.merge(page_data, missing_results, left_on='sensorId',
                                          right_on='sensorId', how='left', suffixes=('_df1', '_df2'))

            control_result['status'] = control_result['writeStatus'].isnull()

            columns_to_drop = ['controlValue_df2', 'duration_df2',
                               'priority_df2', 'defaultControlValue_df2']

            # Filter columns that exist in the dataframe
            existing_columns_to_drop = [
                col for col in columns_to_drop if col in control_result.columns]

            if existing_columns_to_drop:
                control_result.drop(
                    existing_columns_to_drop, axis=1, inplace=True)

            control_result['status'] = control_result['status'].fillna(True)

            control_result = control_result.rename(columns={
                'controlValue_df1': 'controlValue',
                'duration_df1': 'duration',
                'priority_df1': 'priority',
                'defaultControlValue_df1': 'defaultControlValue'
            })

        logger.info(control_result)
        return control_result

    control_results = process_paged_request(data_frame)

    switch_mqtt.disconnect()

    return control_results


def get_control_cache(api_inputs: ApiInputs, key: str, scope_id: str) -> pandas.DataFrame:
    try:
        control_cache_res = get_cache(
            api_inputs=api_inputs, scope="Portfolio", key=key, scope_id=scope_id)

        if control_cache_res['success'] == True:
            cache_data = json.loads(control_cache_res['data'])
            df_from_records = pandas.DataFrame.from_records(
                cache_data)
            return df_from_records
        return pandas.DataFrame()
    except Exception as e:
        logger.error(
            f"An unexpected error occurred in getting Control cache: {e}")
        return pandas.DataFrame()


def set_control_cache(api_inputs: ApiInputs, key: str, scope_id: str, data: any):
    try:
        return set_cache(api_inputs=api_inputs, scope="Portfolio", key=key, val=data, scope_id=scope_id)
    except Exception as e:
        logger.error(
            f"An unexpected error occurred in setting Control cache: {e}")
        return pandas.DataFrame()
