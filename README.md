# SkyTracker

[<img src="https://img.shields.io/badge/github--blue?logo=github" alt="Github badge">](https://github.com/JasperJeuken/SkyTracker)
[<img src="https://img.shields.io/badge/documentation--blue?logo=readthedocs" alt="readthedocs badge">](https://skytracker.readthedocs.io/en/latest/)
[<img src="https://readthedocs.org/projects/skytracker/badge/" alt="readthedocs badge 2">](https://skytracker.readthedocs.io/en/latest/)

Tool for tracking and visualizing aircraft around the world

## Usage
Using the application requires setting up a [ClickHouse](https://clickhouse.com/) database, and acquiring [OpenSky Network API](https://openskynetwork.github.io/opensky-api/index.html)
credentials. 

Please follow the steps outlined on the [`Getting started`](https://skytracker.readthedocs.io/en/latest/getting_started.html) page of the documentation for installation and usage.

## Outline
The SkyTracker application includes several components:
- Collect aircraft states periodically from ADS-B data (via [OpenSky Network](https://opensky-network.org/))
- Store data in [ClickHouse](https://clickhouse.com/) server (local or cloud-based)
- Query database via FastAPI endpoints
- Serve webpages to visualize data

The package structure is modular and asynchronous. Collection services can run in parallel to other functionality.
Abstracted database management allows for expansion and future analyses.

## Current state
The application is still a work in progress. Currently, aircraft state collection is automated. Basic database interaction is implemented, allowing for interaction with a local or cloud-based ClickHouse server. Only `maps` query endpoints have been implemented, which allow for requesting a full batch of aircraft states (optionally within a bounding box), getting aircraft states near a point, and getting the state history of a specific aircraft.