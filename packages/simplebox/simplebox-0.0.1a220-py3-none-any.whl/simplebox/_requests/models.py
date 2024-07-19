#!/usr/bin/env python
# -*- coding:utf-8 -*-
from requests.structures import CaseInsensitiveDict

from .utils import check_header_validity, to_native_string


def prepare_headers(self, headers):
    """Prepares the given HTTP headers."""

    self.headers = CaseInsensitiveDict()
    if headers:
        for header in headers.items():
            # Raise exception on invalid header value.
            check_header_validity(header)
            name, value = header
            self.headers[to_native_string(name)] = value
