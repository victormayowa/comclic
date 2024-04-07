from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import patient, immunization, finance, auth_router
from app.database import init_db, get_mongo_uri, db
from fastapi.middleware.cors import CORSMiddleware

ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:80",
    "http://localhost:80",
]
@asynccontextmanager
async def lifecycle(app: FastAPI):
    """app lifecycle"""
    # logger.info('starting app')
    await db
    yield
    # logger.info('stopping app')


def create_app() -> FastAPI:
    """app factory function"""
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(auth_router.auth_router)
    app.include_router(patient.router)
    app.include_router(immunization.router)
    app.include_router(finance.router)

    @app.get("/api")
    async def root():
        return {"message": "Welcome to the COMCLIC API!"}

    return app

app = create_app()
