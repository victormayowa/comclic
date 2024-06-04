from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.settings import settings
from app.routers import patient, immunization, finance, auth_router
from app.database import init_db #get_mongo_uri, db
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
    await init_db(settings.DATABASE_URL)
    yield
    # logger.info('stopping app')


def create_app() -> FastAPI:
    """app factory function"""
    app = FastAPI(
        title="Comclic API",
        lifespan=lifecycle,
    )

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
if __name__ == "__main__":
    import uvicorn
    # uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
