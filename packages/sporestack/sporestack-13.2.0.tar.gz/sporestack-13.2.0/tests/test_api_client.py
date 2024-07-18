import httpx
import pytest
import respx
from sporestack import api_client, exceptions

# respx seems to ignore the uri://domain if you don't specify it.


def test__is_onion_url() -> None:
    onion_url = "http://spore64i5sofqlfz5gq2ju4msgzojjwifls7"
    onion_url += "rok2cti624zyq3fcelad.onion/v2/"
    assert api_client._is_onion_url(onion_url) is True
    # This is a good, unusual test.
    onion_url = "https://www.facebookcorewwwi.onion/"
    assert api_client._is_onion_url(onion_url) is True
    assert api_client._is_onion_url("http://domain.com") is False
    assert api_client._is_onion_url("domain.com") is False
    assert api_client._is_onion_url("http://onion.domain.com/.onion/") is False
    assert api_client._is_onion_url("http://me.me/file.onion/") is False
    assert api_client._is_onion_url("http://me.me/file.onion") is False


def test_get_response_error_text() -> None:
    assert (
        api_client._get_response_error_text(
            httpx.Response(status_code=422, text="just text")
        )
        == "just text"
    )

    assert (
        api_client._get_response_error_text(
            httpx.Response(status_code=422, json={"detail": "detail text"})
        )
        == "detail text"
    )

    # This may not be the best behavior overall.
    assert (
        api_client._get_response_error_text(
            httpx.Response(status_code=422, json={"detail": {"msg": "nested message"}})
        )
        == "{'msg': 'nested message'}"
    )


def test_handle_response() -> None:
    with pytest.raises(exceptions.SporeStackServerError, match="What is this?"):
        api_client._handle_response(
            httpx.Response(status_code=100, text="What is this?")
        )

    api_client._handle_response(httpx.Response(status_code=200))
    api_client._handle_response(httpx.Response(status_code=201))
    api_client._handle_response(httpx.Response(status_code=204))

    with pytest.raises(exceptions.SporeStackUserError, match="Invalid arguments"):
        api_client._handle_response(
            httpx.Response(status_code=400, text="Invalid arguments")
        )

    with pytest.raises(exceptions.SporeStackUserError, match="Invalid arguments"):
        api_client._handle_response(
            httpx.Response(status_code=422, text="Invalid arguments")
        )

    with pytest.raises(
        exceptions.SporeStackTooManyRequestsError, match="Too many requests"
    ):
        api_client._handle_response(
            httpx.Response(status_code=429, text="Too many requests")
        )

    with pytest.raises(exceptions.SporeStackServerError, match="Try again"):
        api_client._handle_response(httpx.Response(status_code=500, text="Try again"))


def test_token_info(respx_mock: respx.MockRouter) -> None:
    dummy_token = "dummyinvalidtoken"
    response_json = {
        "balance_cents": 0,
        "balance_usd": "$0.00",
        "servers": 0,
        "autorenew_servers": 0,
        "suspended_servers": 0,
        "burn_rate_usd": "$0.00",
        "burn_rate_cents": 0,
        "days_remaining": 0,
    }
    route_response = httpx.Response(200, json=response_json)
    route = respx_mock.get(f"/token/{dummy_token}/info").mock(
        return_value=route_response
    )

    client = api_client.APIClient()
    info_response = client.token_info(dummy_token)
    assert info_response.balance_cents == 0
    assert info_response.balance_usd == "$0.00"
    assert info_response.burn_rate_cents == 0
    assert info_response.burn_rate_usd == "$0.00"
    assert info_response.servers == 0
    assert info_response.days_remaining == 0

    assert route.called


def test_server_info(respx_mock: respx.MockRouter) -> None:
    dummy_machine_id = "dummyinvalidmachineid"
    flavor = {
        "slug": "a flavor slug",
        "cores": 1,
        "memory": 1024,
        "disk": 25,
        "price": 38,
        "ipv4": "/32",
        "ipv6": "/128",
        "bandwidth_per_month": 1.0,
        "provider": "dummy",
    }

    response_json = {
        "machine_id": dummy_machine_id,
        "hostname": "a hostname",
        "provider": "dummy",
        "flavor_slug": "a flavor slug",
        "flavor": flavor,
        "region": "a region",
        "token": "a token",
        "running": True,
        "created_at": 1,
        "expiration": 2,
        "autorenew": False,
        "ipv4": "0.0.0.0",
        "ipv6": "::0",
        "deleted": False,
        "deleted_at": 0,
        "deleted_by": None,
        "forgotten_at": None,
        "suspended_at": None,
        "operating_system": "debian-11",
    }
    route_response = httpx.Response(200, json=response_json)
    route = respx_mock.get(f"/server/{dummy_machine_id}/info").mock(
        return_value=route_response
    )

    client = api_client.APIClient()
    info_response = client.server_info(dummy_machine_id)
    # These aren't exhaustive, but there's a number here.
    assert info_response.machine_id == dummy_machine_id
    assert info_response.hostname == response_json["hostname"]
    assert info_response.token == response_json["token"]
    assert info_response.running == response_json["running"]
    assert info_response.created_at == response_json["created_at"]
    assert info_response.expiration == response_json["expiration"]
    assert info_response.autorenew == response_json["autorenew"]
    assert info_response.forgotten_at == response_json["forgotten_at"]

    assert route.called
