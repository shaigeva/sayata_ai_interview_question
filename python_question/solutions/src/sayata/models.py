from pydantic import BaseModel


class SubmissionCreate(BaseModel):
    business_name: str
    industry: str
    annual_revenue: float
    requested_limit: float
    requested_retention: float


class Submission(BaseModel):
    id: str
    business_name: str
    industry: str
    annual_revenue: float
    requested_limit: float
    requested_retention: float
    status: str = "created"


class Quote(BaseModel):
    carrier: str
    premium: int
    limit: float
    retention: float
    quote_id: str


class SubmissionResponse(BaseModel):
    id: str
    status: str


class SubmissionDetail(BaseModel):
    id: str
    business_name: str
    industry: str
    annual_revenue: float
    requested_limit: float
    requested_retention: float
    status: str
    quotes: list[Quote]


class BindRequest(BaseModel):
    quote_id: str
    carrier: str


class BindResponse(BaseModel):
    status: str
    quote_id: str
    carrier: str
