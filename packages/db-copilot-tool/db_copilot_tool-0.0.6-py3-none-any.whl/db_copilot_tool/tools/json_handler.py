import json


def json_serializable(value):
    try:
        json.dumps(value)
        return True
    except:
        return False


def convert_to_json_serializable(value):
    if isinstance(value, dict):
        return {k: convert_to_json_serializable(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [convert_to_json_serializable(v) for v in value]
    else:
        if not json_serializable(value):
            return str(value)
        else:
            return value
