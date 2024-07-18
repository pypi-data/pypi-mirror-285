
def setup_slack_data_source(slack_token, channel_id, start_date, end_date):

    out = { "source" : "slack",
            "slack_token" : slack_token,
            "channel_id" : channel_id,
            "start_date" : start_date,
            "end_date" : end_date
           }

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

