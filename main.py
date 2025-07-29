from fastapi import FastAPI, Query
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

df = pd.read_excel("DSID4CombinedDataFiles.xlsx", sheet_name="Table1", engine="openpyxl", header=1)

category_map = {
    "01": "Adult",
    "02": "Children 4+",
    "02A": "Children 1-4",
    "05": "Adult"
}

def map_age_group(code):
    code = str(code).strip()
    if code in category_map:
        return category_map[code]
    elif code.startswith("02") and "1 - <4" in code:
        return "Children 1-4"
    return "Unknown"

df["Age Group"] = df["DSID Study Category Code"].apply(map_age_group)

class PredictionInput(BaseModel):
    nutrient: str
    label_value: float
    age_group: str

@app.post("/predict")
def predict_nutrient(data: PredictionInput):
    nutrient_data = df[df["DSID Ingredient Name"].str.lower() == data.nutrient.lower()]
    nutrient_data = nutrient_data[nutrient_data["Age Group"].str.lower() == data.age_group.lower()]
    if nutrient_data.empty:
        return {"error": "No matching data found for given nutrient and age group"}

    prediction_row = nutrient_data.iloc[0]
    predicted_mean = prediction_row["Predicted Mean Value per Serving"]
    percent_diff = prediction_row["Predicted % Difference from Label for Predicted Mean"]

    return {
        "Predicted Mean Value": predicted_mean,
        "Predicted % Difference": percent_diff
    }