import logging
import os
import tempfile
import threading
import time
import uuid
from datetime import datetime, timezone
from queue import Queue
from typing import Optional, Union

from ..apis.maxim import MaximAPI

maximLogger = logging.getLogger("MaximSDK")


class LogWriterConfig:
    def __init__(self, base_url, api_key, repository_id, auto_flush=True, flush_interval: Optional[int] = 10, is_debug=False):
        self.base_url = base_url
        self.api_key = api_key
        self.repository_id = repository_id
        self.auto_flush = auto_flush
        self.flush_interval = flush_interval
        self.is_debug = is_debug
        maximLogger.setLevel(logging.DEBUG if is_debug else logging.INFO)


class LogWriter:
    def __init__(self, config: LogWriterConfig):
        self.is_running = True
        self.id = str(uuid.uuid4())
        self.config = config
        self.queue = Queue()
        self.mutex = threading.Lock()
        self.is_debug = config.is_debug
        self.logs_dir = os.path.join(
            tempfile.gettempdir(), f"maxim-sdk/{self.id}/maxim-logs")
        self.__flush_thread = None
        os.makedirs(self.logs_dir, exist_ok=True)
        if self.config.auto_flush:
            if self.config.flush_interval:
                maximLogger.debug(
                    f"Starting flush thread with interval {self.config.flush_interval} seconds")
                self.__flush_thread = threading.Timer(
                    int(self.config.flush_interval), self.flush)
                self.__flush_thread.start()
            else:
                raise ValueError(
                    "flush_interval is set to None.flush_interval has to be a number")

    def write_to_file(self, logs):
        filename = f"logs-{time.strftime('%Y-%m-%dT%H:%M:%SZ')}.log"
        filepath = os.path.join(self.logs_dir, filename)
        maximLogger.debug(f"Writing logs to file: {filename}")
        with open(filepath, 'w') as file:
            for log in logs:
                file.write(log.serialize() + "\n")
        return filepath

    def flush_log_files(self):
        if os.path.exists(self.logs_dir) == False:
            return
        files = os.listdir(self.logs_dir)
        for file in files:
            with open(os.path.join(self.logs_dir, file), 'r') as f:
                logs = f.read()
            try:
                MaximAPI.pushLogs(
                    self.config.base_url, self.config.api_key, self.config.repository_id, logs)
                os.remove(os.path.join(self.logs_dir, file))
            except Exception as e:
                if self.is_debug:
                    raise Exception(e)

    def flush_logs(self, logs):
        try:
            # Pushing old logs first
            self.flush_log_files()
            # Pushing new logs

            logs_to_push = "\n".join(
                [log.serialize() for log in logs])
            MaximAPI.pushLogs(self.config.base_url, self.config.api_key,
                              self.config.repository_id, logs_to_push)
        except Exception as e:
            self.write_to_file(logs)
            maximLogger.error(
                f"Failed to push logs to server. Writing logs to file. Error: {e}")

    def commit(self, log):
        self.queue.put(log)

    def flush(self):
        if self.is_running == False:
            return
        with self.mutex:
            # Scheduling next call
            if self.config.flush_interval:
                self.__flush_thread = threading.Timer(
                    int(self.config.flush_interval), self.flush)
                self.__flush_thread.start()
            items = []
            while not self.queue.empty():
                items.append(self.queue.get())
            if len(items) == 0:
                maximLogger.debug("No logs to flush")
                return
            maximLogger.debug(
                f"Flushing logs to server {time.strftime('%Y-%m-%dT%H:%M:%S')}")
            if self.is_debug:
                for item in items:
                    maximLogger.debug(f"{item.serialize()}")
        self.flush_logs(items)
        maximLogger.debug("Flush complete")

    def cleanup(self):
        self.flush()
        self.is_running = False
        if self.__flush_thread:
            self.__flush_thread.cancel()
            self.__flush_thread = None
