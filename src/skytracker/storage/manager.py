"""Data storage manager"""
import json

import clickhouse_connect
from clickhouse_connect.driver.asyncclient import AsyncClient


class AsyncObject(object):
    """Parent object for async classes"""

    async def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        await instance.__init__(*args, **kwargs)
        return instance
    
    async def __init__(self):
        pass


class DataManager(AsyncObject):
    """Data manager
    
    Requires Docker container with ClickHouse server, which can be set up locally. To set up a
    local ClickHouse server, follow these steps (assumes Docker is installed):

    1. Pull latest ClickHouse server container

        .. code:: pwsh

            docker pull clickhouse/clickhouse-server
    
    2. Create an XML file to specify user privileges. Any filename is possible, as long as extension
       is ``.xml``. The path to the file is necessary later. Add the following content:

        .. code:: xml

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
        
    3. Run a new server with specific mounts and network settings. The following command runs a
       container with the created XML file. It mounts a ``data`` and ``logs``, which will be located
       in a directory ``clickhouse`` in the directory where the command is executed.

        .. code:: pwsh

            docker run -d --name my-server-name --ulimit nofile=262144:262144 -v "$PWD/path/to/created.xml:/etc/clickhouse-server/users.d/default-user-access.xml" -v "$PWD/clickhouse/data:/var/lib/clickhouse/" -v "$PWD/clickhouse/logs:/var/log/clickhouse-server" -p 8123:8123 -p 9000:9000 clickhouse/clickhouse-server
    
    4. Enter the native client:

        .. code:: pwsh

            docker exec -it my-server-name clickhouse-client

    5. Create a new user with a specified password:

        .. code:: sql

            CREATE USER myusername IDENTIFIED BY 'mypassword';
    
    6. Grant the new user access to all commands:

        .. code:: sql

            GRANT ALL ON *.* TO myusername;

    7. Exit the native client:

        .. code:: sql

            quit
    
    8. Test connection using curl:

        .. code:: pwsh

            curl http://localhost:8123/ping


    Attributes:
        STATE_TABLE_NAME (str): name of aircraft state table
    """
    STATE_TABLE_NAME: str = 'aircraft_states'

    async def __init__(self, username: str, password: str,
                 host: str = 'localhost', port: int = 8123) -> None:
        """Initialize data manager by connecting to ClickHouse server and ensuring table exists

        Args:
            username (str): server username
            password (str): server password
            host (str, optional): server host. Defaults to 'localhost'.
            port (int, optional): server port. Defaults to 8123.
        """
        self.client: AsyncClient = await clickhouse_connect.get_async_client(username=username,
                                                                             password=password,
                                                                             host=host,
                                                                             port=port)
        await self.create_state_table()
        
    async def table_exists(self, name: str) -> bool:
        """Query if a specific table exists in the server

        Args:
            name (str): name of table to find

        Returns:
            bool: whether specified table exists
        """
        return await self.client.command(f'EXISTS TABLE {name}') == 1
    
    async def _create_table(self, name: str, columns: list[str], *args: str) -> None:
        """Create a table in the server

        Args:
            name (str): name of table
            columns (list[str]): column names and data types in SQL format
            args (str): additional SQL statements for CREATE TABLE command
        """
        # Format command
        command = f'CREATE TABLE {name} ('
        command += ', '.join(columns) + ')'
        if args:
            command += ' ' + ' '.join(args)
        command += ';'

        # Execute command
        await self.client.command(command)
    
    async def _drop_table(self, name: str) -> None:
        """Drop a table in the server

        Args:
            name (str): name of table
        """
        command = f'DROP TABLE {name};'
        await self.client.command(command)
    
    async def create_state_table(self) -> None:
        """Create aircraft state table in server (if it does not exist already)"""
        # Skip if table already exists
        if await self.table_exists(self.STATE_TABLE_NAME):
            return
        
        # Fields for state table
        fields = [
            "time DateTime64(3, 'UTC') NOT NULL",
            'icao24 FixedString(6) NOT NULL',
            'callsign Nullable(String)',
            'origin_country String NOT NULL',
            "time_position Nullable(DateTime64(3, 'UTC'))",
            "last_contact DateTime64(3, 'UTC') NOT NULL",
            'longitude Nullable(Float64)',
            'latitude Nullable(Float64)',
            'baro_altitude Nullable(Float64)',
            'on_ground Bool NOT NULL',
            'velocity Nullable(Float64)',
            'true_track Nullable(Float64)',
            'vertical_rate Nullable(Float64)',
            'sensors Array(UInt32)',
            'geo_altitude Nullable(Float64)',
            'squawk Nullable(String)',
            'spi Bool NOT NULL',
            'position_source UInt8 NOT NULL',
            'category UInt8 NOT NULL'
        ]

        # Create table
        await self._create_table(self.STATE_TABLE_NAME, fields, 'ENGINE MergeTree',
                                 'PARTITION BY toDate(time)', 'ORDER BY (icao24, time)',
                                 'SETTINGS index_granularity=8192')

    async def close(self) -> None:
        """Close client connection"""
        await self.client.close()


if __name__ == '__main__':
    async def _main():
        # Get credentials
        with open('credentials.json', 'r', encoding='utf-8') as file:
            credentials = json.load(file)
        username, password = credentials['clickhouseUser'], credentials['clickhouseSecret']

        # Create manager
        manager = await DataManager(username, password)
        print(await manager.table_exists(manager.STATE_TABLE_NAME))
        await manager.create_state_table()
        print(await manager.table_exists(manager.STATE_TABLE_NAME))
        await manager.close()
    
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass
