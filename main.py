from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional

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
    bp_treated: Optional[bool] = False


def calculate_framingham_risk(factors: RiskFactors) -> dict:
    """
    Calculate 10-year cardiovascular disease risk using the full Framingham algorithm
    Returns risk percentage and category based on:
    - Age
    - Total cholesterol
    - HDL cholesterol
    - Systolic BP (treated/untreated)
    - Smoking status
    - Diabetes status
    """

    if factors.gender == "male":
        return _calculate_male_framingham(
            factors.age,
            factors.total_cholesterol,
            factors.hdl_cholesterol,
            factors.systolic_bp,
            factors.smoker,
            factors.diabetic,
            factors.bp_treated
        )
    else:
        return _calculate_female_framingham(
            factors.age,
            factors.total_cholesterol,
            factors.hdl_cholesterol,
            factors.systolic_bp,
            factors.smoker,
            factors.diabetic,
            factors.bp_treated
        )


def _calculate_male_framingham(age, total_chol, hdl, sbp, smoker, diabetic, bp_treated):
    """Calculate Framingham risk for males"""
    points = 0

    # Age points
    if age >= 70:
        points += 12
    elif age >= 65:
        points += 11
    elif age >= 60:
        points += 10
    elif age >= 55:
        points += 8
    elif age >= 50:
        points += 6
    elif age >= 45:
        points += 4
    elif age >= 40:
        points += 2
    elif age >= 35:
        points += 1

    # Total cholesterol points by age group
    if age >= 70:
        points += _get_cholesterol_points(total_chol, [0, 1, 2, 3, 4])
    elif age >= 60:
        points += _get_cholesterol_points(total_chol, [0, 1, 2, 3, 4])
    elif age >= 50:
        points += _get_cholesterol_points(total_chol, [0, 1, 2, 3, 4])
    elif age >= 40:
        points += _get_cholesterol_points(total_chol, [0, 1, 2, 3, 4])
    else:  # 20-39
        points += _get_cholesterol_points(total_chol, [0, 4, 7, 9, 11])

    # HDL cholesterol points
    points += _get_hdl_points(hdl)

    # Systolic BP points
    points += _get_bp_points(sbp, bp_treated)

    # Smoking adds points
    if smoker: points += 4

    # Diabetes adds points
    if diabetic: points += 3

    # Convert points to risk percentage
    risk_percentage = _male_points_to_risk(points)

    # Determine category
    if risk_percentage < 6:
        category = "Low"
    elif risk_percentage < 20:
        category = "Moderate"
    else:
        category = "High"

    return {
        "risk_percentage": risk_percentage,
        "risk_category": category,
        "points": points
    }


def _calculate_female_framingham(age, total_chol, hdl, sbp, smoker, diabetic, bp_treated):
    """Calculate Framingham risk for females"""
    points = 0

    # Age points
    if age >= 70:
        points += 16
    elif age >= 65:
        points += 14
    elif age >= 60:
        points += 12
    elif age >= 55:
        points += 10
    elif age >= 50:
        points += 8
    elif age >= 45:
        points += 6
    elif age >= 40:
        points += 4
    elif age >= 35:
        points += 2

    # Total cholesterol points by age group
    if age >= 70:
        points += _get_cholesterol_points(total_chol, [0, 1, 2, 3, 4])
    elif age >= 60:
        points += _get_cholesterol_points(total_chol, [0, 1, 2, 3, 4])
    elif age >= 50:
        points += _get_cholesterol_points(total_chol, [0, 1, 2, 3, 4])
    elif age >= 40:
        points += _get_cholesterol_points(total_chol, [0, 1, 2, 3, 4])
    else:  # 20-39
        points += _get_cholesterol_points(total_chol, [0, 4, 7, 9, 11])

    # HDL cholesterol points
    points += _get_hdl_points(hdl)

    # Systolic BP points
    points += _get_bp_points(sbp, bp_treated)

    # Smoking adds points
    if smoker: points += 3

    # Diabetes adds points
    if diabetic: points += 4

    # Convert points to risk percentage
    risk_percentage = _female_points_to_risk(points)

    # Determine category
    if risk_percentage < 5:
        category = "Low"
    elif risk_percentage < 20:
        category = "Moderate"
    else:
        category = "High"

    return {
        "risk_percentage": risk_percentage,
        "risk_category": category,
        "points": points
    }


