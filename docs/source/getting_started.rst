Getting started
===============

Setting up the SkyTracker application requires several steps to ensure external APIs and the 
database server function correctly. On this page, the required steps are detailed:

1. Install the SkyTracker package (`Installation <#installation>`__)
2. Set up ClickHouse database server (`ClickHouse server <#clickhouse-server>`__)
3. Get OpenSky Network API credentials (`OpenSky Network API credentials <#opensky-network-api-credentials>`__)
4. Set up environment variables (`Environment variables <#environment-variables>`__)

------------
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

-----------------
ClickHouse server
-----------------

SkyTracker uses ClickHouse to store data in a database. There are several options for setting this
up:

- `ClickHouse cloud <#clickhouse-cloud>`__
- `Local Docker container <#local-docker-container>`__

After setting up a cloud or local server, create a :code:`.env` file in the root of the repository
by following the instructions in `Environment variables <#environment-variables>`__.

ClickHouse cloud
----------------

Use the following steps to set up a ClickHouse cloud database which hosts the server in the cloud. 
Note that after a 30-day trial period, a plan needs to be selected 
(see `ClickHouse pricing <https://clickhouse.com/pricing>`_).

1. Go to the `ClickHouse website <https://clickhouse.com/>`_ and click :code:`Get started`.

2. Sign in or create an account.

3. Configure a service (select a provider and region).

4. In the ClickHouse console, click :code:`Connect`, and copy the username and password (reset it 
   if you did not make one yet), as well as the host URL.

5. Follow the instructions under `Environment variables <#environment-variables>`__ to set up the 
   environment variables.

Local Docker container
----------------------

Use the following steps to set up a `Docker <https://www.docker.com/>`_ container which hosts this
server locally:

1. Pull latest ClickHouse server container

    .. code-block:: pwsh

        docker pull clickhouse/clickhouse-server

2. Create an XML file to specify user priviliges. Any filename is acceptable. The path to the file 
   is needed later. Add the following file content:

    .. code-block:: xml
        
        <yandex>
            <users>
                <default>
                    <access_management>1</access_management>
                    <named_collection_control>1</named_collection_control>
                    <show_named_collections>1</show_named_collections>
                    <show_named_collections_secrets>1</show_named_collections>
                </default>
            </users>
        </yandex>

3. Run a new server with specific settings, including the XML file created in step 2. The name of 
   the server can be adjusted. Use the following command:

    .. code-block:: pwsh

        docker run -d --name my-server-name --ulimit nofile=262144:262144 -v "$PWD/path/to/created.xml:/etc/clickhouse-server/users.d/default-user-access.xml" -v "clickhouse_data:/var/lib/clickhouse/" -v "clickhouse_logs:/var/log/clickhouse-server" -p 8123:8123 -p 9000:9000 clickhouse/clickhouse-server

4. Enter the native client from the console (use the same server name as specified in step 3):

    .. code-block:: pwsh

        docker exec -it my-server-name clickhouse-client

5. Create a new user (select username and password):

    .. code-block:: sql

        CREATE USER myusername IDENTIFIED BY 'mypassword';

6. Grant the new user access to all commands:

    .. code-block:: sql

        GRANT ALL ON *.* TO myusername;

7. Exit the native client:

    .. code-block:: sql

        quit

8. Follow the instructions under `Environment variables <#environment-variables>`__ to set up the 
   environment variables.

-------------------------------
OpenSky Network API credentials
-------------------------------

The SkyTracker application pulls data from the `OpenSky Network API <https://openskynetwork.github.io/opensky-api/>`_.
This requires API credentials, which can be obtained from the website:

1. Create an account on the `OpenSky Network <https://opensky-network.org/>`_ website.

2. On your account page, copy the :code:`client ID` and :code:`client secret`.

3. Follow the instructions under `Environment variables <#environment-variables>`__ to set up the 
   environment variables.

Please note that the API comes with several limitations, as outlined on the page
`REST API <https://openskynetwork.github.io/opensky-api/rest.html#limitations>`_. Notably, users 
receive a set amount of credits, which are spent based on the performed requests (see 
`API credit usage <https://openskynetwork.github.io/opensky-api/rest.html#api-credit-usage>`_). For
a regular user, if requesting the states of all aircraft, this amounts to roughly one request every 
minute and a half.

---------------------
Environment variables
---------------------

The SkyTracker application uses environment variables to change settings within the program. Use 
these steps to set them up correctly:

