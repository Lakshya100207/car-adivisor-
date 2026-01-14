from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Optional, List
import json
from pathlib import Path
import math

app = FastAPI(title="Car Advisor API", version="3.0.0")

# Load cars data
DATA_PATH = Path("data/cars.json")
cars_data = []
if DATA_PATH.exists():
    with open(DATA_PATH, 'r') as f:
        cars_data = json.load(f)

# Pydantic Models
class UserQuery(BaseModel):
    query: str
    user_income: Optional[float] = None
    max_budget: Optional[float] = None

class EMIRequest(BaseModel):
    principal: float
    annual_rate: float
    tenure_years: float

# === DAY 2: EMI CALCULATOR ===
def calculate_emi(principal: float, annual_rate: float, tenure_years: float) -> dict:
    monthly_rate = annual_rate / 12 / 100
    tenure_months = tenure_years * 12
    if monthly_rate == 0:
        emi = principal / tenure_months
    else:
        emi = principal * monthly_rate * (1 + monthly_rate)**tenure_months / ((1 + monthly_rate)**tenure_months - 1)
    total_payment = emi * tenure_months
    return {
        "emi_amount": round(emi, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_payment - principal, 2)
    }

# === DAY 2: CAR DATABASE TOOLS ===
def get_car_by_name(name: str):
    for car in cars_data:
        if name.lower() in car["name"].lower():
            return car
    return None

def get_cars_by_budget(max_price: float):
    return [car for car in cars_data if car["price"] <= max_price]

# === DAY 2: RULE ENGINE ===
def apply_safety_rules(emi_amount: float, user_income: float):
    if user_income is None:
        return {"approved": True, "message": "ℹ️ Income not provided - Skipping safety check"}
    max_emi = (user_income / 12) * 0.3
    if emi_amount <= max_emi:
        return {"approved": True, "message": f"✅ Safe EMI (₹{emi_amount} ≤ ₹{max_emi:.0f})"}
    return {"approved": False, "message": f"❌ Risky EMI (₹{emi_amount} > ₹{max_emi:.0f})"}

# === DAY 3: INTENT DETECTION + MAIN ENDPOINT ===
def detect_intent(query: str) -> str:
    query_lower = query.lower()
    if any(word in query_lower for word in ['emi', 'loan', 'finance', 'monthly', 'emi']):
        return "emi_calculation"
    elif any(word in query_lower for word in ['budget', 'lakhs', 'crore', 'price under']):
        return "budget_search"
    elif any(word in query_lower for word in ['compare', 'vs', 'versus']):
        return "car_comparison"
    elif any(word in query_lower for word in ['find', 'show', 'which']):
        return "car_search"
    else:
        return "general_info"

def process_user_query(query_data: UserQuery):
    intent = detect_intent(query_data.query)
    
    # Call appropriate tool
    if intent == "emi_calculation":
        # Use first car's price for demo or budget
        principal = query_data.max_budget or 1500000
        tool_result = calculate_emi(principal, 9.5, 5)
        emi_amount = tool_result["emi_amount"]
        safety_result = apply_safety_rules(emi_amount, query_data.user_income)
    elif intent == "budget_search":
        tool_result = get_cars_by_budget(query_data.max_budget or 2000000)
        safety_result = {"approved": True, "message": "✅ Budget search completed"}
    elif intent == "car_comparison":
        tool_result = {"message": "Comparison feature coming in Day 4"}
        safety_result = {"approved": True, "message": "✅ Comparison ready"}
    elif intent == "car_search":
        tool_result = get_car_by_name(query_data.query)
        safety_result = {"approved": True, "message": "✅ Car found"}
    else:
        tool_result = {"cars_count": len(cars_data)}
        safety_result = {"approved": True, "message": "✅ General info"}
    
    return {
        "intent": intent,
        "user_query": query_data.query,
        "tool_output": tool_result,
        "safety_check": safety_result,
        "recommended_action": f"Processed {intent.replace('_', ' ')} successfully"
    }

# === API ENDPOINTS ===
@app.get("/")
def root():
    return {"message": "Car Advisor Backend - Day 3 Ready 🚗💰", "cars_count": len(cars_data)}

@app.get("/cars")
def get_cars():
    return {"cars": cars_data}

# Day 2 Test Endpoints
@app.get("/emi/{principal}/{rate}/{tenure}")
def test_emi(principal: float, rate: float, tenure: float):
    return calculate_emi(principal, rate, tenure)

@app.get("/car/{name}")
def test_car(name: str):
    return get_car_by_name(name) or {"error": "Car not found"}

@app.get("/cars/budget/{max_price}")
def test_budget(max_price: float):
    return get_cars_by_budget(max_price)

@app.get("/rules/{emi}/{income}")
def test_rules(emi: float, income: float):
    return apply_safety_rules(emi, income)

# === DAY 3: MAIN ENDPOINT ===
@app.post("/process_query")
def process_query(query: UserQuery = Body(...)):
    """Main endpoint - Day 3 requirement"""
    return process_user_query(query)
