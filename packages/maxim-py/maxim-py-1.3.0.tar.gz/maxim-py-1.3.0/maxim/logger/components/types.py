import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class Entity(Enum):
    SESSION = "session"
    TRACE = "trace"
    SPAN = "span"
    GENERATION = "generation"
    FEEDBACK = "feedback"
    RETRIEVAL = "retrieval"


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class CommitLog:
    def __init__(self, entity: Entity, entity_id: str, action: str, data: Optional[Dict[str, Any]] = None):
        self.entity = entity
        self.entity_id = entity_id
        self.action = action
        self.data = data

    def serialize(self, custom_data: Optional[Dict[str,Any]] = None) -> str:
        if custom_data is not None:
            if self.data is None:
                self.data = {}
            self.data.update(custom_data)
        return f"{self.entity.value}{{id={self.entity_id},action={self.action},data={json.dumps(self.data,cls=DateTimeEncoder)}}}"
