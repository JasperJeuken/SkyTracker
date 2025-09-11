"""Maps API endpoints"""
import time

from fastapi import APIRouter, Depends

from skytracker.dependencies import get_storage
from skytracker.storage import Storage

# from skytracker.models.maps import
# from skytracker.services.maps import


router = APIRouter(prefix='/maps', tags=['maps'])


@router.get('/')
async def get_latest_batch(storage: Storage = Depends(get_storage)):
    start = time.time()
    states = await storage['state'].get_latest_batch()
    elapsed = (time.time() - start) * 1e3
    return {'message': f'got {len(states)} states (took {elapsed} ms)'}
