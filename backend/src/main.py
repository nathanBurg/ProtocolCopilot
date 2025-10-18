from fastapi import FastAPI
from src.web.routers import healthcheck_router

app = FastAPI(title="Protocol Copilot API")

# All routes go under /api
app.include_router(healthcheck_router.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to Protocol Copilot API"}
