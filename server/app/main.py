from fastapi import FastAPI
from .routers import patient, immunization, finance

app = FastAPI()

# Include routers
app.include_router(patient.router)
app.include_router(immunization.router)
app.include_router(finance.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)