import os
import json
import requests
from pydantic import BaseModel, ValidationError

from .datasource import DataSource
from .models import StructuredDB, Dataset, QueryEngine
from pathlib import Path

client_url = os.environ['MAJORDOMO_AI_CLIENT_URL']

class DocumentIngestionRequest(BaseModel):
    user_token: str
    data_source: DataSource
    dataset: Dataset
    pdf_extractor: str
    image_dataset: Dataset | None = None
    image_database : StructuredDB | None = None

class DocQuery(BaseModel):
    user_token: str
    query_engine: QueryEngine
    dataset: Dataset
    query_str: str

def create_user_response(result):
    response = {}
    r = result.json()
    if result.status_code == 200:
        response['status'] = 0
        if r is not None:
            response['response'] = r['response']
        response['error'] = ''
    else:
        response['status'] = -1
        response['error'] = r['detail']

    return response

def create_dataset_from_documents(user_token, dataset, data_source, **kwargs):

    json_input = {}
    client_url = os.environ['MAJORDOMO_AI_CLIENT_URL']

    pdf_extractor = "PyMuPDF"
    # Parse the user overrides.
    for key, value in kwargs.items():
        match key:
            case "pdf_extractor":
                json_input['pdf_extractor'] = value
            case "image_dataset":
                json_input['image_dataset'] = value
            case "image_database":
                json_input['image_database'] = value
            case default:
                pass

    request_body = DocumentIngestionRequest(
                        user_token=user_token, 
                        data_source=data_source, 
                        dataset=dataset, 
                        pdf_extractor = pdf_extractor)

    match data_source.location:

        case "local":
            request_body.data_source.info.file_name = data_source.info.file_name
            os.path.basename(request_body.data_source.info.file_name)
            my_file = Path(data_source.info.file_name)
            if not my_file.is_file():
                raise ValueError("Input file not found")

            file = {'file': open(data_source.info.file_name, 'rb')}

            resp  = requests.post(client_url + '/file_upload', files=file)

        case default:
           pass

    try:
        headers = {"Content-Type": "application/json"}
        result = requests.post(client_url + '/doc_ingestion', data=json.dumps(request_body.model_dump(mode='json')), headers=headers)
        response_json = create_user_response(result)
    except Exception as e: raise

    return response_json

def query_from_dataset(user_token, query_engine, dataset, query_str):
        
    client_url = os.environ['MAJORDOMO_AI_CLIENT_URL']

    request_body = DocQuery(
                        user_token=user_token, 
                        query_engine=query_engine, 
                        dataset=dataset,
                        query_str = query_str)

    try:
        headers = {"Content-Type": "application/json"}
        result = requests.post(client_url + '/doc_query', data=json.dumps(request_body.model_dump(mode='json')), headers=headers)
        response_json = create_user_response(result)
    except Exception as e: raise

    return response_json

def image_query(user_token,
                query_engine,
                dataset,
                query_str,
                **kwargs
                ):

    request_body = DocQuery(
                        user_token=user_token, 
                        query_engine=query_engine, 
                        dataset=dataset,
                        query_str = query_str)

    try:
        headers = {"Content-Type": "application/json"}
        result = requests.post(client_url + '/image_query', data=json.dumps(request_body.model_dump(mode='json')), headers=headers)
        response_json = create_user_response(result)
    except Exception as e: raise

    return response_json
