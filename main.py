from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load regression data
df = pd.read_csv("dsid_all_model_data.csv")

@app.get("/")
def read_root():
    return {"message": "DSID Prediction API is running."}

@app.post("/predict")
def predict_nutrient(age_group: str, nutrient: str, label_claim: float):
    # Filter data for nutrient and age group
    matched_rows = df[
        (df["DSID Ingredient Name"].str.lower() == nutrient.lower()) &
        (df["DSID Study Category Code"].str.lower().str.contains(age_group.lower()))
    ]
    if matched_rows.empty:
        raise HTTPException(status_code=404, detail="Nutrient or age group not found")

    try:
        # Use predicted % difference from label to estimate measured value
        pct_diff = matched_rows["Predicted % Difference from Label for Predicted Mean"].astype(float).values[0]
        predicted_measured_amount = label_claim * (1 + pct_diff / 100)
        return {
            "age_group": age_group,
            "nutrient": nutrient,
            "label_claim": label_claim,
            "predicted_measured_amount": round(predicted_measured_amount, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))