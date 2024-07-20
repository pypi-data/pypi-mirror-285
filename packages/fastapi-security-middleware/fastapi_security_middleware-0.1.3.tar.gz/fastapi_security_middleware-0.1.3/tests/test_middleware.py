import pytest
import sys
from pathlib import Path

diretorio_raiz = str(Path(__file__).resolve().parent.parent)
if diretorio_raiz not in sys.path:
    sys.path.append(diretorio_raiz)

from ..fastapi_security_middleware.middleware import WAFMiddleware

from fastapi.testclient import TestClient
from fastapi import FastAPI

app = FastAPI()
WAFMiddleware(app)

client = TestClient(app)

def test_root_path():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

def test_excluded_path(monkeypatch):
    async def mock_check_exclusions(self, request):
        return True

    monkeypatch.setattr("app.rules.CoreWAF.check_exclusions", mock_check_exclusions)

    response = client.get("/some-excluded-path")
    assert response.status_code == 200

def test_injection_detected(monkeypatch):
    async def mock_check_exclusions(self, request):
        return False

    async def mock_check_injection(self, body, url_path):
        return True

    monkeypatch.setattr("app.rules.CoreWAF.check_exclusions", mock_check_exclusions)
    monkeypatch.setattr("app.rules.CoreWAF.check_injection", mock_check_injection)

    response = client.post("/", json={"key": "value"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Injection pattern detected"}

def test_injection_not_detected(monkeypatch):
    async def mock_check_exclusions(self, request):
        return False

    async def mock_check_injection(self, body, url_path):
        return False

    monkeypatch.setattr("app.rules.CoreWAF.check_exclusions", mock_check_exclusions)
    monkeypatch.setattr("app.rules.CoreWAF.check_injection", mock_check_injection)

    response = client.post("/", json={"key": "value"})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

def test_security_headers():
    response = client.get("/")
    assert response.status_code == 200
    assert "X-Frame-Options" in response.headers
    assert "Cache-Control" in response.headers
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Cache-Control"] == "no-store"
