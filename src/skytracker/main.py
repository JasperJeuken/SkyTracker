"""Main API (entrypoint)"""
from fastapi import FastAPI

from skytracker.api.v1 import aircraft, analysis, flights, maps, search


app = FastAPI(
    title='SkyTracker',
    description='Track flights in the sky',
    version='0.1'
)

app.include_router(aircraft.router, prefix='/api/v1')
app.include_router(analysis.router, prefix='/api/v1')
app.include_router(flights.router, prefix='/api/v1')
app.include_router(maps.router, prefix='/api/v1')
app.include_router(search.router, prefix='/api/v1')


@app.get('/')
async def root():
    return {'message': 'welcome'}
