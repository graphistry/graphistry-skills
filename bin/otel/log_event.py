#!/usr/bin/env python3
"""Emit a single OTel log record to the OTLP collector."""
from __future__ import annotations

import argparse
import logging
import os

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit a single OTel log record.")
    parser.add_argument("message", help="Log message")
    parser.add_argument("--level", default="info", help="Log level (info, warning, error)")
    parser.add_argument("--service", default=None, help="Service name (default: BOTS_OTEL_SERVICE_NAME or OTEL_SERVICE_NAME)")
    parser.add_argument("--endpoint", default=None, help="OTLP gRPC endpoint (default: OTEL_EXPORTER_OTLP_ENDPOINT_GRPC)")
    parser.add_argument("--attr", action="append", default=[], help="Key=Value attribute (repeatable)")
    args = parser.parse_args()

    service_name = (
        args.service
        or os.environ.get("BOTS_OTEL_SERVICE_NAME")
        or os.environ.get("OTEL_SERVICE_NAME")
        or "bots-runner"
    )
    endpoint = args.endpoint or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT_GRPC", "http://localhost:4317")
    endpoint = endpoint.replace("http://", "").replace("https://", "")

    resource = Resource.create({"service.name": service_name})
    provider = LoggerProvider(resource=resource)
    provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter(endpoint=endpoint, insecure=True)))
    set_logger_provider(provider)

    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)
    logger.addHandler(LoggingHandler(level=logging.NOTSET, logger_provider=provider))

    attrs = {k: v for k, _, v in (item.partition("=") for item in args.attr)}
    level = getattr(logging, args.level.upper(), logging.INFO)
    attr_pairs = " ".join(f"{key}={value}" for key, value in attrs.items())
    message = f"{args.message} {attr_pairs}".strip()
    logger.log(level, message, extra=attrs)
    provider.shutdown()


if __name__ == "__main__":
    main()
