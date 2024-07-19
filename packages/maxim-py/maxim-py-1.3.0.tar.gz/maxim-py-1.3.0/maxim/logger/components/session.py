from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ..writer import LogWriter
from .base import EventEmittingBaseContainer
from .feedback import Feedback
from .trace import Trace, TraceConfig
from .types import Entity


@dataclass
class SessionConfig:
    id: str
    name: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


class Session(EventEmittingBaseContainer):
    ENTITY = Entity.SESSION

    def __init__(self, config: SessionConfig, writer: LogWriter):
        super().__init__(Session.ENTITY, config.__dict__, writer)
        self._commit("create")

    def trace(self, config: TraceConfig) -> Trace:
        # Assuming TraceConfig in Python has a session_id attribute
        config.session_id = self.id
        return Trace(config, self.writer)

    @staticmethod
    def trace_(writer: LogWriter, session_id: str, config: TraceConfig) -> Trace:
        config.session_id = session_id
        return Trace(config, writer)

    def feedback(self, feedback: Feedback):
        self._commit("add-feedback", feedback.__dict__)

    @staticmethod
    def feedback_(writer: LogWriter, session_id: str, feedback: Feedback):
        EventEmittingBaseContainer._commit_(writer,
                                            Entity.SESSION, session_id, "add-feedback", feedback.__dict__)

    @staticmethod
    def add_tag_(writer: LogWriter, session_id: str, key: str, value: str):
        return EventEmittingBaseContainer._add_tag_(writer, Entity.SESSION, session_id, key, value)

    @staticmethod
    def end_(writer: LogWriter, session_id: str, data: Optional[Dict[str, Any]] = None):
        if data is None:
            data = {}
        return EventEmittingBaseContainer._end_(writer, Entity.SESSION, session_id, {
            "endTimestamp": datetime.now(timezone.utc),
            **data,
        })

    @staticmethod
    def event_(writer: LogWriter, session_id: str, id: str, event: str, data: Dict[str, str]):
        return EventEmittingBaseContainer._event_(writer, Entity.SESSION, session_id, id, event, data)
