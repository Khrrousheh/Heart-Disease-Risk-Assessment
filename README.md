# Framingham Cardiovascular Risk Calculator

This is a web-based application built using **FastAPI** and **Jinja2** that calculates the 10-year cardiovascular disease (CVD) risk using the **Framingham Risk Score** algorithm. It supports input for various risk factors and provides personalized health recommendations based on the calculated risk level.

## Features

- Calculates 10-year CVD risk for both men and women
- Uses Framingham algorithm with inputs such as:
  - Age
  - Gender
  - Total cholesterol
  - HDL cholesterol
  - Systolic blood pressure (with/without treatment)
  - Smoking status
  - Diabetes status
- Categorizes risk into **Low**, **Moderate**, or **High**
- Provides actionable health recommendations
- Web interface with HTML form

## Tech Stack

- **FastAPI** – for backend API and routing
- **Jinja2** – for HTML templating
- **Pydantic** – for data validation
- **HTML/CSS** – for the frontend (templates and static files)

## Getting Started

### Prerequisites

- Python 3.8+
- `pip` package manager

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/framingham-risk-calculator.git
   cd framingham-risk-calculator
