#!/usr/bin/env python
# -*- coding:utf-8 -*-

from requests import PreparedRequest

from .._requests.models import prepare_headers

PreparedRequest.prepare_headers = prepare_headers

