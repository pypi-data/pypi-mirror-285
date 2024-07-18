import os
import requests
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

class DocQuery():

    def __init__(self, llm_model, temperature=1.0, top_k=2):
        self.llm_model = llm_model
        self.temperature = temperature
        self.top_k = top_k

    def from_dataset(self, user_token, dataset, query_str):
        
        json_input = {}
        client_url = os.environ['MAJORDOMO_AI_CLIENT_URL']

        json_input['dataset'] = dataset.to_dict()
        json_input['embedding_model'] = dataset.embedding_model
        json_input['llm_model'] = llm_model
        json_input['dataset'] = dataset
        json_input['query'] = query_str
        json_input['temperature'] = self.temperature
        json_input['top_k'] = self.top_k

        try:
            headers = {"Content-Type": "application/json"}
            json_data = json.dumps(json_input)
            result = requests.post(client_url + '/doc_query', data=json_data, headers=headers)
            response_json = create_user_response(result)

