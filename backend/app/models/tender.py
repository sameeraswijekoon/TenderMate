from pydantic import BaseModel, Field
from typing import Optional

class TenderField(BaseModel):
    value: Optional[str] = None
    page: Optional[int] = None
    confidence: float = Field(default=0.0, ge=0, le=1)

class TenderSummary(BaseModel):
    tender_title: TenderField = TenderField()
    reference_number: TenderField = TenderField()
    closing_date: TenderField = TenderField()
    closing_time: TenderField = TenderField()
    pre_bid_date: TenderField = TenderField()
    pre_bid_time: TenderField = TenderField()
    pre_bid_location: TenderField = TenderField()
    submission_location: TenderField = TenderField()
    delivery_period: TenderField = TenderField()
    bid_validity: TenderField = TenderField()
    quantity: TenderField = TenderField()
    warranty: TenderField = TenderField()
    bid_security: TenderField = TenderField()
    performance_security: TenderField = TenderField()
    required_documents: TenderField = TenderField()
