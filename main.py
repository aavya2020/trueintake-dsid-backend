from fastapi import FastAPI, Query
import pandas as pd

app = FastAPI()

df = pd.read_csv("final_dsid_backend_ready.csv")

def map_age_group_input(age_group: str) -> str:
    if age_group == "Adult":
        return "adult"
    elif age_group == "Children 4+":
        return "4"
    elif age_group == "Children 1-4":
        return "1-4"
    return age_group

@app.get("/predict")
def predict_nutrient(
    nutrient: str = Query(..., description="Nutrient name (e.g., Calcium)"),
    label_value: float = Query(..., description="Label value per serving"),
    age_group: str = Query(..., description="Age group: Adult, Children 4+, or Children 1-4")
):
    age_group_mapped = map_age_group_input(age_group)
    row = df[
        (df["DSID Ingredient Name"].str.lower() == nutrient.lower()) &
        (df["Age Group"] == age_group_mapped)
    ]
    if row.empty:
        return {"error": "No matching data found."}
    result = row.iloc[0]
    predicted = (label_value / result["NHANES Supplement Label Value per Serving"]) * result["Predicted Mean Value per Serving"]
    return {
        "input_label_value": label_value,
        "predicted_actual_value": round(predicted, 2),
        "unit": result["Unit per Serving"]
    }