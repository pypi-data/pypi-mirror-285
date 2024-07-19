# Assuming similar components exist in Python with the same functionality
import logging
from typing import Any, Dict, Optional

from ..logger.components.session import Session, SessionConfig
from ..logger.components.trace import Trace, TraceConfig
from .components.feedback import Feedback
from .components.generation import (Generation, GenerationConfig,
                                    GenerationError)
from .components.retrieval import Retrieval, RetrievalConfig
from .components.span import Span, SpanConfig
from .writer import LogWriter, LogWriterConfig


class LoggerConfig:
    def __init__(self, id, auto_flush=True, flush_interval=10):
        self.id = id
        self.auto_flush = auto_flush
        self.flush_interval = flush_interval


logger = logging.getLogger("MaximSDK")


class Logger:

    def __init__(self, config: LoggerConfig, api_key, base_url, is_debug=False):
        logger.setLevel(logging.DEBUG if is_debug else logging.INFO)
        if not config.id:
            raise ValueError(
                "Logger must be initialized with id of the logger")
        self._id = config.id
        self.is_debug = is_debug
        writer_config = LogWriterConfig(auto_flush=config.auto_flush,
                                        flush_interval=config.flush_interval,
                                        base_url=base_url,
                                        api_key=api_key,
                                        is_debug=is_debug,
                                        repository_id=config.id)
        self.writer = LogWriter(writer_config)
        logger.debug(f"Logger initialized")

    def session(self, config: SessionConfig) -> Session:
        return Session(config, self.writer)

    def trace(self, config: TraceConfig) -> Trace:
        return Trace(config, self.writer)

    # Session methods
    def session_add_tag(self, session_id: str, key: str, value: str):
        Session.add_tag_(self.writer, session_id, key, value)

    def session_end(self, session_id: str):
        Session.end_(self.writer, session_id)

    def session_event(self, session_id: str, event_id: str, event: str, data: Any):
        Session.event_(self.writer, session_id, event_id, event, data)

    def session_feedback(self, session_id: str, feedback: Feedback):
        Session.feedback_(self.writer, session_id, feedback)

    def session_trace(self, session_id: str, config: TraceConfig) -> Trace:
        return Session.trace_(self.writer, session_id, config)

    # Trace methods
    def trace_generation(self, trace_id: str, config: GenerationConfig) -> Generation:
        return Trace.generation_(self.writer, trace_id, config)

    def trace_retrieval(self, trace_id: str, config: RetrievalConfig) -> Retrieval:
        return Trace.retrieval_(self.writer, trace_id, config)

    def trace_span(self, trace_id: str, config: SpanConfig) -> Span:
        return Trace.span_(self.writer, trace_id, config)

    def trace_add_tag(self, trace_id: str, key: str, value: str):
        Trace.add_tag_(self.writer, trace_id, key, value)

    def trace_event(self, trace_id: str, event_id: str, event: str, tags: Optional[Dict[str, str]] = None):
        Trace.event_(self.writer, trace_id, event_id, event, tags)

    def trace_set_input(self, trace_id: str, input: str):
        Trace.set_input_(self.writer, trace_id, input)

    def trace_set_output(self, trace_id: str, output: str):
        Trace.set_output_(self.writer, trace_id, output)

    def trace_feedback(self, trace_id: str, feedback: Feedback):
        Trace.feedback_(self.writer, trace_id, feedback)

    def trace_end(self, trace_id: str):
        Trace.end_(self.writer, trace_id)

    # Generation methods
    def generation_set_model(self, generation_id: str, model: str):
        Generation.set_model_(self.writer, generation_id, model)

    def generation_add_message(self, generation_id: str, message: Any):
        Generation.add_message_(self.writer, generation_id, message)

    def generation_set_model_parameters(self, generation_id: str, model_parameters: dict):
        Generation.set_model_parameters_(
            self.writer, generation_id, model_parameters)

    def generation_result(self, generation_id: str, result: Any):
        Generation.result_(self.writer, generation_id, result)

    def generation_end(self, generation_id: str):
        Generation.end_(self.writer, generation_id)

    def generation_error(self, generation_id: str, error: GenerationError):
        Generation.error_(self.writer, generation_id, error)

    # Span methods
    def span_generation(self, span_id: str, config: GenerationConfig) -> Generation:
        return Span.generation_(self.writer, span_id, config)

    def span_retrieval(self, span_id: str, config: RetrievalConfig):
        return Span.retrieval_(self.writer, span_id, config)

    def span_end(self, span_id: str):
        Span.end_(self.writer, span_id)

    def span_add_tag(self, span_id: str, key: str, value: str):
        Span.add_tag_(self.writer, span_id, key, value)

    def span_event(self, span_id: str, event_id: str, name: str, tags: Optional[Dict[str, str]] = None):
        Span.event_(self.writer, span_id, event_id, name, tags)

    def span_span(self, span_id: str, config: SpanConfig):
        return Span.span_(self.writer, span_id, config)

    # Retrieval methods
    def retrieval_end(self, retrieval_id: str):
        Retrieval.end_(self.writer, retrieval_id)

    def retrieval_input(self, retrieval_id: str, query: Any):
        Retrieval.input_(self.writer, retrieval_id, query)

    def retrieval_output(self, retrieval_id: str, docs: Any):
        Retrieval.output_(self.writer, retrieval_id, docs)

    @property
    def id(self):
        return self._id

    def flush(self):
        self.writer.flush()

    def cleanup(self):
        self.writer.cleanup()
