import requests
from pathlib import Path
import os
import json

def create_user_response(result):
    response = {}
    r = result.json()
    if result.status_code == 200:
        response['status'] = 0
        response['response'] = r['response']
        response['error'] = ''
    else:
        response['status'] = -1
        response['response'] = ''
        response['error'] = r['detail']

    return response

def doc_query(connection, 
              dataset, 
              llm_model, 
              query_str,
              **kwargs
              ):

    json_input = {}

    json_input['user_token'] = connection['user_token']

    # Fill the default values.
    json_input['dataset'] = dataset
    json_input['embedding_model'] = dataset['embedding_model']
    json_input['llm_model'] = llm_model
    json_input['dataset'] = dataset
    json_input['query'] = query_str
    json_input['temperature'] = 1.0
    json_input['top_k'] = 2

    # Parse the user overrides.
    for key, value in kwargs.items():
        match key:
            case "debug_on":
                debug_on = value
            case "temperature":
                json_input['temperature'] = value
            case "top_k":
                json_input['top_k'] = value
            case default:
                pass

    try:
        headers = {"Content-Type": "application/json"}
        json_data = json.dumps(json_input)
        result = requests.post(connection['client_url'] + '/doc_query', data=json_data, headers=headers)
        response_json = create_user_response(result)

    except Exception as e: raise

    return response_json

def image_query(connection,
                dataset,
                embedding_model,
                query_str,
                **kwargs
                ):
    debug_on = False

    json_input = {}

    json_input['user_token'] = connection['user_token']

    # Fill the default values.
    json_input['embedding_model'] = embedding_model
    json_input['llm_model'] = ''
    json_input['dataset'] = dataset
    json_input['temperature'] = 1.0
    json_input['query'] = query_str
    json_input['top_k'] = 2

    # Parse the user overrides.
    for key, value in kwargs.items():
        match key:
            case "debug_on":
                debug_on = value
            case "top_k":
                json_input['top_k'] = value
            case default:
                pass

    try:
        headers = {"Content-Type": "application/json"}
        json_data = json.dumps(json_input)
        result = requests.post(connection['client_url'] + '/image_query', data=json_data, headers=headers)
        response_json = create_user_response(result)
    except Exception as e: raise

    return response_json
