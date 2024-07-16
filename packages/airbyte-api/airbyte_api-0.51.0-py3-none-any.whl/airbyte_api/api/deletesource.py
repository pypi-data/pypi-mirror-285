"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http


@dataclasses.dataclass
class DeleteSourceRequest:
    source_id: str = dataclasses.field(metadata={'path_param': { 'field_name': 'sourceId', 'style': 'simple', 'explode': False }})
    



@dataclasses.dataclass
class DeleteSourceResponse:
    content_type: str = dataclasses.field()
    r"""HTTP response content type for this operation"""
    status_code: int = dataclasses.field()
    r"""HTTP response status code for this operation"""
    raw_response: requests_http.Response = dataclasses.field()
    r"""Raw HTTP response; suitable for custom response parsing"""
    

