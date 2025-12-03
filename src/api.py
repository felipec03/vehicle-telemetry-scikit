import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from .data_loader import load_and_preprocess_data
from .predictive_maintenance import train_maintenance_model
from .route_optimization import optimize_routes

app = FastAPI(
    title="Fleet Management ML API",
    description="API for Vehicle Predictive Maintenance and Route Optimization",
    version="1.0.0"
)

# Global variables to store models and data
model = None
df_combined = None

class VehicleData(BaseModel):
    mileage: float
    vehicle_age: int
    fuel_efficiency: float
    battery_health: float
    engine_health: float
    avg_speed: float
    avg_accel: float
    odometer_reading: float

class PredictionResponse(BaseModel):
    needs_maintenance: bool
    maintenance_probability: Optional[float] = None
    input_data: VehicleData

class Location(BaseModel):
    lat: float
    long: float

class RouteRequest(BaseModel):
    locations: List[Location]
    n_vehicles: int = 5

class RouteResponse(BaseModel):
    routes: Dict[int, List[tuple]]

@app.on_event("startup")
async def startup_event():
    global model, df_combined
    print("Loading data and training model on startup...")
    
    # Define paths - try to find them relative to where we are running
    # Assuming running from root or src
    files = [
        "data/67a6fef440f8a5868a2e023e_DLP Labs_Sample.csv",
        "data/data_for_fleet_dna_composite_data.csv",
        "data/data_for_fleet_dna_delivery_vans.csv"
    ]
    
    dfs = []
    
    # Check current directory and parent directory
    search_dirs = [".", ".."]
    
    for fname in files:
        found = False
        for d in search_dirs:
            fpath = os.path.join(d, fname)
            if os.path.exists(fpath):
                print(f"Processing {fname} from {d}...")
                try:
                    d_df = load_and_preprocess_data(fpath)
                    dfs.append(d_df)
                    found = True
                    break
                except Exception as e:
                    print(f"Error loading {fname}: {e}")
        if not found:
            print(f"Warning: File {fname} not found in {search_dirs}")

    if dfs:
        df_combined = pd.concat(dfs, ignore_index=True)
        print(f"Combined Data Shape: {df_combined.shape}")
        
        # Train model
        print("Training maintenance model...")
        trained_model, metrics = train_maintenance_model(df_combined)
        model = trained_model
        print(f"Model trained. Accuracy: {metrics['accuracy']:.2%}")
    else:
        print("No data loaded. Model will not be available.")

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict-maintenance", response_model=PredictionResponse)
def predict_maintenance(data: VehicleData):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not trained or data not loaded")
    
    # Prepare input dataframe
    input_df = pd.DataFrame([data.dict()])
    
    # Ensure columns match what the model expects (based on predictive_maintenance.py)
    # The model was trained on: ['mileage', 'vehicle_age', 'fuel_efficiency', 'battery_health', 'engine_health', 'avg_speed', 'avg_accel', 'odometer_reading']
    # Pydantic model matches these fields.
    
    prediction = model.predict(input_df)[0]
    
    # Get probability if supported
    prob = None
    if hasattr(model, "predict_proba"):
        prob = float(model.predict_proba(input_df)[0][1]) # Probability of class 1 (needs maintenance)
        
    return PredictionResponse(
        needs_maintenance=bool(prediction),
        maintenance_probability=prob,
        input_data=data
    )

@app.post("/optimize-routes")
def get_optimized_routes(request: RouteRequest):
    # Convert input locations to DataFrame expected by optimize_routes
    # optimize_routes expects a DataFrame with 'lat' and 'long' columns
    
    data = [{"lat": loc.lat, "long": loc.long} for loc in request.locations]
    df_loc = pd.DataFrame(data)
    
    if df_loc.empty:
         raise HTTPException(status_code=400, detail="No locations provided")

    try:
        # optimize_routes returns a dict of {vehicle_id: [(lat, long), ...]}
        # We need to adapt it because optimize_routes currently prints and plots, 
        # but also returns the routes dict.
        # However, looking at route_optimization.py, it saves a plot. 
        # In an API context, we might just want the data.
        
        routes = optimize_routes(df_loc, n_vehicles=request.n_vehicles)
        
        # The keys in routes are integers (0, 1, 2...), but JSON keys must be strings.
        # Pydantic/FastAPI handles int keys in Dict[int, ...] by converting to strings in JSON output usually,
        # but let's be safe or just return as is and let FastAPI handle serialization.
        
        return {"routes": routes}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
