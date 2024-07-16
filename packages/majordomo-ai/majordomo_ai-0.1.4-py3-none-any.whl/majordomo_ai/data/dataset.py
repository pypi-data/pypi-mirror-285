import requests
from pathlib import Path
import os
import json
from datetime import datetime

def create_user_response(result):
    response = {}
    r = result.json()
    if result.status_code == 200:
        response['status'] = 0
        response['response'] = ''
        response['error'] = ''
    else:
        response['status'] = -1
        response['error'] = r['detail']

    return response

def create_dataset_from_documents(connection, dataset, data_source, **kwargs):

    debug_on = False

    json_input = {}

    json_input['dataset'] = dataset

    json_input['user_token'] = connection['user_token']

    json_input['pdf_extractor'] = "PyMuPDF"

    json_input['data_source'] = data_source['source']
    del data_source['source']

    match json_input['data_source']:

        case "azure_blob":
            json_input['azure_blob'] = data_source

        case "aws_s3":
            json_input['aws_s3'] = data_source

        case "slack":
            json_input['slack_channel'] = data_source

        case "local":
            json_input['input_file'] = os.path.basename(data_source['input_file'])
            my_file = Path(data_source['input_file'])
            if not my_file.is_file():
                raise ValueError("Input file not found")

            file = {'file': open(data_source['input_file'], 'rb')}

            resp  = requests.post(connection['client_url'] + '/file_upload', files=file)

        case "webpage":
            json_input['input_file'] = data_source['input_file']

        case default:
           pass

    # Parse the user overrides.
    for key, value in kwargs.items():
        match key:
            case "debug_on":
                debug_on = value
            case "pdf_extractor":
                json_input['pdf_extractor'] = value
            case "image_dataset":
                json_input['image_dataset'] = value
            case "image_database":
                json_input['image_database'] = value
            case default:
                pass

    if json_input['pdf_extractor'] == "PDF2Image":
        if (json_input['image_dataset'] == '' or 
             json_input['image_database'] == ''):
                 raise Exception("Image extraction requires database in addition to vector database")

    try:
        headers = {"Content-Type": "application/json"}
        json_data = json.dumps(json_input)
        result = requests.post(connection['client_url'] + '/doc_ingestion', data=json_data, headers=headers)
        response_json = create_user_response(result)
    except Exception as e: raise

    return response_json
