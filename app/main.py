from fastapi import FastAPI
from app.api.routes.ml import router as ml_router
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.google_oauth import router as google_router
from app.api.routes.connector import router as connector_router
from app.api.routes.reader import router as reader_router
from app.utils.logging import logger
from app.core.api_logs import APILoggingMiddleware
import os

app = FastAPI(title="datasaki API", version="1.0")

# Include routers
app.include_router(ml_router, prefix="/ml", tags=["Machine Learning"])
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(google_router, prefix="/auth", tags=["Google OAuth"])
app.include_router(connector_router, prefix="/connectors", tags=["Connectors"])
app.include_router(reader_router, prefix="/reader", tags=["Readers"])

app.add_middleware(APILoggingMiddleware)

@app.get("/")
def root():
    logger.info("Welcome to datasaki")
    return {"message": "Welcome to datasaki"}

if __name__ == "__main__":
    import uvicorn
    ssl_certfile = os.getenv("SSL_CERTFILE", "certs/ssl-cert.pem")
    ssl_keyfile = os.getenv("SSL_KEYFILE", "certs/ssl-key.pem")
    uvicorn.run(app, host="0.0.0.0", port=8000, ssl_certfile=ssl_certfile, ssl_keyfile=ssl_keyfile)


