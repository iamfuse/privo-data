from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import io
import pandas as pd
import hashlib

app = FastAPI()

# Add this root endpoint
@app.get("/")
async def root():
    return {"message": "Privio Data Unifier API is running."}

# Your existing code...
# Fields to anonymize
ANON_FIELDS = ['name', 'email']

def anonymize_value(val: str) -> str:
    if not val:
        return val
    return hashlib.sha256(val.encode()).hexdigest()[:10]

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid CSV file or format"})

    for col in ANON_FIELDS:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(anonymize_value)

    sample = df.head(3).to_dict(orient='records')
    return {"message": f"File '{file.filename}' uploaded and processed.", "sample_data": sample}
