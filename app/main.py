from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.rbac import RBACMiddleware
from app.middleware.auth import AuthMiddleware
from app.api.routes import auth, connector, dataset, llm, reader
from app.core.config import settings
from app.db.database import engine, Base
from contextlib import asynccontextmanager
from app.utils.logging import logger
from app.core.api_logs import APILoggingMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    # Add any cleanup code here if needed

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
app.add_middleware(AuthMiddleware)

# Add RBAC middleware
app.add_middleware(RBACMiddleware)

app.add_middleware(APILoggingMiddleware)

# Include routers with proper prefixes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(connector.router, prefix="/api/v1/connectors", tags=["connectors"])
app.include_router(dataset.router, prefix="/api/v1/datasets", tags=["datasets"])
app.include_router(llm.router, prefix="/api/v1/llms", tags=["llms"])
app.include_router(reader.router, prefix="/api/v1/readers", tags=["readers"])

@app.get("/")
async def root():
    logger.info("Welcome to datasaki")
    return {"message": "Welcome to datasaki"}


