from fastapi import FastAPI

app = FastAPI(title="Wagon Inspection System")

@app.get("/")
def root():
    return {
        "message": "Wagon Yard Line Final Inspection API is running"
    }

@app.get("/health")
def health():
    return {"status": "OK"}