def _get_cholesterol_points(total_chol, thresholds):
    """Helper for cholesterol points"""
    if total_chol < 160:
        return thresholds[0]
    elif total_chol < 200:
        return thresholds[1]
    elif total_chol < 240:
        return thresholds[2]
    elif total_chol < 280:
        return thresholds[3]
    return thresholds[4]


def _get_hdl_points(hdl):
    """Helper for HDL points"""
    if hdl >= 60:
        return -2
    elif hdl >= 50:
        return -1
    elif hdl >= 40:
        return 0
    elif hdl >= 35:
        return 1
    return 2


def _get_bp_points(sbp, treated):
    """Helper for BP points"""
    if sbp < 120:
        points = 0
    elif sbp < 130:
        points = 1
    elif sbp < 140:
        points = 2
    elif sbp < 160:
        points = 3
    else:
        points = 4
    return points + (2 if treated else 0)


def _male_points_to_risk(points):
    """Convert male Framingham points to risk percentage"""
    risk_map = [
        (0, 1), (5, 2), (7, 3), (8, 4), (9, 5), (10, 6),
        (11, 8), (12, 10), (13, 12), (14, 16), (15, 20),
        (16, 25), (17, 30)
    ]
    for threshold, risk in risk_map:
        if points < threshold:
            return risk
    return 30


def _female_points_to_risk(points):
    """Convert female Framingham points to risk percentage"""
    risk_map = [
        (9, 1), (12, 2), (14, 3), (15, 4), (16, 5), (17, 6),
        (18, 8), (19, 11), (20, 14), (21, 17), (22, 22),
        (23, 27), (24, 30)
    ]
    for threshold, risk in risk_map:
        if points < threshold:
            return risk
    return 30


def get_recommendations(risk_category: str, gender: str) -> list:
    """Generate recommendations based on risk level"""
    base_recommendations = [
        "Maintain a healthy diet rich in fruits and vegetables",
        "Engage in at least 150 minutes of moderate exercise weekly",
        "Maintain a healthy weight (BMI 18.5-24.9)"
    ]

    gender_specific = [
        "Reduce alcohol consumption (≤2 drinks/day for men, ≤1 for women)"
    ]

    if risk_category == "Low":
        return base_recommendations + gender_specific + [
            "Regular health check-ups every 2 years",
            "Monitor blood pressure annually"
        ]
    elif risk_category == "Moderate":
        return base_recommendations + gender_specific + [
            "Consult with your primary care physician",
            "Consider cholesterol screening annually",
            "Monitor blood pressure regularly (every 6 months)",
            "Consider aspirin therapy (discuss with doctor)"
        ]
    else:  # High
        return base_recommendations + gender_specific + [
            "Urgent consultation with a cardiologist",
            "Medication evaluation may be needed (statins, antihypertensives)",
            "Comprehensive cardiac workup recommended",
            "Strict blood pressure control (<130/80 mmHg)",
            "LDL cholesterol target <100 mg/dL (or <70 if very high risk)"
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
        diabetic: bool = Form(False),
        bp_treated: bool = Form(False)
):
    # Create risk factors object
    factors = RiskFactors(
        age=age,
        gender=gender,
        total_cholesterol=total_cholesterol,
        hdl_cholesterol=hdl_cholesterol,
        systolic_bp=systolic_bp,
        smoker=smoker,
        diabetic=diabetic,
        bp_treated=bp_treated
    )

    # Calculate risk
    risk_result = calculate_framingham_risk(factors)
    recommendations = get_recommendations(risk_result["risk_category"], factors.gender)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "factors": factors,
            "risk_result": risk_result,
            "recommendations": recommendations
        }
    )