import os
import json
import requests

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

class Dataset():

    def __init__(self, name, index_type, embedding_model=''):

        self.name = name
        self.index_type = index_type
        self.embedding_model = embedding_model

    def to_dict(self):
        out = {
                "name": self.name,
                "index_type": self.index_type,
                "embedding_model": self.embedding_model
            }

        return out

    def create_from_documents(self, user_token, data_source, **kwargs):

        json_input = {}
        client_url = os.environ['MAJORDOMO_AI_CLIENT_URL']

        json_input['dataset'] = self.to_dict()
        json_input['user_token'] = user_token
        json_input['pdf_extractor'] = "PyMuPDF"
        json_input['data_source'] = data_source.location

        match json_input['data_source']:

            case "azure_blob":
                json_input['azure_blob'] = data_source.src.to_dict()

            case "aws_s3":
                json_input['aws_s3'] = data_source.src.to_dict()

            case "slack":
                json_input['slack_channel'] = data_source.src.to_dict()

            case "local":
                json_input['input_file'] = os.path.basename(data_source.src.filename)
                my_file = Path(data_source.src.filename)
                if not my_file.is_file():
                    raise ValueError("Input file not found")

                file = {'file': open(data_source.src.filename, 'rb')}

                resp  = requests.post(client_url + '/file_upload', files=file)

            case "webpage":
                json_input['input_file'] = data_source.src.url

            case default:
               pass

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
