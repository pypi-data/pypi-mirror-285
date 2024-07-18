import os
import json
import requests
from pydantic import BaseModel, ValidationError
from .models import DocumentIngestionRequest

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

class Dataset(BaseModel):

    name : str
    index_type2 : str
    embedding_model : str 

    def create_from_documents(self, user_token, data_source, **kwargs):

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
                            dataset=self, 
                            pdf_extractor = pdf_extractor)

        match data_source.location:

            case "local":
                request_body.data_source.local.file_name = os.path.basename(data_source.src.filename)
                my_file = Path(data_source.local.file_name)
                if not my_file.is_file():
                    raise ValueError("Input file not found")

                file = {'file': open(data_source.local.file_name, 'rb')}

                resp  = requests.post(client_url + '/file_upload', files=file)

            case default:
               pass

        if json_input['pdf_extractor'] == "PDF2Image":
            if (json_input['image_dataset'] == '' or 
                 json_input['image_database'] == ''):
                     raise Exception("Image extraction requires database in addition to vector database")

        try:
            headers = {"Content-Type": "application/json"}
            json_data = json.dumps(json_input)
            result = requests.post(client_url + '/doc_ingestion', data=json_data, headers=headers)
            response_json = create_user_response(result)
        except Exception as e: raise

        return response_json
