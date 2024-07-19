# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

from __future__ import annotations

import typing as t

import requests


def fetch(
    request: str,
    token: str | None = None,
    **kwargs: t.Any,
) -> requests.Response:
    """Fetch a network resource as a context manager."""
    method = kwargs.pop("method", "GET")
    f = getattr(requests, method.lower())
    headers = kwargs.pop("headers", {})
    if len(headers) == 0:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Jupyter kernels CLI",
        }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if "timeout" not in kwargs:
        kwargs["timeout"] = 60
    response = f(request, headers=headers, **kwargs)
    response.raise_for_status()
    return response
