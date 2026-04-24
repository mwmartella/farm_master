from fastapi import FastAPI

from app.routers import worker_codes, workers, worker_times

app = FastAPI(
    title="Worker Management API",
    version="0.1.0",
)

app.include_router(worker_codes.router)
app.include_router(workers.router)
app.include_router(worker_times.router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}