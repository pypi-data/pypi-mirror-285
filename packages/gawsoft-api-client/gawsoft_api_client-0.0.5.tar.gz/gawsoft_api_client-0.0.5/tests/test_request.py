import pytest
from pytest_httpserver import HTTPServer
from gawsoft.api_client import Request, ApiException

def test_send_post_request(
    request_client: Request,
    httpserver: HTTPServer
):
    httpserver.expect_request('/v1/data', method="POST").respond_with_json({"foo": "bar"}, 201)

    response = request_client.request("/data", "POST")
    assert response.status_code == 201
    assert response.data() == {"foo": "bar"}


def test_send_post_request_error_code_429(
    request_client: Request,
    httpserver: HTTPServer
):
    httpserver.expect_request('/v1/data', method="POST").respond_with_json({"foo": "bar"}, 429)

    with pytest.raises(ApiException):
        response = request_client.request("/data", "POST")
        assert response.status_code == 429
        assert response.data() == {"foo": "bar"}

def test_send_post_request_with_400_response(
    request_client: Request,
    httpserver: HTTPServer
):
    httpserver.expect_request('/v1/data', method="POST").respond_with_json({"foo": "bar"}, 400)

    response = request_client.request("/data", "POST")
    assert response.status_code == 400
    assert response.data() == {"foo": "bar"}

def test_get_request_with_params(
    request_client: Request,
    httpserver: HTTPServer
):
    httpserver.expect_request('/v1/data', method="GET", query_string={"abc": "1", "def": "aaa"}).respond_with_json({"foo": "bar"})

    response = request_client.request("/data", "GET", query_params={"abc": 1, "def": "aaa"})
    assert response.data() == {"foo": "bar"}

def test_get_request_gzipped(
    request_client: Request,
):
    response = request_client.execute(
        url = "https://httpbin.org/gzip",
        method = "GET",
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip"
        }
    )
    assert response.is_json()
    assert response.data()['gzipped']


def test_delete_request_with_params(
    request_client: Request,
    httpserver: HTTPServer
):
    httpserver.expect_request('/v1/data/id1', method="DELETE").respond_with_json({"foo": "bar"})

    response = request_client.request("/data/id1", "DELETE")
    assert response.status_code == 200
    assert response.data() == {"foo": "bar"}

def test_put_request_with_params(
    request_client: Request,
    httpserver: HTTPServer
):
    httpserver.expect_request('/v1/data/id1', method="PUT").respond_with_json({"foo": "bar"})

    response = request_client.request("/data/id1", "PUT", {"abc": 123})
    assert response.status_code == 200
    assert response.data() == {"foo": "bar"}

def test_post_request_with_image(
    request_client: Request,
    image_bytes: bytes,
    httpserver: HTTPServer
):

    httpserver.expect_request(
        '/v1/upload',
        headers = {
          "Content-Type": "image/png"
        },
        data = image_bytes,
        method="POST"
    ).respond_with_json({"foo": "bar"})

    response = request_client.request("/upload", "POST", image_bytes, headers={
        "Content-Type": "image/png"
    })
    assert response.status_code == 200
    assert response.data() == {"foo": "bar"}


def test_get_execute_with_params(
    request_client: Request,
    httpserver: HTTPServer
):
    httpserver.expect_request('/v1/data', method="GET", query_string={"abc": "1", "def": "aaa"}).respond_with_json({"foo": "bar"})

    response = request_client.execute(url="http://127.0.0.1:5050/v1/data", method="GET", query_params={"abc": 1, "def": "aaa"})
    assert response.data() == {"foo": "bar"}