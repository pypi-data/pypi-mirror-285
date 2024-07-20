from .rules import CoreWAF, CoreWAFMiddleware
from .headers import SecurityHeadersManager
from fastapi import FastAPI

class WAFMiddleware:
    def __init__(
        self,
        app: FastAPI,
        Option={},
        script_nonce=False,
        style_nonce=False,
        report_only=False,
        config_file_path="fastapi_security_middleware/config/settings.yml"
    ):
        self.app = app
        self.Option = Option
        self.script_nonce = script_nonce
        self.style_nonce = style_nonce
        self.report_only = report_only
        self.core_waf = CoreWAF(config_file_path)

        default_config = {
            'xframe': True,
            'cacheControl': True,
            'clearSiteData': True,
            'csp': None,
            'coep': None,
            'coop': None,
            'corp': None,
            'referrer': None,
            'hsts': None,
            'wshsts': None,
            'xcto': None,
            'xdns': None,
            'xdo': None,
            'xcdp': None,
            'xss': None
        }
        
        sec_headers_config = {key: self.Option.get(key, value) for key, value in default_config.items()}

        self.app.add_middleware(SecurityHeadersManager, config=sec_headers_config)

        self.app.add_middleware(CoreWAFMiddleware, core_waf=self.core_waf)
