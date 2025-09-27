"""Main API (entrypoint)"""
from contextlib import asynccontextmanager
import asyncio
import sys
from asyncio.tasks import Task
from typing import AsyncGenerator

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from skytracker import dependencies
from skytracker.api.v1 import aircraft, analysis, flights, maps, search
from skytracker.storage import Storage
from skytracker.services.browser import WebBrowser
from skytracker.services.opensky import opensky_service
from skytracker.utils import logger
from skytracker.settings import settings


# Set asyncio to use Windows event loop policy
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


origins = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:4173',
    'http://127.0.0.1:4173'
]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan asynchronous context manager

    Args:
        _ (FastAPI): FastAPI application instance

    Returns:
        AsyncGenerator[None, None]: async generator (no data)
    """
    logger.debug('Starting application lifespan...')

    # Initialize database connection
    dependencies.storage = Storage(username=settings.clickhouse_user,
                                   password=settings.clickhouse_password,
                                   host=settings.clickhouse_host,
                                   port=settings.clickhouse_port,
                                   database=settings.clickhouse_database,
                                   secure=settings.clickhouse_secure)
    await dependencies.storage.connect()
    logger.debug('Connected to database.')

    # Initialize web browser
    dependencies.browser = WebBrowser()
    await dependencies.browser.start()
    logger.debug('Opened web browser.')

    # Start background services
    tasks: list[Task] = []
    # tasks.append(asyncio.create_task(opensky_service(dependencies.storage, repeat=90)))
    logger.debug(f'Started {len(tasks)} services.')

    # Run FastAPI application
    logger.debug('Starting FastAPI application...')
    yield

    # Shut down background services
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    logger.debug('Cancelled all tasks.')

    # Close database connection
    await dependencies.storage.close()
    dependencies.storage = None
    logger.debug('Closed database connection.')

    # Close web browser
    await dependencies.browser.stop()
    dependencies.browser = None
    logger.debug('Closed web browser')

    logger.debug('Application lifespan ended.')


app = FastAPI(
    title='SkyTracker',
    description='Track flights in the sky',
    version='0.1',
    lifespan=lifespan
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True,
                   allow_methods=['*'], allow_headers=['*'])

app.include_router(aircraft.router, prefix='/api/v1')
app.include_router(analysis.router, prefix='/api/v1')
app.include_router(flights.router, prefix='/api/v1')
app.include_router(maps.router, prefix='/api/v1')
app.include_router(search.router, prefix='/api/v1')
