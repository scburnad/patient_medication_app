from fastapi import FastAPI

from patient_medication_app.api import api_router

app = FastAPI(
    title="Patient Medication", description="Patient Medication API", version="0.1.0"
)

app.include_router(api_router, tags=["api"])


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
