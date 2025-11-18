from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from schemas import UserInput, PredictionResponse
import pickle
import pandas as pd

# Load the ML model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

MODEL_VERSION = "1.0.0"

app = FastAPI(
    title="Insurance Premium Prediction API",
    description="API for predicting insurance premium categories based on user data",
    version=MODEL_VERSION
)

def predict_output(user_data: dict) -> dict:
    """Make prediction using the trained model"""
    input_df = pd.DataFrame([user_data])
    
    prediction = model.predict(input_df)[0]
    
    response = {
        'predicted_category': str(prediction)
    }
    
    if hasattr(model, 'predict_proba'):
        probabilities = model.predict_proba(input_df)[0]
        confidence = float(max(probabilities))
        
        if hasattr(model, 'classes_'):
            class_probs = {
                str(class_name): round(float(prob), 4)
                for class_name, prob in zip(model.classes_, probabilities)
            }
            response['confidence'] = round(confidence, 4)
            response['class_probabilities'] = class_probs
    
    return response

@app.get('/')
def home():
    """Human-readable welcome message"""
    return {
        'message': 'Insurance Premium Prediction API',
        'version': MODEL_VERSION,
        'endpoints': {
            'docs': '/docs',
            'health': '/health',
            'predict': '/predict'
        }
    }

@app.get('/health')
def health_check():
    """Machine-readable health check"""
    return {
        'status': 'OK',
        'version': MODEL_VERSION,
        'model_loaded': model is not None,
        'model_type': type(model).__name__
    }

@app.post('/predict')
async def predict_premium(request: Request, data: UserInput):
    """Predict insurance premium category"""
    
    body = await request.body()
    print("\n=== RAW REQUEST ===")
    print(body.decode())
    print("===================\n")
    
    print("\n=== PARSED DATA ===")
    print(f"Age: {data.age} → Age Group: {data.age_group}")
    print(f"Weight: {data.weight}kg, Height: {data.height}m → BMI: {data.bmi}")
    print(f"Smoker: {data.smoker} → Lifestyle Risk: {data.lifestyle_risk}")
    print(f"City: {data.city} → City Tier: {data.city_tier}")
    print(f"Income: {data.income_lpa} LPA")
    print(f"Occupation: {data.occupation}")
    print("===================\n")
    
    user_input = {
        'bmi': data.bmi,
        'age_group': data.age_group,
        'lifestyle_risk': data.lifestyle_risk,
        'city_tier': data.city_tier,
        'income_lpa': data.income_lpa,
        'occupation': data.occupation
    }
    
    input_df = pd.DataFrame([user_input])
    
    print("\n=== DATAFRAME ===")
    print(input_df)
    print(input_df.dtypes)
    print("=================\n")
    
    try:
        prediction = predict_output(user_input)
        
        print(f"\n=== PREDICTION: {prediction['predicted_category']} ===\n")
        
        return JSONResponse(
            status_code=200, 
            content={'response': prediction}
        )
    
    except Exception as e:
        print(f"\n=== ERROR: {str(e)} ===\n")
        return JSONResponse(
            status_code=500, 
            content={
                'error': 'Prediction failed',
                'message': str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)