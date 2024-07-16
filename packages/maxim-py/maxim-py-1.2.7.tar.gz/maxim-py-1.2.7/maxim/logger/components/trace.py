from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict, Optional

from ..writer import LogWriter
from .base import EventEmittingBaseContainer
from .feedback import Feedback
from .generation import Generation, GenerationConfig
from .retrieval import Retrieval, RetrievalConfig
from .types import Entity

if TYPE_CHECKING:
    from .span import Span, SpanConfig  # Type checking only


@dataclass
class TraceConfig:
    id: str
    name: Optional[str] = None
    session_id: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    input: Optional[str] = None


class Trace(EventEmittingBaseContainer):
    def __init__(self, config: TraceConfig, writer: LogWriter):
        super().__init__(Entity.TRACE, config.__dict__, writer)
        payload_to_send = {
            **self.data(),
            "sessionId": config.session_id,            
        }
        if config.input is not None :
            payload_to_send["input"] = config.input 
        self._commit("create", payload_to_send)

    def set_input(self, input: str):
        self._commit("update", {"input": input})
        
    @staticmethod
    def set_input_(writer: LogWriter, trace_id: str, input: str):
        Trace._commit_(writer, Entity.TRACE, trace_id, "update", {"input": input})
        
    def set_output(self, output: str):
        self._commit("update", {"output": output})
    
    @staticmethod
    def set_output_(writer: LogWriter, trace_id: str, output: str):
        Trace._commit_(writer, Entity.TRACE, trace_id, "update", {"output": output})

    def generation(self, config: GenerationConfig) -> Generation:
        generation = Generation(config, self.writer)
        self._commit("add-generation", {
            **generation.data(),
            "id": generation.id,
        })
        return generation

    @staticmethod
    def generation_(writer: LogWriter, trace_id: str, config: GenerationConfig) -> Generation:
        generation = Generation(config, writer)
        Trace._commit_(writer, Entity.TRACE, trace_id, "add-generation", {
            **generation.data(),
            "id": generation.id,
        })
        return generation

    def retrieval(self, config: RetrievalConfig):
        retrieval = Retrieval(config, self.writer)
        self._commit("add-retrieval", {
            "id": config.id,
            **retrieval.data(),
        })
        return retrieval

    @staticmethod
    def retrieval_(writer: LogWriter, trace_id: str, config: RetrievalConfig):
        retrieval = Retrieval(config, writer)
        Trace._commit_(writer, Entity.TRACE, trace_id, "add-retrieval", {
            "id": config.id,
            **retrieval.data(),
        })
        return retrieval

    def span(self, config: 'SpanConfig') -> 'Span':
        from .span import Span, SpanConfig
        span = Span(config, self.writer)
        self._commit("add-span", {
            "id": config.id,
            **span.data(),
        })
        return span

    @staticmethod
    def span_(writer: LogWriter, trace_id: str, config: 'SpanConfig') -> 'Span':
        from .span import Span, SpanConfig
        span = Span(config, writer)
        Trace._commit_(writer, Entity.TRACE, trace_id, "add-span", {
            "id": config.id,
            **span.data(),
        })

        return span

    def feedback(self, feedback: Feedback):
        self._commit("add-feedback", feedback.__dict__)

    @staticmethod
    def feedback_(writer: LogWriter, trace_id: str, feedback: Feedback):
        Trace._commit_(writer, Entity.TRACE, trace_id,
                       "add-feedback", feedback.__dict__)

    @staticmethod
    def add_tag_(writer: LogWriter, id: str, key: str, value: str):
        EventEmittingBaseContainer._add_tag_(
            writer, Entity.TRACE, id, key, value)

    @staticmethod
    def end_(writer: LogWriter, trace_id: str, data: Optional[Dict[str, str]] = None):
        if data is None:
            data = {}
        return EventEmittingBaseContainer._end_(writer, Entity.TRACE, trace_id, {
            "endTimestamp": datetime.now(timezone.utc),
            **data,
        })

    @staticmethod
    def event_(writer: LogWriter, trace_id: str, id: str, event: str, tags: Optional[Dict[str, str]] = None):
        return EventEmittingBaseContainer._event_(writer, Entity.TRACE, trace_id, id, event, tags)
