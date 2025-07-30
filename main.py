from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the cleaned CSV
df = pd.read_csv("dsid_model_parameters.csv")

@app.get("/predict")
def predict(
    nutrient: str = Query(..., description="Name of the nutrient (e.g., Calcium)"),
    label_value: float = Query(..., description="Label claim value"),
    age_group: str = Query(..., description="Age group (Adult, Children 4+, Children 1-4)")
):
    try:
        # Normalize and filter the row
        filtered_df = df[
            (df["Nutrient Name"].str.lower() == nutrient.lower()) &
            (df["Age Group"].str.lower() == age_group.lower())
        ]

        if filtered_df.empty:
            return {"error": "No matching nutrient and age group found"}

        # Get slope and intercept
        slope = filtered_df.iloc[0]["Slope"]
        intercept = filtered_df.iloc[0]["Intercept"]

        # Calculate predicted value
        predicted_value = slope * label_value + intercept

        return {
            "nutrient": nutrient,
            "label_value": label_value,
            "age_group": age_group,
            "predicted_value": round(predicted_value, 2)
        }

    except Exception as e:
        return {"error": str(e)}