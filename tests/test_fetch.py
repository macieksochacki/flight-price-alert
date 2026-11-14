import fetch_prices
import pytest
import requests


class FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {"success": False, "error": "bad token"}


def test_fetch_flights_success_false(monkeypatch):
    def fake_get(url, params=None, headers=None):
        return FakeResponse()

    monkeypatch.setattr(fetch_prices.requests, "get", fake_get)

    with pytest.raises(RuntimeError):
        fetch_prices.fetch_flights("GDN", "FNC", "2026-12")


class FakeResponse500:
    def raise_for_status(self):
        raise requests.exceptions.HTTPError("500 Server Error")


def test_fetch_flights_http_error(monkeypatch):
    def fake_get(url, params=None, headers=None):
        return FakeResponse500()

    monkeypatch.setattr(fetch_prices.requests, "get", fake_get)

    with pytest.raises(requests.exceptions.HTTPError):
        fetch_prices.fetch_flights("GDN", "FNC", "2026-12")
