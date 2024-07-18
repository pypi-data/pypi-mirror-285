from pydantic import BaseModel, ValidationError
from sqlalchemy import create_engine, select, Table, MetaData, delete
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.sql import text

import os
from pathlib import Path
import requests
import json
from .datasource import DataSource
from .models import StructuredDB, CsvUpload, SQLQuery
     
client_url = os.environ['MAJORDOMO_AI_CLIENT_URL']

def create_user_response(result):
    response = {}
    r = result.json()
    if result.status_code == 200:
        response['status'] = 0
        response['response'] = r['response']
        response['error'] = ''
    else:
        response['status'] = -1
        response['error'] = r['detail']

    return response

def create_sql_table_from_csv(database, data_source, table_name, **kwargs):

    if database.db_type != 'SQL':
        raise Exception("Incorrect database type")

    request_body = CsvUpload(sql_database=database, data_source=data_source, table_name=table_name, append=False)

    # Parse the user overrides.
    for key, value in kwargs.items():
        match key:
            case "append":
                request_body.append = value
            case default:
                pass

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
            raise Exception("Incorrect file location type")

    try:
        headers = {"Content-Type": "application/json"}
        result = requests.post(client_url + '/csv_ingestion', data=json.dumps(request_body.model_dump(mode='json')), headers=headers)

    except Exception as e: raise

    return result

def sql_tables_query(user_token, query_engine, database, table_names, query_str, **kwargs):

    client_url = os.environ['MAJORDOMO_AI_CLIENT_URL']

    if database.db_type != 'SQL':
        raise Exception("Incorrect database type")

    request_body = SQLQuery(user_token=user_token, 
                        query_engine=query_engine, 
                        database=database, 
                        table_names=table_names, 
                        query_str=query_str)

    # Parse the user overrides.
    for key, value in kwargs.items():
        match key:
            case default:
                pass

    try:
        headers = {"Content-Type": "application/json"}
        result = requests.post(client_url + '/sql_query', data=json.dumps(request_body.model_dump(mode='json')), headers=headers)
        response_json = create_user_response(result)

    except Exception as e: raise

    return response_json

def fetch_image_from_sql(database, table, image_id):

    if database.db_type != 'SQL':
        raise Exception("Incorrect database type")

    # Connect to DB and output data frame
    engine = create_engine(database.info.url + "/" + database.info.name)

    conn = engine.connect()

    metadata = MetaData()

    image_table = Table(table, metadata, autoload_with=engine)

    stmt = select(image_table).where(image_table.c.id == image_id)
    row = conn.execute(stmt)
    return(row.first().data)
