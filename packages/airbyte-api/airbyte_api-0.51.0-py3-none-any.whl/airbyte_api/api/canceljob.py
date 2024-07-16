"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ..models import jobresponse as models_jobresponse
from typing import Optional


@dataclasses.dataclass
class CancelJobRequest:
    job_id: int = dataclasses.field(metadata={'path_param': { 'field_name': 'jobId', 'style': 'simple', 'explode': False }})
    



@dataclasses.dataclass
class CancelJobResponse:
    content_type: str = dataclasses.field()
    r"""HTTP response content type for this operation"""
    status_code: int = dataclasses.field()
    r"""HTTP response status code for this operation"""
    raw_response: requests_http.Response = dataclasses.field()
    r"""Raw HTTP response; suitable for custom response parsing"""
    job_response: Optional[models_jobresponse.JobResponse] = dataclasses.field(default=None)
    r"""Cancel a Job."""
    

