import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Load the combined DSID data
df = pd.read_excel("DSID4CombinedDataFiles.xlsx", sheet_name="Table 1", engine='openpyxl')
df.columns = df.columns.str.strip()

# Rename age group to match frontend format
df["Age Group"] = df["DSID Study Category Description"].apply(
    lambda x: "Adult" if "Adult" in x else "Children 1–4" if "1 - <4" in x else "Children 4+"
)

# Nutrient mapping to match frontend names
df["Nutrient"] = df["DSID Ingredient Name"].str.strip().str.lower()

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionRequest(BaseModel):
    nutrient: str
    label_claim: float
    age_group: str

@app.post("/predict")
async def predict_nutrient(req: PredictionRequest):
    try:
        match = df[
            (df["Nutrient"].str.lower() == req.nutrient.strip().lower()) &
            (df["Age Group"] == req.age_group.strip())
        ]

        if match.empty:
            raise HTTPException(status_code=404, detail="Nutrient or age group not found")

        slope = match.iloc[0]["Predicted % Difference from Label for Predicted Mean"]
        predicted = req.label_claim * (1 + slope / 100)

        return {
            "nutrient": req.nutrient,
            "label_claim": req.label_claim,
            "age_group": req.age_group,
            "predicted_measured_amount": round(predicted, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))