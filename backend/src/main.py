from fastapi import FastAPI
from src.web.routers import healthcheck_router
from src.web.routers import protocols_router
from src.web.routers import experiment_router

app = FastAPI(title="Protocol Copilot API")

# All routes go under /api
app.include_router(healthcheck_router.router, prefix="/api")
app.include_router(protocols_router.router, prefix="/api")
app.include_router(experiment_router.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to Protocol Copilot API"}
