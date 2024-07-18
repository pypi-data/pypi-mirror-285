from enum import Enum, IntEnum
from pydantic import BaseModel, ValidationError

class AzureBlobDataSource(BaseModel):

    client_id : str
    tenant_id : str
    client_secret : str
    account_url : str
    container_name : str
    blob_name : str

class AWSS3DataSource(BaseModel):
    access_key : str
    secret_token : str
    bucket : str
    key : str

class WebDataSource(BaseModel):
    url : str

class LocalDataSource(BaseModel):
    file_name: str

class LocationEnum(str, Enum):
    local = 'local'
    webpage = 'webpage'
    aws_s3 = 'aws_s3'
    azure_blob = 'azure_blob'
    slack = 'slack'

class DataSource(BaseModel):

    location : LocationEnum

    info : AzureBlobDataSource | AWSS3DataSource | LocalDataSource | WebDataSource

