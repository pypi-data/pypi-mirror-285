# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from .._models import BaseModel
from .seq_data import SeqData

__all__ = ["BaseSequenceParseResponse"]


class BaseSequenceParseResponse(BaseModel):
    data: SeqData
