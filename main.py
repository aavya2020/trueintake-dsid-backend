
from fastapi import FastAPI, Query
import pandas as pd

app = FastAPI()

# Load all regression model data with age group
df = pd.read_csv("dsid_all_model_data.csv")

@app.get("/predict")
def predict(nutrient: str = Query(...), label_claim: float = Query(...), age_group: str = Query(...)):
    row = df[
        (df["Nutrient"].str.lower() == nutrient.lower()) &
        (df["AgeGroup"].str.lower() == age_group.lower())
    ]
    if row.empty:
        return {"error": "Nutrient or age group not found"}

    a = float(row["Intercept"].values[0])
    b = float(row["Linear_Coeff"].values[0])
    c = float(row["Quadratic_Coeff"].values[0])

    predicted = a + b * label_claim + c * (label_claim ** 2)
    return {
        "age_group": age_group,
        "nutrient": nutrient,
        "label_claim": label_claim,
        "predicted_measured_amount": round(predicted, 2)
    }
