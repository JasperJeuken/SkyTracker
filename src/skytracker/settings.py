"""API configuration"""
from pydantic.fields import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings
    
    Attributes:
        clickhouse_host (str): hostname of ClickHouse server (default="localhost")
        clickhouse_port (int): port of ClickHouse server (default=8123)
        clickhouse_user (str): username to access ClickHouse server with
        clickhouse_password (str): password to access ClickHouse server with
        clickhouse_database (str): name of ClickHouse database to use
        opensky_client_id (str): client ID to access OpenSky Network API with
        opensky_client_secret (str): client secret to access OpenSky Network API with
        app_name (str): name of FastAPI application
        environment (str): FastAPI environment (development, staging, or production)
        debug (bool): whether to run in debug mode
    """
    # ClickHouse
    clickhouse_host: str = Field('localhost')
    clickhouse_port: int = Field(8123)
    clickhouse_user: str = Field('default')
    clickhouse_password: str = Field('')
    clickhouse_database: str = Field('default')
    clickhouse_secure: bool = Field(False)

    # OpenSky
    opensky_client_id: str = Field('')
    opensky_client_secret: str = Field('')

    # FastAPI
    app_name: str = Field('SkyTracker')
    environment: str = Field('development')
    debug: bool = Field(True)

    # Load environment variables
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings: Settings = Settings()
