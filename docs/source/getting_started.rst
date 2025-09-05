Getting started
===============

Installation
------------
To install SkyTracker, first clone the repository:

.. code-block::

   git clone https://github.com/JasperJeuken/SkyTracker

Next, use `uv <https://docs.astral.sh/uv>`_ to install the package:

.. code-block::

   uv sync

Alternatively, use pip to install:

.. code-block::

   pip install -e .

Usage
-----
Run the API server (using `uv <https://docs.astral.sh/uv>`_):

.. code-block::

    uv run fastapi dev skytracker/main.py

Alternatively, run without `uv <https://docs.astral.sh/uv>`_:

.. code-block::

    fastapi dev skytracker/main.py

Command-line utility
--------------------
There is a command-line utility for retrieving aircraft data from the `OpenSky Network API <https://opensky-network.org/>`_.
Running the utility requires OpenSky API credentials, which can be created by making an account `here <(https://opensky-network.org/my-opensky/account>`_.
Collected data is written into `HDF5 <https://github.com/HDFGroup/hdf5>`_ files.

.. code-block::

    uv run skytracker [options]

Alternatively, run without `uv <https://docs.astral.sh/uv>`_:

.. code-block::

    skytracker [options]

Available options are:

+--------------------------------------------------+-------------------------------------------------------------------------------------+----------------------------+--------------------------------------+
| **Argument**                                     | **Description**                                                                     | **Default**                | **Example**                          |
+==================================================+=====================================================================================+============================+======================================+
| :code:`--outdir <directory>` (alias :code:`-o`)  | Specify path to output directory                                                    | :code:`output`             | :code:`-o ./other/directory`         |
+--------------------------------------------------+-------------------------------------------------------------------------------------+----------------------------+--------------------------------------+
| :code:`--filename <name>` (alias :code:`-f`)     | Specify name of output file excluding extension (supports time format codes)        | :code:`%Y%m%d`             | :code:`-f %Y%m%d_data`               |
+--------------------------------------------------+-------------------------------------------------------------------------------------+----------------------------+--------------------------------------+
| :code:`--credentials <path>` (alias :code:`-c`)  | Specify path to OpenSky API credentials                                             | :code:`credentials.json`   | :code:`-c ./creds/file.txt`          |
+--------------------------------------------------+-------------------------------------------------------------------------------------+----------------------------+--------------------------------------+
| :code:`--time <int>` (alias :code:`-t`)          | Specify Unix timestamp to get states for (max. 30 mins ago)                         | :code:`N/A` (now)          | :code:`-t 173568600`                 |
+--------------------------------------------------+-------------------------------------------------------------------------------------+----------------------------+--------------------------------------+
| :code:`--icao24 <code>`                          | Specify aircraft ICAO 24-bit (hex) address(es) to get states for                    | :code:`N/A` (all aircraft) | :code:`--icao24 AC82EC`              |
+--------------------------------------------------+-------------------------------------------------------------------------------------+----------------------------+--------------------------------------+
| :code:`--bbox <lat0> <lon0> <lat1> <lon1>`       | Specify coordinate bounding box to get states in (min/max latitude/longitude)       | :code:`N/A` (worldwide)    | :code:`--bbox 10.5 20.0 -50.5 -60.0` |
+--------------------------------------------------+-------------------------------------------------------------------------------------+----------------------------+--------------------------------------+
| :code:`--repeat <seconds>` (alias :code:`-r`)    | Specify number of seconds between repeated requests (:code:`0`=once, min. 15 sec)   | :code:`0` (once)           | :code:`-r 100`                       |
+--------------------------------------------------+-------------------------------------------------------------------------------------+----------------------------+--------------------------------------+
