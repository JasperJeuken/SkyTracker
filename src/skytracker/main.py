"""Main API (entrypoint)"""
from contextlib import asynccontextmanager
import asyncio
from asyncio.tasks import Task
from typing import AsyncGenerator

from fastapi import FastAPI

from skytracker.api.v1 import aircraft, analysis, flights, maps, search
from skytracker import dependencies
from skytracker.storage import Storage
from skytracker.services.opensky import collect_service
from skytracker.config import get_credentials


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan asynchronous context manager

    Args:
        app (FastAPI): FastAPI application instance

    Returns:
        AsyncGenerator[None, None]: async generator (no data)
    """
    # Initialize database connection
    credentials = get_credentials()
    dependencies.storage = Storage(username=credentials['clickhouseUser'],
                                   password=credentials['clickhouseSecret'])
    await dependencies.storage.connect()

    # Start background services
    tasks: list[Task] = []
    tasks.append(asyncio.create_task(collect_service(dependencies.storage, repeat=90)))

    # Run FastAPI application
    yield

    # Shut down background services
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    # Close database connection
    await dependencies.storage.close()
    dependencies.storage = None


app = FastAPI(
    title='SkyTracker',
    description='Track flights in the sky',
    version='0.1',
    lifespan=lifespan
)

app.include_router(aircraft.router, prefix='/api/v1')
app.include_router(analysis.router, prefix='/api/v1')
app.include_router(flights.router, prefix='/api/v1')
app.include_router(maps.router, prefix='/api/v1')
app.include_router(search.router, prefix='/api/v1')


@app.get('/')
async def root():
    """Root message"""
    return {'message': 'welcome'}
