import re
from typing import Dict
from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from .config.load import LoadConfig

class CoreWAF:
    def __init__(self, config_file_path: str) -> None:
        self.config_file_path = config_file_path
    
    async def _load_configuration(self) -> Dict:
        config_loader = LoadConfig(self.config_file_path)
        return await config_loader.load_config()

    async def check_exclusions(self, request: Request) -> bool:
        try:
            config = await self._load_configuration()
            excluded_paths = config.get('exclusions', [])
            request_path = str(request.url.path)
            
            if request_path in excluded_paths:
                logger.info(f"Request path {request_path} is excluded from checks")
                return True
            
            logger.debug(f"Request path {request_path} is not excluded")
            return False
        except Exception as e:
            logger.error(f"Error checking exclusions: {e}")
            raise e

    async def check_injection(self, body: bytes, url_path: str) -> bool:
        try:
            config = await self._load_configuration()
            if not config['rules']['injection']['enabled']:
                logger.info("Injection checks are not enabled")
                return False

            body_decoded = body.decode().lower()

            if await self._check_patterns(config, 'sql', body_decoded, url_path):
                return True
            if await self._check_patterns(config, 'xss', body_decoded, url_path):
                return True
            if await self._check_patterns(config, 'nosql', body_decoded, url_path):
                return True

            logger.debug("No injection patterns found in body")
            return False
        except Exception as e:
            logger.error(f"Error checking injection: {e}")
            raise e

    async def _check_patterns(self, config: Dict, injection_type: str, body_decoded: str, url_path: str) -> bool:
        if not config['rules']['injection'][injection_type]['enabled']:
            return False

        patterns = config['rules']['injection'][injection_type]['patterns']
        for pattern in patterns:
            if re.search(pattern, body_decoded) or re.search(pattern, url_path):
                logger.warning(f"{injection_type.upper()} injection pattern found in body: {pattern}")
                return True

        return False

class CoreWAFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, core_waf: CoreWAF) -> None:
        super().__init__(app)
        self.core_waf = core_waf

    async def dispatch(self, request: Request, call_next):
        if await self.core_waf.check_exclusions(request):
            return await call_next(request)

        body = await request.body()

        if await self.core_waf.check_injection(body, str(request.url.path)):
            return JSONResponse(status_code=400, content={"detail": "Injection pattern detected"})

        response = await call_next(request)
        return response