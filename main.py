from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

# Load all data from the Excel sheet 'Table1'
df = pd.read_excel("DSID4CombinedDataFiles.xlsx", sheet_name="Table1", engine="openpyxl")

# Normalize age group values
def map_age_group(val):
    if str(val).strip() == "Adult":
        return "Adult"
    elif str(val).strip() == "4":
        return "Children 4+"
    elif str(val).strip() == "1-4":
        return "Children 1-4"
    else:
        return str(val).strip()

df["Age Group"] = df["Age Group"].apply(map_age_group)

class PredictionRequest(BaseModel):
    nutrient_name: str
    label_claim: float
    age_group: str

@app.post("/predict")
def predict_nutrient(request: PredictionRequest):
    try:
        nutrient = request.nutrient_name.strip()
        age_group = request.age_group.strip()

        match = df[(df["Nutrient Name"].str.lower() == nutrient.lower()) & 
                   (df["Age Group"] == age_group)]

        if match.empty:
            raise HTTPException(status_code=404, detail="No matching record found.")

        intercept = match["Intercept"].values[0]
        slope = match["Slope"].values[0]
        predicted = intercept + slope * request.label_claim

        return {
            "predicted_actual_content": round(predicted, 2),
            "unit": match["Unit"].values[0],
            "slope": round(slope, 4),
            "intercept": round(intercept, 4)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
