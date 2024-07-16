import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..parsers.generation_parser import parse_model_parameters, parse_result
from ..writer import LogWriter
from .base import BaseContainer
from .types import Entity


@dataclass
class GenerationError:
    message: str
    code: Optional[str] = None
    type: Optional[str] = None


logger = logging.getLogger("MaximSDK")


@dataclass
class GenerationConfig:
    id: str
    provider: str
    model: str
    messages: Optional[List[Any]] = field(default_factory=list)
    model_parameters: Dict[str, Any] = field(default_factory=dict)
    span_id: Optional[str] = None
    name: Optional[str] = None
    maxim_prompt_id: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


class Generation(BaseContainer):
    def __init__(self, config: GenerationConfig, writer: LogWriter):
        super().__init__(Entity.GENERATION, config.__dict__, writer)
        self.model = config.model
        self.maxim_prompt_id = config.maxim_prompt_id
        self.messages = []
        self.provider = config.provider
        if config.messages is not None:
            self.messages.extend(config.messages)
        self.model_parameters = parse_model_parameters(config.model_parameters)

    @staticmethod
    def set_model_(writer: LogWriter, id: str, model: str):
        BaseContainer._commit_(writer, Entity.GENERATION,
                               id, "update", {"model": model})

    def set_model(self, model: str):
        self.model = model
        self._commit("update", {"model": model})

    @staticmethod
    def add_message_(writer: LogWriter, id: str, message: Any):
        BaseContainer._commit_(writer, Entity.GENERATION, id, "update", {
            "messages": [message]})

    def add_message(self, message: Any):
        self.messages.append(message)
        self._commit("update", {"messages": [message]})

    @staticmethod
    def set_model_parameters_(writer: LogWriter, id: str, model_parameters: Dict[str, Any]):
        BaseContainer._commit_(writer, Entity.GENERATION, id, "update", {
            "model_parameters": model_parameters})

    def set_model_parameters(self, model_parameters: Dict[str, Any]):
        self.model_parameters = model_parameters
        self._commit("update", {"model_parameters": model_parameters})

    @staticmethod
    def result_(writer: LogWriter, id: str, result: Any):
        try:
            result = parse_result(result)
            BaseContainer._commit_(writer,
                                   Entity.GENERATION, id, "result", {"result": result})
            BaseContainer._end_(writer, Entity.GENERATION, id, {
                "endTimestamp": datetime.now(timezone.utc),
            })
        except ValueError as e:
            logger.error(
                "Invalid result. We expect OpenAI response format: {e}")
            raise ValueError(
                f"Invalid result. We expect OpenAI response format: {e}")

    @staticmethod
    def end_(writer: LogWriter, id: str, data: Optional[Dict[str, Any]] = None):
        if data is None:
            data = {}
        BaseContainer._end_(writer, Entity.GENERATION, id, {
            "endTimestamp": datetime.now(timezone.utc),
            **data,
        })

    @staticmethod
    def add_tag_(writer: LogWriter, id: str, key: str, value: str):
        BaseContainer._add_tag_(writer, Entity.GENERATION, id, key, value)

    def result(self, result: Any):
        try:
            parse_result(result)
            self._commit("result", {"result": result})
            self.end()
        except ValueError as e:
            logger.error(
                "Invalid result. We expect OpenAI response format: {e}")
            raise ValueError(
                f"Invalid result. We expect OpenAI response format: {e}")

    def error(self, error: GenerationError):
        if not error.code:
            error.code = ""
        if not error.type:
            error.type = ""
        self._commit("result", {"result": {"error": {
            "message": error.message,
            "code": error.code,
            "type": error.type,
        }, "id": str(uuid4())}})
        self.end()

    @staticmethod
    def error_(writer: LogWriter, id: str, error: GenerationError):
        if not error.code:
            error.code = ""
        if not error.type:
            error.type = ""
        BaseContainer._commit_(writer, Entity.GENERATION,
                               id, "result", {"result": {"error": {
                                   "message": error.message,
                                   "code": error.code,
                                   "type": error.type,
                               }, "id": str(uuid4())}})
        BaseContainer._end_(writer, Entity.GENERATION, id, {
            "endTimestamp": datetime.now(timezone.utc),
        })

    def data(self) -> Dict[str, Any]:
        base_data = super().data()
        return {
            **base_data,
            "model": self.model,
            "provider": self.provider,
            "maximPromptId": self.maxim_prompt_id,
            "messages": self.messages,
            "modelParameters": self.model_parameters,
        }
