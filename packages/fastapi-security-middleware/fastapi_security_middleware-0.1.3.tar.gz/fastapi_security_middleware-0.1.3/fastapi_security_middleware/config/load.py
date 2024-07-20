"""load configs"""
import asyncio
import httpx
from loguru import logger
from yaml import safe_load


class LoadConfig:
    """Class to load configuration from a YAML file or an external endpoint."""

    def __init__(self, file_path: str = None, endpoint: str = None) -> None:
        self.file_path = file_path
        self.endpoint = endpoint
        self.config = None
        logger.debug(
            f"LoadConf initialized with file path: {self.file_path} and endpoint: {self.endpoint}")

    async def load_config(self) -> dict:
        """Load configuration from the YAML file or an external endpoint."""
        if self.file_path:
            return self.load_from_file()
        elif self.endpoint:
            return await self.fetch_from_endpoint()
        else:
            logger.error("No file path or endpoint provided for configuration.")
            raise ValueError("A file path or endpoint must be provided.")

    def load_from_file(self) -> dict:
        """Load configuration from the YAML file."""
        try:
            with open(self.file_path, 'r', encoding="utf-8") as file:
                config = safe_load(file.read())
                logger.info("Configuration loaded successfully from file.")
                return config
        except Exception as e:
            logger.error(f"Failed to load configuration from file: {e}")
            raise e

    async def fetch_from_endpoint(self) -> dict:
        """Fetch configuration from an external endpoint."""
        async with httpx.AsyncClient() as client:
            response = await client.get(self.endpoint)
            self.config = response.json()
            logger.info("Configuration fetched successfully from endpoint.")
            return self.config

    def update_waf_config(self):
        """Update the WAF configuration."""
        pass

    async def schedule_config_updates(self, interval: int = 60):
        """Schedule configuration updates at a set interval."""
        while True:
            if self.endpoint:
                await self.fetch_from_endpoint()
                self.update_waf_config()
            await asyncio.sleep(interval)
