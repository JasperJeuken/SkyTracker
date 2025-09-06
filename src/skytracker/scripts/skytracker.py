"""SkyTracker command line script"""
from datetime import datetime
import argparse
import pathlib
import os
import time

from skytracker.scripts.opensky import OpenskyAPI


def main() -> None:
    """Main entrypoint for SkyTracker CLI"""

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

    api = OpenskyAPI(credentials_file=args.credentials)
    running = True
    while running:
        start_time = time.time()
        try:

            # Get states from API
            if args.repeat != 0:
                args.time = None  # use current time when repeating
            states = api.get_states(args.time, args.icao24, args.bbox)

            # Write to output
            filename = f'{datetime.now().strftime(args.filename)}.h5'
            out_file = args.outdir / pathlib.Path(filename)
            os.makedirs(args.outdir, exist_ok=True)
            states.to_hdf5(out_file)

            # Print outcome
            print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] ' + \
                f'wrote {len(states)} states to "{out_file}".')

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


if __name__ == '__main__':
    main()
