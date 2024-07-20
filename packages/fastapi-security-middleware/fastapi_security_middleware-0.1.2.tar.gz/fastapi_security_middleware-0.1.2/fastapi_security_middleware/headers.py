from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.responses import Response
from fastapi import Request
from typing import Callable, List, Dict

class ContentSecurityPolicyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, policy: str):
        super().__init__(app)
        self.policy = policy

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers['Content-Security-Policy'] = self.policy
        return response

class CrossOriginEmbedderPolicyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, policy: str):
        super().__init__(app)
        self.policy = policy

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers['Cross-Origin-Embedder-Policy'] = self.policy
        return response

class CrossOriginOpenerPolicyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, policy: str):
        super().__init__(app)
        self.policy = policy

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers['Cross-Origin-Opener-Policy'] = self.policy
        return response

class CrossOriginResourcePolicyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, policy: str):
        super().__init__(app)
        self.policy = policy

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers['Cross-Origin-Resource-Policy'] = self.policy
        return response

class ReferrerPolicyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, policy: str):
        super().__init__(app)
        self.policy = policy

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers['Referrer-Policy'] = self.policy
        return response

class StrictTransportSecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, policy: str):
        super().__init__(app)
        self.policy = policy

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers['Strict-Transport-Security'] = self.policy
        return response

class XContentTypeOptionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

class XDNSPrefetchControlMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, policy: str):
        super().__init__(app)
        self.policy = policy

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers['X-DNS-Prefetch-Control'] = self.policy
        return response

class XDownloadOptionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers['X-Download-Options'] = 'noopen'
        return response

class XPermittedCrossDomainPoliciesMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, policy: str):
        super().__init__(app)
        self.policy = policy

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers['X-Permitted-Cross-Domain-Policies'] = self.policy
        return response

class XXSSProtectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers['X-XSS-Protection'] = '0'
        return response

class SecurityHeadersManager(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, config: Dict[str, str]):
        self.config = config or {}
        self.middlewares = self.get_middlewares(app)
        super().__init__(app)

    def get_middlewares(self, app: ASGIApp) -> List[BaseHTTPMiddleware]:
        middlewares = [
            ContentSecurityPolicyMiddleware(app, policy=self.config.get('Content-Security-Policy', "default-src 'self'")),
            CrossOriginEmbedderPolicyMiddleware(app, policy=self.config.get('Cross-Origin-Embedder-Policy', 'require-corp')),
            CrossOriginOpenerPolicyMiddleware(app, policy=self.config.get('Cross-Origin-Opener-Policy', 'same-origin')),
            CrossOriginResourcePolicyMiddleware(app, policy=self.config.get('Cross-Origin-Resource-Policy', 'same-site')),
            ReferrerPolicyMiddleware(app, policy=self.config.get('Referrer-Policy', 'strict-origin-when-cross-origin')),
            StrictTransportSecurityMiddleware(app, policy=self.config.get('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')),
            XContentTypeOptionsMiddleware(app),
            XDNSPrefetchControlMiddleware(app, policy=self.config.get('X-DNS-Prefetch-Control', 'off')),
            XDownloadOptionsMiddleware(app),
            XPermittedCrossDomainPoliciesMiddleware(app, policy=self.config.get('X-Permitted-Cross-Domain-Policies', 'none')),
            XXSSProtectionMiddleware(app),
        ]
        return middlewares

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        for middleware in self.middlewares:
            call_next = self.wrap_call_next(middleware, call_next)
        return await call_next(request)

    def wrap_call_next(self, middleware: BaseHTTPMiddleware, call_next: Callable) -> Callable:
        async def new_call_next(request: Request) -> Response:
            response = await middleware.dispatch(request, call_next)
            return response
        return new_call_next