
# TrueIntake DSID Backend

This FastAPI project powers the DSID prediction engine for TrueIntake AI.

## API Endpoint

`GET /predict`

**Query Parameters:**
- `nutrient`: Nutrient name (e.g., "Vitamin C")
- `label_claim`: Numeric label claim (e.g., 60)
- `age_group`: One of "Adult", "Children 4+", or "Children 1-4"

**Returns:**
Predicted measured nutrient amount using DSID regression model.

## Deployment

Use Render.com or Vercel backend with a `Procfile`:

```
web: uvicorn main:app --host 0.0.0.0 --port 10000
```
