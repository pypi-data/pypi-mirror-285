
def setup_webpage_data_source(input_file, **kwargs):

    out = {"source": "webpage", "input_file": input_file}

    # Parse the user overrides.
    for key, value in kwargs.items():
        match key:
            case default:
                raise ValueError(f"Unknown parameter {key} received") 
    return out

def setup_azure_data_source(**kwargs):

    out = {"source": "azure_blob"}

    # Parse the user overrides.
    for key, value in kwargs.items():
        match key:
            case "client_id":
                out["client_id"] = value
            case "tenant_id":
                out["tenant_id"] = value
            case "client_secret":
                out["client_secret"] = value
            case "account_url":
                out["account_url"] = value
            case "container_name":
                out["container_name"] = value
            case "blob_name":
                out["blob_name"] = value
            case default:
                raise ValueError(f"Unknown parameter {key} received") 

    return out


def setup_aws_data_source(**kwargs):

    out = {"source": "aws_s3"}

    # Parse the user overrides.
    for key, value in kwargs.items():
        match key:
            case "access_key":
                out["access_key"] = value
            case "secret_token":
                out["secret_token"] = value
            case "bucket":
                out["bucket"] = value
            case "key":
                out["key"] = value
            case default:
                raise ValueError(f"Unknown parameter {key} received") 

    return out

def setup_slack_data_source(slack_token, channel_id, start_date, end_date):

    out = { "source" : "slack",
            "slack_token" : slack_token,
            "channel_id" : channel_id,
            "start_date" : start_date,
            "end_date" : end_date
           }

    return out

def setup_local_data_source(input_file, **kwargs):

    out = {"source": "local", 'input_file': input_file}

    # Parse the user overrides.
    for key, value in kwargs.items():
        match key:
            case default:
                raise ValueError(f"Unknown parameter {key} received") 

    return out

def setup_dataset(name, index_type, **kwargs):

    out = {"name" : name, "index_type" : index_type, "llm_model" : '', "embedding_model" : ''}

    # Parse the user overrides.
    for key, value in kwargs.items():
        match key:
            case "embedding_model":
                out['embedding_model'] = value
            case default:
                raise ValueError(f"Unknown parameter {key} received") 

    return out

def setup_image_database(database_url, database, table, **kwargs):

    out = { "database_type" : "sql",
            "database_url" : database_url,
            "name" : database,
            "table" : table,
           }

    return out

