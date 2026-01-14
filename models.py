from pydantic import BaseModel
from typing import Optional, Dict

class UserQuery(BaseModel):
    query: str
    user_income: Optional[float] = None

class CarSpecs(BaseModel):
    name: str
    price: float
    fuel_type: str
    seating_capacity: int
    safety_rating: str
    model_year: int

class EMIRequest(BaseModel):
    principal: float
    annual_rate: float
    tenure_years: float

class APIResponse(BaseModel):
    success: bool
    data: dict
    message: str

