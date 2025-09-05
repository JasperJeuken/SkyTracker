# SkyTracker

[<img src="https://img.shields.io/badge/github--blue?logo=github" alt="Github badge">](https://github.com/JasperJeuken/SkyTracker)
[<img src="https://img.shields.io/badge/documentation--blue?logo=readthedocs" alt="readthedocs badge">](https://skytracker.readthedocs.io/en/latest/)
[<img src="https://readthedocs.org/projects/skytracker/badge/" alt="readthedocs badge 2">](https://skytracker.readthedocs.io/en/latest/)

Tool for tracking and visualizing aircraft

## Installation
Clone the repository:
```
git clone https://github.com/JasperJeuken/SkyTracker
```

Then, install the package using [uv](https://docs.astral.sh/uv) (recommended):
```
uv sync
```

or install manually with:
```
pip install -e .
```

## Usage
Run the API server (with [uv](https://docs.astral.sh/uv)):
```
uv run fastapi dev skytracker/main.py
```

or without [uv](https://docs.astral.sh/uv):
```
fastapi dev skytracker/main.py
```

## Command-line utility
There is a command-line utility for retrieving aircraft data from the [OpenSky Network](https://opensky-network.org/) API. Running the utility requires OpenSky API credentials, which can be created by making an account [here](https://opensky-network.org/my-opensky/account). Collected data is written into HDF5 files.
```
uv run skytracker [options]
```

or without [uv](https://docs.astral.sh/uv):
```
skytracker [options]
```

Available options are:

| **Argument**                         | **Description**                                                               | **Default**           | **Example**                    |
|--------------------------------------|-------------------------------------------------------------------------------|-----------------------|--------------------------------|
| `--outdir <directory>` (alias `-o`)  | Specify path to output directory                                              | `output`              | `-o ./other/directory`         |
| `--filename <name>` (alias `-f`)     | Specify name of output file excluding extension (supports time format codes)  | `%Y%m%d`              | `-f %Y%m%d_data`               |
| `--credentials <path>` (alias `-c`)  | Specify path to OpenSky API credentials                                       | `credentials.json`    | `-c ./creds/file.txt`          |
| `--time <int>` (alias `-t`)          | Specify Unix timestamp to get states for (max. 30 mins ago)                   | `-` (now)          | `-t 173568600`                 |
| `--icao24 <code>`                    | Specify aircraft ICAO 24-bit (hex) address(es) to get states for              | `-` (all aircraft) | `--icao24 AC82EC`              |
| `--bbox <lat0> <lon0> <lat1> <lon1>` | Specify coordinate bounding box to get states in (min/max latitude/longitude) | `-` (worldwide)    | `--bbox 10.5 20.0 -50.5 -60.0` |
| `--repeat <seconds>` (alias `-r`)    | Specify number of seconds between repeated requests (`0`=once, min. 15 sec)   | `0` (once)            | `-r 100`                       |
