"""SkyTracker command line script"""
import argparse
import asyncio

from skytracker.storage import Storage
from skytracker.services.api.api import collection_service
from skytracker.settings import settings


# TODO: remove (obsolete)


async def main() -> None:
    """Main async entrypoint for SkyTracker CLI"""

    # Create command-line argument parser
    parser = argparse.ArgumentParser(
        prog='SkyTracker',
        description='Track aircraft over the world',
        usage='skytracker.py [options]'
    )
    parser.add_argument('-r', '--repeat', default=90, type=int,
                        help='Repeat request every X seconds (default: 90)')
    args = parser.parse_args()
    if 0 < args.repeat < 15:
        raise ValueError('Repeat value must be at least 15 seconds, or 0 for one call...')

    # Open database connection
    storage = Storage(settings.clickhouse_user, settings.clickhouse_password,
                      settings.clickhouse_host, settings.clickhouse_port,
                      settings.clickhouse_database, settings.clickhouse_secure)
    await storage.connect()
    
    # Run service until interrupted or completion
    try:
        await collection_service(storage, repeat=args.repeat)
    except KeyboardInterrupt:
        pass

    # Close database connection
    await storage.close()


def cli() -> None:
    """Sync entrypoint for command-line script"""
    asyncio.run(main())


if __name__ == '__main__':
    cli()
