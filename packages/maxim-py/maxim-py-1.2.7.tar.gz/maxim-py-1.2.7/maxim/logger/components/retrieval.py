from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ..writer import LogWriter
from .base import BaseContainer
from .types import Entity


@dataclass
class RetrievalConfig():
    id: str
    name: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


class Retrieval(BaseContainer):
    def __init__(self, config: RetrievalConfig, writer: LogWriter):
        super().__init__(Entity.RETRIEVAL, config.__dict__, writer)
        self._commit("create")

    def input(self, query: str):
        self._commit("update", {"input": query})
        self.end()

    @staticmethod
    def input_(writer: LogWriter, id: str, query: str):
        BaseContainer._commit_(writer, Entity.RETRIEVAL,
                               id, "update", {"input": query})

    def output(self, docs: Any):
        self._commit("output", {"docs": docs, "endTimestamp": datetime.now(timezone.utc)})
        self.end()

    @staticmethod
    def output_(writer: LogWriter, id: str, docs: Any):
        BaseContainer._commit_(writer, Entity.RETRIEVAL, id, "output", {
                               "docs": docs})
        BaseContainer._end_(writer, Entity.RETRIEVAL, id, {
                            "endTimestamp": datetime.now(timezone.utc)})

    @staticmethod
    def end_(writer: LogWriter, id: str, data: Optional[Dict[str, Any]] = None):
        if data is None:
            data = {}
        BaseContainer._end_(writer, Entity.RETRIEVAL, id, {
            "endTimestamp": datetime.now(timezone.utc),
            **data,
        })

    @staticmethod
    def add_tag_(writer: LogWriter, id: str, key: str, value: str):
        BaseContainer._add_tag_(writer, Entity.RETRIEVAL, id, key, value)
