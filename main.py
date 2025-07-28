
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the regression model data
df = pd.read_csv("dsid_all_model_data.csv")

@app.get("/")
def read_root():
    return {"message": "TrueIntake DSID API is live!"}

@app.post("/predict")
def predict(nutrient: str, label_claim: float, age_group: str):
    # Normalize input
    nutrient = nutrient.strip().lower()
    age_group = age_group.strip()

    # Search for matching row
    row = df[
        (df['Nutrient'].str.strip().str.lower() == nutrient) &
        (df['AgeGroup'].str.strip() == age_group)
    ]

    if row.empty:
        raise HTTPException(status_code=404, detail="Nutrient or age group not found")

    intercept = row['Intercept'].values[0]
    slope = row['Slope'].values[0]
    quadratic = row['Quadratic'].values[0]

    predicted = intercept + slope * label_claim + quadratic * (label_claim ** 2)

    return {
        "age_group": age_group,
        "nutrient": nutrient.title(),
        "label_claim": label_claim,
        "predicted_measured_amount": round(predicted, 2)
    }
