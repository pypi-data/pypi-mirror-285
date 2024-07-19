from dataclasses import field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..parsers.tags_parser import parse_tags
from ..writer import LogWriter
from .types import CommitLog, Entity


class ContainerLister:
    def on_end(self):
        pass


BaseConfig = Dict[str, Any]


class BaseContainer:

    def __init__(self, entity: Entity, config: BaseConfig, writer: LogWriter):
        self.entity = entity
        self._id = config['id']
        self._name = config.get('name')
        self.span_id = config.get('span_id')
        self.start_timestamp = datetime.now(timezone.utc)
        self.end_timestamp = None
        self.tags = parse_tags(config.get('tags', {}))
        self.writer = writer

    @property
    def id(self) -> str:
        return self._id

    def add_tag(self, key: str, value: str):
        if self.tags == None:
            self.tags = {}
        # Validate if value is str and not None
        self.tags[key] = value
        self.tags = parse_tags(self.tags)
        self._commit("update", {"tags": {key: value}})

    @staticmethod
    def _add_tag_(writer: LogWriter, entity: Entity, id: str, key: str, value: str):
        writer.commit(CommitLog(entity, id, "update", {"tags": {key: value}}))

    def end(self):
        self.end_timestamp = datetime.now(timezone.utc)
        self._commit("end", {"endTimestamp": self.end_timestamp})

    @staticmethod
    def _end_(writer: LogWriter, entity: Entity, id: str, data: Optional[Dict[str, Any]] = None):
        if data is None:
            data = {}
        data = {k: v for k, v in data.items() if v is not None}
        writer.commit(CommitLog(entity, id, "end", data))

    def data(self) -> Dict[str, Any]:
        data = {
            "name": self._name,
            "spanId": self.span_id,
            "tags": self.tags,
            "startTimestamp": self.start_timestamp,
            "endTimestamp": self.end_timestamp,
        }
        # removing none values
        data = {k: v for k, v in data.items() if v is not None}
        return data

    @staticmethod
    def _commit_(writer: LogWriter, entity: Entity, id: str, action: str, data: Optional[Dict[str, Any]] = None):
        # Removing all null values from data dict
        if data is not None:
            data = {k: v for k, v in data.items() if v is not None}
        writer.commit(CommitLog(entity, id, action, data))

    def _commit(self, action: str, data: Optional[Dict[str, Any]] = None):
        if data is None:
            data = self.data()
        # Removing all null values from data dict
        data = {k: v for k, v in data.items() if v is not None}
        self.writer.commit(CommitLog(self.entity, self._id,
                           action, data))


class EventEmittingBaseContainer(BaseContainer):

    @staticmethod
    def _event_(writer: LogWriter, entity: Entity, entity_id: str, id: str, name: str, tags: Optional[Dict[str, str]] = None):
        BaseContainer._commit_(writer, entity, entity_id, "add-event", {
            "id": id, "name": name, "timestamp": datetime.now(timezone.utc), "tags": tags})

    def event(self, id: str, name: str, tags: Optional[Dict[str, str]] = None):
        self._commit("add-event", {"id": id, "name": name,
                                   "timestamp": datetime.now(timezone.utc), "tags": tags})
