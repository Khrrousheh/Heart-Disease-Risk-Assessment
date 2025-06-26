from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import math

app = FastAPI()

# Mount static files and setup templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class RiskFactors(BaseModel):
    age: int
    gender: str  # "male" or "female"
    total_cholesterol: int
    hdl_cholesterol: int
    systolic_bp: int
    smoker: bool
    diabetic: bool


def calculate_framingham_risk(factors: RiskFactors) -> dict:
    """
    Calculate 10-year cardiovascular disease risk using Framingham algorithm
    Returns risk percentage and category
    """
    # Simplified Framingham calculation (actual implementation would be more complex)
    risk_score = 0

    # Age factors
    if factors.gender == "male":
        risk_score += factors.age * 0.5
    else:
        risk_score += factors.age * 0.4

    # Cholesterol factors
    risk_score += (factors.total_cholesterol / factors.hdl_cholesterol) * 0.3

    # Blood pressure factors
    if factors.systolic_bp >= 140:
        risk_score += 1.5
    elif factors.systolic_bp >= 120:
        risk_score += 0.8

    # Behavioral factors
    if factors.smoker:
        risk_score += 1.4
    if factors.diabetic:
        risk_score += 1.3

    # Convert score to percentage (simplified for demo)
    risk_percentage = min(100, max(1, risk_score * 3))

    # Determine risk category
    if risk_percentage < 10:
        category = "Low"
    elif risk_percentage < 20:
        category = "Moderate"
    else:
        category = "High"

    return {
        "risk_percentage": round(risk_percentage, 1),
        "risk_category": category
    }


def get_recommendations(risk_category: str) -> list:
    """Generate recommendations based on risk level"""
    base_recommendations = [
        "Maintain a healthy diet rich in fruits and vegetables",
        "Engage in at least 150 minutes of moderate exercise weekly"
    ]

    if risk_category == "Low":
        return base_recommendations + [
            "Regular health check-ups every 2 years"
        ]
    elif risk_category == "Moderate":
        return base_recommendations + [
            "Consult with your primary care physician",
            "Consider cholesterol screening annually",
            "Monitor blood pressure regularly"
        ]
    else:  # High
        return base_recommendations + [
            "Urgent consultation with a cardiologist",
            "Medication evaluation may be needed",
            "Comprehensive cardiac workup recommended"
        ]


@app.get("/", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/calculate", response_class=HTMLResponse)
async def calculate_risk(
        request: Request,
        age: int = Form(...),
        gender: str = Form(...),
        total_cholesterol: int = Form(...),
        hdl_cholesterol: int = Form(...),
        systolic_bp: int = Form(...),
        smoker: bool = Form(False),
        diabetic: bool = Form(False)
):
    # Create risk factors object
    factors = RiskFactors(
        age=age,
        gender=gender,
        total_cholesterol=total_cholesterol,
        hdl_cholesterol=hdl_cholesterol,
        systolic_bp=systolic_bp,
        smoker=smoker,
        diabetic=diabetic
    )

    # Calculate risk
    risk_result = calculate_framingham_risk(factors)
    recommendations = get_recommendations(risk_result["risk_category"])

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "factors": factors,
            "risk_result": risk_result,
            "recommendations": recommendations
        }
    )