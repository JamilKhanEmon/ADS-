from fastapi import FastAPI
from routers import farms, crops_markets

app = FastAPI(
    title="Agriculture DB API",
    description="Farm Performance & Crop Market Intelligence Reports",
    version="1.0.0",
)

app.include_router(farms.router)
app.include_router(crops_markets.router)


@app.get("/", tags=["Health"])
@app.head("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Agriculture API is running!"}


@app.get("/health", tags=["Health"])
@app.head("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
