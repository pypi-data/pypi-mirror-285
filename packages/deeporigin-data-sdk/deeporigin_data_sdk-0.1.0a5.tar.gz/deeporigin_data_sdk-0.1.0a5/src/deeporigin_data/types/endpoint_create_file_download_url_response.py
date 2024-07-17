# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["EndpointCreateFileDownloadURLResponse", "Data"]


class Data(BaseModel):
    download_url: str = FieldInfo(alias="downloadUrl")


class EndpointCreateFileDownloadURLResponse(BaseModel):
    data: Data
