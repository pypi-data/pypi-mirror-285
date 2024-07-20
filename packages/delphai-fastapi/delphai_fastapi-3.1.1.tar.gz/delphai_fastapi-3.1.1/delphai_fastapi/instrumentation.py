import os

from fastapi import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    generate_latest,
    multiprocess,
)
from prometheus_fastapi_instrumentator import Instrumentator

from .auth import Authorization


METRICS_URL = "/metrics"


def instrument(app, options):
    if isinstance(options, bool) and not options:
        # Disabled when `options == False`
        return None

    options = {
        "should_group_status_codes": False,
        "excluded_handlers": [METRICS_URL],
        "should_instrument_requests_inprogress": True,
        "inprogress_labels": True,
        **(options or {}),
    }

    instrumentator = Instrumentator(**options).instrument(app)

    @app.get(METRICS_URL, include_in_schema=False)
    def metrics(authorization=Authorization) -> Response:
        """Endpoint that serves Prometheus metrics."""

        authorization.require(authorization.is_direct_request)

        registry = instrumentator.registry
        if "PROMETHEUS_MULTIPROC_DIR" in os.environ:
            registry = CollectorRegistry()
            multiprocess.MultiProcessCollector(registry)

        return Response(
            headers={"Content-Type": CONTENT_TYPE_LATEST},
            content=generate_latest(registry),
        )

    return instrumentator
