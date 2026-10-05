from pydantic import BaseModel, Field
from typing import Optional
class TenderField(BaseModel):
    value: Optional[str]=None; page: Optional[int]=None; confidence: float=Field(default=0.0,ge=0,le=1)
class Requirement(BaseModel):
    category:str; requirement:str; page:Optional[int]=None; confidence:float=0.0
class TenderSummary(BaseModel):
    tender_title:TenderField=Field(default_factory=TenderField); reference_number:TenderField=Field(default_factory=TenderField); closing_date:TenderField=Field(default_factory=TenderField); closing_time:TenderField=Field(default_factory=TenderField); pre_bid_date:TenderField=Field(default_factory=TenderField); pre_bid_time:TenderField=Field(default_factory=TenderField); pre_bid_location:TenderField=Field(default_factory=TenderField); submission_location:TenderField=Field(default_factory=TenderField); delivery_period:TenderField=Field(default_factory=TenderField); bid_validity:TenderField=Field(default_factory=TenderField); quantity:TenderField=Field(default_factory=TenderField); warranty:TenderField=Field(default_factory=TenderField); bid_security:TenderField=Field(default_factory=TenderField); performance_security:TenderField=Field(default_factory=TenderField); required_documents:TenderField=Field(default_factory=TenderField)
