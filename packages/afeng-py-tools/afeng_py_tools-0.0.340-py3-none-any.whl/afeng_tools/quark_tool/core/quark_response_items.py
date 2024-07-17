from typing import Optional

from pydantic import BaseModel

from afeng_tools.quark_tool.core.quark_items import ShareToken, PageMetadata, ShareData


class QuarkResponse(BaseModel):
    # ok：200
    status: Optional[int] = None
    # 0
    code: Optional[int] = None
    # ok
    message: Optional[str] = None
    timestamp: Optional[int] = None


class ShareTokenResponse(QuarkResponse):
    data: Optional[ShareToken] = None


class ShareDataResponse(QuarkResponse):
    metadata: Optional[PageMetadata] = None
    data: Optional[ShareData] = None
