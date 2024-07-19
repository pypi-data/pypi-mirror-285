import logging
import re
import time
from typing import Any, Dict, List, Union
from uuid import uuid4

from langchain_core.outputs import LLMResult

from ..components.generation import GenerationError

logger = logging.getLogger("MaximSDK")


def parse_langchain_provider(serialized: Dict[str, Any]):
    """ Parses langchain provider from serialized data
    Args:
        serialized: Dict[str, Any]: Serialized data to parse provider from
    Returns:
        str: Parsed provider
    """
    provider = serialized.get("name", "").lower()
    if provider.startswith("chat"):
        return provider.replace("chat", "")
    return provider


def parse_langchain_llm_error(error: Union[Exception, KeyboardInterrupt]) -> GenerationError:
    """ Parses langchain LLM error into a format that is accepted by Maxim logger
    Args:
        error: Union[Exception, KeyboardInterrupt]: Error to be parsed
    Returns:
        GenerationError: Parsed LLM error
    """
    if isinstance(error, KeyboardInterrupt):
        return GenerationError(message="Generation was interrupted by the user")
    else:
        message = error.__dict__.get("message", "")
        type = error.__dict__.get("type", None)
        code = error.__dict__.get("code", None)
        return GenerationError(message=message, type=type, code=code)


def parse_langchain_model_parameters(**kwargs: Any):
    """ Parses langchain kwargs into model and model parameters. You can use this function with any langchain _start callback function
    Args:
        kwargs: Dict[str, Any]: Kwargs to be parsed
    Returns:
        Tuple[str, Dict[str, Any]]: Model and model parameters
    Raises:
        Exception: If model_name is not found in kwargs
    """
    model_parameters = kwargs.get("invocation_params", {})
    model = model_parameters.get("model_name", "")
    del model_parameters["model_name"]
    return model, model_parameters


def parse_langchain_llm_result(result: LLMResult):
    """ Parses langchain LLM result into a format that is accepted by Maxim logger
    Args:
        result: LLMResult: LLM result to be parsed
    Returns:
        Dict[str, Any]: Parsed LLM result
    Raises:
        Exception: If error parsing LLM result
    """
    try:
        generations = result.generations
        choices = []
        if generations is not None:
            for gen_idx, generation in enumerate(generations):
                for idx, gen in enumerate(generation):
                    messages = parse_langchain_messages([gen.text], "system")
                    choices.append({
                        'index': gen_idx+idx,
                        'text': messages[0]['content'],
                        'logprobs': gen.generation_info.get("logprobs") if gen.generation_info else None,
                        'finish_reason': gen.generation_info.get("finish_reason") if gen.generation_info else None
                    })
        usage = result.llm_output.get(
            "token_usage") if result.llm_output else None
        return {
            'id': str(uuid4()),
            'created': int(time.time()),
            'choices': choices,
            'usage': usage
        }
    except Exception as e:
        logger.error(f"Error parsing LLM result: {e}")
        raise Exception(f"Error parsing LLM result: {e}")


def parse_langchain_messages(input: Union[List[str], List[List[Any]]], default_role="user"):
    """ Parses langchain messages into messages that are accepted by Maxim logger
    Args:
        input: List[str] or List[List[Any]]: List of messages to be parsed
        default_role: str: Default role to assign to messages without a role
    Returns:
        List[Dict[str, str]]: List of messages with role and content
    Raises:
        Exception: If input is not List[str] or List[List[Any]]
        Exception: If message type is not str or list
        Exception: If message type is not recognized
    """
    try:
        delimiter_to_role = {
            "System": "system",
            "Human": "user",
            "User": "user",
            "Assistant": "assistant",
            "Model": "model",
        }
        messages = []
        # checking if input is List[str] or List[List]

        if isinstance(input[0], list):
            for message_list in input or []:
                for message in message_list:
                    if isinstance(message, str):
                        continue
                    message_type = type(message).__name__
                    if message_type.endswith("SystemMessage"):
                        messages.append(
                            {"role": "system", "content": message.content or ""})
                    elif message_type.endswith("HumanMessage"):
                        messages.append(
                            {"role": "user", "content": message.content or ""})
                    else:
                        logger.error(
                            f"Invalid message type: {type(message)}")
                        raise Exception(
                            f"Invalid message type: {type(message)}")
        else:
            for message in input or []:
                if not isinstance(message, str):
                    logger.error(f"Invalid message type: {type(message)}")
                    raise Exception(
                        f"Invalid message type: {type(message)}")
                # get type of message
                # Define the delimiter pattern
                pattern = r'(System:|Human:|User:|Assistant:|Model:)'
                # Split the text using the pattern
                splits = re.split(pattern, message)
                # Remove any leading/trailing whitespace and empty strings
                splits = [s.strip() for s in splits if s.strip()]
                # Pair up the delimiters with their content
                for i in range(0, len(splits), 2):
                    if i + 1 < len(splits):
                        # Remove ":" from delimiter and trim both delimiter and content
                        delimiter = splits[i].rstrip(':').strip()
                        content = splits[i+1].strip()
                        messages.append({"role": delimiter_to_role.get(
                            delimiter, "user"), "content": content})
                    else:
                        if splits[i].find(":") == -1:
                            messages.append({"role": delimiter_to_role.get(
                                default_role, "user"), "content": splits[i]})
                        else:
                            # Handle case where there's a delimiter without content
                            delimiter = splits[i].rstrip(':').strip()
                            messages.append({"role": delimiter_to_role.get(
                                delimiter, "user"), "content": ""})
        return messages
    except Exception as e:
        logger.error(f"Error parsing messages: {e}")
        raise Exception(f"Error parsing messages: {e}")
