"""Data storage manager"""
from typing import Any, Sequence, Literal
from asyncio import Lock

import clickhouse_connect
from clickhouse_connect.driver.asyncclient import AsyncClient

from skytracker.utils import logger, log_and_raise


class DatabaseManager:
    """Generic async database manager for ClickHouse
    
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

            docker run -d --name my-server-name --ulimit nofile=262144:262144 -v "$PWD/path/to/crea\
                ted.xml:/etc/clickhouse-server/users.d/default-user-access.xml" -v "clickhouse_data\
                    :/var/lib/clickhouse/" -v "clickhouse_logs:/var/log/clickhouse-server" -p 8123:\
                        8123 -p 9000:9000 clickhouse/clickhouse-server
    
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
    
    """

    def __init__(self, username: str, password: str,
                 host: str = 'localhost', port: int = 8123, database: str = '__default__',
                 secure: bool = False) -> None:
        """Initialize data manager by storing ClickHouse connection settings

        Args:
            username (str): server username
            password (str): server password
            host (str, optional): server host. Defaults to 'localhost'.
            port (int, optional): server port. Defaults to 8123.
            database (str, optional): server database name. Defaults to '__default__'.
            secure (bool, optional): whether to use secure connection. Defaults to False.
        """
        self.client_settings: dict[Literal['username', 'password', 'host',
                                           'port', 'database', 'secure'], int | str] = {
            'username': username,
            'password': password,
            'host': host,
            'port': port,
            'database': database,
            'secure': secure
        }
        self.client: AsyncClient = None
        self._connected: bool = False
        self._lock: Lock = Lock()

    async def connect(self) -> None:
        """Connect to the ClickHouse server"""
        if await self.is_connected():
            return
        logger.info('Connecting ClickHouse manager ' + \
                    f'({self.client_settings["host"]}:{self.client_settings["port"]})...')
        self.client = await clickhouse_connect.get_async_client(**self.client_settings)
        await self.set_connected()
        logger.info('Connected ClickHouse manager')

    async def close(self) -> None:
        """Close client connection"""
        if not await self.is_connected():
            return
        logger.info('Disconnecting ClickHouse manager...')
        await self.client.close()
        await self.set_disconnected()
        logger.info('Disconnected ClickHouse manager')

    async def is_connected(self) -> bool:
        """Check if the client is connected to the ClickHouse databse

        Returns:
            bool: whether the client is connected to the ClickHouse database
        """
        async with self._lock:
            return self._connected

    async def set_connected(self, new_connected: bool = True) -> None:
        """Set a new connection status for the database manager

        Args:
            new_connected (bool, optional): new connection status. Defaults to True.
        """
        async with self._lock:
            self._connected = new_connected

    async def set_disconnected(self) -> None:
        """Set the database connection status to False"""
        await self.set_connected(False)

    async def table_exists(self, name: str) -> bool:
        """Check if a specific table exists

        Args:
            name (str): name of table to find

        Returns:
            bool: whether specified table exists
        """
        await self.connect()
        return await self.client.command(f'EXISTS TABLE {name}') == 1

    async def create_table(self, name: str, columns: list[str], *args: str) -> None:
        """Create a table in the server

        Args:
            name (str): name of table to create
            columns (list[str]): column names and data types in SQL format (i.e. "time UInt32")
            args (str): additional SQL statements for CREATE TABLE command
        """
        await self.connect()
        command = f'CREATE TABLE {name} ({", ".join(columns)})'
        if args:
            command += ' ' + ' '.join(args)
        command += ';'
        logger.debug(f'Creating table "{name}" with {len(columns)} columns...')
        await self.client.command(command)

    async def drop_table(self, name: str) -> None:
        """Drop a table

        Args:
            name (str): name of table to drop
        """
        await self.connect()
        logger.info(f'Dropping table {name}...')
        await self.client.command(f'DROP TABLE {name};')

    async def insert(self, name: str, rows: Sequence[Sequence[Any]],
                     column_names: list[str]) -> None:
        """Insert new rows into a table

        Args:
            name (str): name of table to insert rows in
            rows (Sequence[Sequence[Any]]): list of new rows
            column_names (list[str]): names of columns corresponding to row values
        """
        await self.connect()
        logger.info(f'Inserting {len(rows)} rows into "{name}"...')
        await self.client.insert(name, rows, column_names)

    async def sql_query(self, sql_query: str) -> Sequence[Sequence[Any]]:
        """Perform an SQL query

        Args:
            sql_query (str): SQL query

        Returns:
            Sequence[Sequence[Any]]: list of matching rows
        """
        await self.connect()
        if not isinstance(sql_query, str) or len(sql_query) == 0:
            log_and_raise(ValueError, f'Invalid SQL query ({sql_query})')
        if not sql_query.endswith(';'):
            sql_query += ';'
        logger.debug(f'Running SQL query ({sql_query})')
        result = await self.client.query(sql_query)
        return result.result_rows
