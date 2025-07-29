
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

df = pd.read_csv("dsid_model_parameters.csv")

@app.get("/predict")
def predict(nutrient: str, label_value: float, age_group: str):
    try:
        filtered_df = df[
            (df["Nutrient Name"].str.lower() == nutrient.lower()) &
            (df["Age Group"].str.lower() == age_group.lower())
        ]
        if filtered_df.empty:
            return {"error": "No matching nutrient and age group found"}

        slope = filtered_df["Slope"].values[0]
        intercept = filtered_df["Intercept"].values[0]
        predicted_value = slope * label_value + intercept

        return {
            "nutrient": nutrient,
            "label_value": label_value,
            "age_group": age_group,
            "predicted_value": predicted_value
        }
    except Exception as e:
        return {"error": str(e)}
