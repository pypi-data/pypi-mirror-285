import json
import time
from dataclasses import dataclass, field
from typing import Any, List, Optional

from .core import (validate_content, validate_optional_type, validate_type,
                   validate_type_to_be_one_of)


def parse_choice(choice_data):
    validate_type(choice_data.get('index'), int, 'index')
    validate_type(choice_data.get('text'), str, 'text')
    validate_type(choice_data.get('finish_reason'), str, 'finish_reason')
    return choice_data


def parse_usage(usage_data):
    if usage_data is None:
        return None
    validate_type(usage_data.get('prompt_tokens'), int, 'prompt_tokens')
    validate_type(usage_data.get('completion_tokens'),
                  int, 'completion_tokens')
    validate_type(usage_data.get('total_tokens'), int, 'total_tokens')
    return usage_data


def parse_generation_error(error_data):
    if error_data is None:
        return None
    validate_type(error_data.get('message'), str, 'message')
    validate_optional_type(error_data.get('code'), str, 'code')
    validate_optional_type(error_data.get('type'), str, 'type')
    return error_data


def parse_result(data: dict) -> dict:
    validate_type(data.get('id'), str, 'id')
    validate_optional_type(data.get('object'), str, 'object')
    validate_type(data.get('created'), int, 'created')
    validate_optional_type(data.get('model'), str, 'model')

    choices_data = data.get('choices')
    validate_type(choices_data, list, 'choices')
    if not choices_data:
        raise ValueError("choices must not be empty")
    choices = [parse_choice(choice) for choice in choices_data]
    usage = parse_usage(data.get('usage', None))
    error = parse_generation_error(data.get('error', None))
    result = {
        'id': data['id'],
        'object': data['object'] if 'object' in data else None,
        'created': data['created'],
        'choices': choices,
        'usage': usage,
        'error': error if error else None
    }
    # removing all None from result
    result = {k: v for k, v in result.items() if v is not None}    
    return result


def parse_message(message: Any) -> Any:
    validate_type(message.get('role'), str, 'role')
    validate_content(message.get('role'), [
                     'user', 'assistant', 'system', 'bot', 'chatbot', 'model'])
    validate_type_to_be_one_of(message.get('content'), [str, object], 'type')
    if isinstance(message.get('content'), object):
        # Making sure if content has type and corresponding data
        content = message.get('content')
        validate_type(content.get('type'), str, 'type')
        validate_content(content.get('type'), ['image_url', 'text'])
        # Making sure type is image or text
        type = content.get('type')
        if type == 'image_url':
            validate_type(content.get('image_url'), str, 'image_url')
        elif type == 'text':
            validate_type(content.get('text'), str, 'text')
        else:
            raise ValueError(
                f"Invalid content type. We expect 'text' or 'image' type. Got: {type}")
    return message


def parse_messages(messages: List[Any]) -> List[Any]:
    if len(messages) == 0:
        return []
    return [parse_message(message) for message in messages]


def parse_model_parameters(parameters: dict) -> dict:
    # convert parameters dict into JSON string
    if parameters is None:
        return {}
    # we will go through each key and make sure it is a string
    # if not we will do json.dumps on it
    for key, value in parameters.items():
        if not isinstance(value, str):
            parameters[key] = json.dumps(value)
    return parameters
