"""SkyTracker command line script"""
import argparse
import pathlib
import json
import time
import asyncio
from datetime import datetime

from skytracker.storage import Storage
from skytracker.services.opensky import OpenskyAPI


# TODO: remove (obsolete)


async def main() -> None:
    """Main async entrypoint for SkyTracker CLI"""

    # Create command-line argument parser
    parser = argparse.ArgumentParser(
        prog='SkyTracker',
        description='Track aircraft over the world',
        usage='skytracker.py [options]'
    )
    parser.add_argument_group('File settings', 'Change credentials and output file')
    parser.add_argument('-o', '--outdir', default='output', type=pathlib.Path,
                        help='Path to output directory (default: "output")')
    parser.add_argument('-f', '--filename', default='%Y%m%d', type=str,
                        help='Output filename, supports time formatting (default: "%%Y%%m%%d")')
    parser.add_argument('-c', '--credentials', default='credentials.json', type=pathlib.Path,
                        help='Path to credentials file (default: "credentials.json")')
    parser.add_argument_group('State parameters', 'Settings for state request')
    parser.add_argument('-t', '--time', default=None, type=int,
                        help='Unix timestamp for states to get, max. 30 min ago (default: now)')
    parser.add_argument('--icao24', default=None, nargs='*', type=str,
                        help='One or more ICAO 24 addresses to get for (default: none)')
    parser.add_argument('--bbox', default=None, nargs=4, type=float,
                        help='(lat0, lon0, lat1, lon1) bounding box to get (default: none)')
    parser.add_argument('-r', '--repeat', default=0, type=int,
                        help='Repeat request every X seconds, min. 15 sec, 0=once (default: 0)')
    args = parser.parse_args()
    if 0 < args.repeat < 15:
        raise ValueError('Repeat value must be at least 15 seconds, or 0 for one call...')

    # Start data manager
    with open(args.credentials, 'r', encoding='utf-8') as file:
        credentials = json.load(file)
    username, password = credentials['clickhouseUser'], credentials['clickhouseSecret']
    storage: Storage = Storage(username, password)
    await storage.connect()

    # Start Opensky API
    api = OpenskyAPI(credentials_file=args.credentials)

    # Start acquisition
    running = True
    while running:
        start_time = time.time()
        try:

            # Get states from API
            if args.repeat != 0:
                args.time = None  # use current time when repeating
            states = api.get_states(args.time, args.icao24, args.bbox)

            # Write states to data storage
            await storage['state'].insert_states(states)
            print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] inserted {len(states)} states')

        # Catch exception
        except Exception as exc:
            print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] error occurred:')
            print(exc)

        # Repeat or stop
        finally:
            if args.repeat == 0:
                running = False
                continue
            elapsed_time = time.time() - start_time
            sleep_time = min(max(0, args.repeat - elapsed_time), args.repeat)
            time.sleep(sleep_time)

    # Close manager
    await storage.close()


def cli() -> None:
    """Sync entrypoint for command-line script"""
    asyncio.run(main())


if __name__ == '__main__':
    cli()
