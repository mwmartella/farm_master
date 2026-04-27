from fastapi import FastAPI

from app.routers import worker_codes, workers, worker_times, businesses, sites, fields, fruit_types, varieties, variety_clones, blocks, rootstocks

app = FastAPI(
    title="Farm Master API",
    version="0.1.0",
)

app.include_router(worker_codes.router)
app.include_router(workers.router)
app.include_router(worker_times.router)
app.include_router(businesses.router)
app.include_router(sites.router)
app.include_router(fields.router)
app.include_router(fruit_types.router)
app.include_router(varieties.router)
app.include_router(variety_clones.router)
app.include_router(blocks.router)
app.include_router(rootstocks.router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}