
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

df = pd.read_excel("DSID4CombinedDataFiles.xlsx", sheet_name="Table1", engine="openpyxl")
df.columns = df.columns.str.strip()

def map_age_group(desc):
    desc = str(desc)
    if "1 - <4" in desc:
        return "Children 1-4"
    elif "4 years and older" in desc or "4+" in desc:
        return "Children 4+"
    elif "Adult" in desc:
        return "Adult"
    return "Unknown"

df["Age Group"] = df["DSID Study Category Description"].apply(map_age_group)
df["Nutrient Name"] = df["DSID Ingredient Name"].str.strip().str.lower()

class PredictionRequest(BaseModel):
    nutrient_name: str
    label_claim: float
    age_group: str

@app.post("/predict")
def predict_nutrient(request: PredictionRequest):
    try:
        nutrient = request.nutrient_name.strip().lower()
        age_group = request.age_group.strip()

        match = df[
            (df["Nutrient Name"] == nutrient) &
            (df["Age Group"] == age_group)
        ]

        if match.empty:
            raise HTTPException(status_code=404, detail="No matching record found.")

        slope = match["Predicted % Difference from Label for Predicted Mean"].values[0]
        predicted = request.label_claim * (1 + slope / 100)

        return {
            "nutrient": request.nutrient_name,
            "label_claim": request.label_claim,
            "predicted_measured_amount": round(predicted, 2),
            "slope_percent": round(slope, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
