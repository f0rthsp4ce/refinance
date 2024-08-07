"""DTO for Token"""

from app.schemas.base import BaseSchema


class TokenSendReportSchema(BaseSchema):
    entity_found: bool
    token_generated: bool
    message_sent: bool
