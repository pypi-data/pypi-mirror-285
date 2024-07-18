from gawsoft.api_client.response import Response
from requests import Response as RequestsResponse
import hashlib


def assert_file_hash(file_path: str, hash: str):
    with open(file_path, "rb") as fp:
        image = fp.read()

    md5 = hashlib.md5()
    md5.update(image)
    md5_hash = md5.hexdigest()

    assert md5_hash == hash


def test_parse_response(
    response : RequestsResponse
):
    resp = Response(response)
    assert resp.status_code == 200
    assert resp.headers == {
        "content-type": "application/json",
        "accept": "application/gzip"
    }
    assert resp.is_json()
    assert resp.data() == {"foo": "bar"}

def test_save_json_in_file(
    response : RequestsResponse
):
    resp = Response(response)
    assert resp.is_json()
    assert resp.save("/tmp/test.json")
    assert_file_hash("/tmp/test.json", "94232c5b8fc9272f6f73a1e36eb68fcf")

def test_image_as_response(
    response_image : RequestsResponse
):
    resp = Response(response_image)
    assert resp.status_code == 200
    assert resp.headers == {
        "content-type": "image/png",
    }
    assert resp.is_json() == False
    assert resp.save("/tmp/image.png") == "/tmp/image.png"
    assert_file_hash("/tmp/image.png", "d16fbdccd830021d48d0a7498b0c4456")

def test_image_as_response(
    response_image : RequestsResponse
):
    resp = Response(response_image)
    assert resp.status_code == 200
    assert resp.headers == {
        "content-type": "image/png",
    }
    assert resp.is_json() == False
    assert resp.save("/tmp/image.png") == "/tmp/image.png"
    assert_file_hash("/tmp/image.png", "d16fbdccd830021d48d0a7498b0c4456")