1. Create the file :code:`.env` in the root directory.

2. Add the following content to the file:

    .. code-block:: basemake

        CLICKHOUSE_HOST=hostname        # localhost or URL to cloud server
        CLICKHOUSE_PORT=0               # server port (0 = use default)
        CLICKHOUSE_USER=myusername      # name of user on server
        CLICKHOUSE_PASSWORD=mypassword  # password of user on server
        CLICKHOUSE_SECURE=False         # typically False for local server, True for cloud server
        CLICKHOUSE_DATABASE=default     # name of database to use on server (typically "default")

        OPENSKY_CLIENT_ID=client-id          # OpenSky Network API client ID
        OPENSKY_CLIENT_SECRET=client-secret  # OpenSky Network API client secret

        APP_NAME=SkyTracker      # Name of application in FastAPI
        ENVIRONMENT=development  # FastAPI environment mode (development, staging, or production)
        DEBUG=True               # Whether to start in debug mode

-----
Usage
-----
Run the API server (using `uv <https://docs.astral.sh/uv>`_):

.. code-block::

    uv run fastapi dev skytracker/main.py

Alternatively, run without `uv <https://docs.astral.sh/uv>`_:

.. code-block::

    fastapi dev skytracker/main.py

.. --------------------
.. Command-line utility
.. --------------------
.. There is a command-line utility for retrieving aircraft data from the `OpenSky Network API <https://opensky-network.org/>`_.
.. Running the utility requires OpenSky API credentials, which can be created by making an account `here <(https://opensky-network.org/my-opensky/account>`_.
.. Collected data is written into `HDF5 <https://github.com/HDFGroup/hdf5>`_ files.

.. .. code-block::

..     uv run skytracker [options]

.. Alternatively, run without `uv <https://docs.astral.sh/uv>`_:

.. .. code-block::

..     skytracker [options]

.. Available options are:

.. +--------------------------------------------------+-------------------------------------------------------------------------------------+----------------------------+--------------------------------------+
.. | **Argument**                                     | **Description**                                                                     | **Default**                | **Example**                          |
.. +==================================================+=====================================================================================+============================+======================================+
.. | :code:`--outdir <directory>` (alias :code:`-o`)  | Specify path to output directory                                                    | :code:`output`             | :code:`-o ./other/directory`         |
.. +--------------------------------------------------+-------------------------------------------------------------------------------------+----------------------------+--------------------------------------+
.. | :code:`--filename <name>` (alias :code:`-f`)     | Specify name of output file excluding extension (supports time format codes)        | :code:`%Y%m%d`             | :code:`-f %Y%m%d_data`               |
.. +--------------------------------------------------+-------------------------------------------------------------------------------------+----------------------------+--------------------------------------+
.. | :code:`--credentials <path>` (alias :code:`-c`)  | Specify path to OpenSky API credentials                                             | :code:`credentials.json`   | :code:`-c ./creds/file.txt`          |
.. +--------------------------------------------------+-------------------------------------------------------------------------------------+----------------------------+--------------------------------------+
.. | :code:`--time <int>` (alias :code:`-t`)          | Specify Unix timestamp to get states for (max. 30 mins ago)                         | :code:`N/A` (now)          | :code:`-t 173568600`                 |
.. +--------------------------------------------------+-------------------------------------------------------------------------------------+----------------------------+--------------------------------------+
.. | :code:`--icao24 <code>`                          | Specify aircraft ICAO 24-bit (hex) address(es) to get states for                    | :code:`N/A` (all aircraft) | :code:`--icao24 AC82EC`              |
.. +--------------------------------------------------+-------------------------------------------------------------------------------------+----------------------------+--------------------------------------+
.. | :code:`--bbox <lat0> <lon0> <lat1> <lon1>`       | Specify coordinate bounding box to get states in (min/max latitude/longitude)       | :code:`N/A` (worldwide)    | :code:`--bbox 10.5 20.0 -50.5 -60.0` |
.. +--------------------------------------------------+-------------------------------------------------------------------------------------+----------------------------+--------------------------------------+
.. | :code:`--repeat <seconds>` (alias :code:`-r`)    | Specify number of seconds between repeated requests (:code:`0`=once, min. 15 sec)   | :code:`0` (once)           | :code:`-r 100`                       |
.. +--------------------------------------------------+-------------------------------------------------------------------------------------+----------------------------+--------------------------------------+
