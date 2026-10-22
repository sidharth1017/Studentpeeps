import json
import logging
import queue
import threading
from typing import Any
import requests

from django.conf import settings

from .formatters import DatadogJsonFormatter


class DatadogHTTPHandler(logging.Handler):
    """
    Ships JSON logs to Datadog Log HTTP intake when DD_API_KEY is configured.
    Uses a background thread so outbound API logging never blocks request paths.
    """

    def __init__(self):
        super().__init__()
        self.setFormatter(DatadogJsonFormatter())
        self._queue: queue.Queue[str | None] = queue.Queue(maxsize=10_000)
        self._worker = threading.Thread(target=self._run, name="datadog-log-shipper", daemon=True)
        self._worker.start()

    def emit(self, record: logging.LogRecord) -> None:
        if not getattr(settings, "DD_API_KEY", ""):
            return
        try:
            line = self.format(record)
            self._queue.put_nowait(line)
        except queue.Full:
            pass
        except Exception:
            self.handleError(record)

    def _run(self) -> None:
        session = requests.Session()
        url = getattr(settings, "DD_LOGS_INTAKE_URL", "")
        api_key = getattr(settings, "DD_API_KEY", "")
        if not url or not api_key:
            return

        batch: list[dict[str, Any]] = []
        while True:
            line = self._queue.get()
            if line is None:
                break
            try:
                batch.append(json.loads(line))
            except json.JSONDecodeError:
                continue

            if len(batch) >= 25:
                self._flush(session, url, api_key, batch)
                batch = []

        if batch:
            self._flush(session, url, api_key, batch)

    def _flush(
        self,
        session: requests.Session,
        url: str,
        api_key: str,
        batch: list[dict[str, Any]],
    ) -> None:
        try:
            session.post(
                url,
                headers={
                    "DD-API-KEY": api_key,
                    "Content-Type": "application/json",
                },
                json=batch,
                timeout=5,
            )
        except Exception:
            pass

    def close(self) -> None:
        try:
            self._queue.put_nowait(None)
        except queue.Full:
            pass
        super().close()


def build_root_handlers() -> list[logging.Handler]:
    console = logging.StreamHandler()
    console.setFormatter(DatadogJsonFormatter())
    handlers: list[logging.Handler] = [console]

    if getattr(settings, "DD_API_KEY", ""):
        handlers.append(DatadogHTTPHandler())

    return handlers
