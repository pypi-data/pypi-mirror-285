from enum import Enum, IntEnum
from pydantic import BaseModel
from typing import Optional
from .datasource import DataSource

class SQLDatabase(BaseModel):
    url : str
    name: str

class DBTypeEnum(str, Enum):
    sql = 'SQL'

class StructuredDB(BaseModel):
    db_type: DBTypeEnum
    info: SQLDatabase

class CsvUpload(BaseModel):
    sql_database: StructuredDB
    data_source: DataSource
    table_name: str
    append: bool

class Dataset(BaseModel):
    name : str
    index_type : str
    embedding_model : str 

class QueryEngine(BaseModel):
    embedding_model: str
    llm_model: str
    temperature: float | None = 1.0
    top_k: float | None = 2

class AccessInfoResponse(BaseModel):
    user: str
    cost_tags: str
    model_provider: str
    llm_model : str
    embedding_model : str
    model_access_key: str
    vectordb_provider: str
    vectordb_access_key: str

class SQLQuery(BaseModel):
    user_token: str
    database: StructuredDB
    query_engine: QueryEngine
    table_names: list[str]
    query_str: str

class MetaQueryResponse(BaseModel):
    response: str
    metadata: str

class QueryResponse(BaseModel):
    response: str

class ImageQueryResponse(BaseModel):
    response: list


