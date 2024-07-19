import os
from mlflow.tracking.request_header.abstract_request_header_provider import (
    RequestHeaderProvider,
)


class CloudflareRequestHeaderProvider(RequestHeaderProvider):
    """RequestHeaderProvider provided through plugin system"""

    def in_context(self):
        return True

    def request_headers(self):
        request_headers = dict()
        request_headers["CF-Access-Client-Id"] = os.getenv("CF_ACCESS_CLIENT_ID")
        request_headers["CF-Access-Client-Secret"] = os.getenv("CF_ACCESS_CLIENT_SECRET")
        return request_headers
