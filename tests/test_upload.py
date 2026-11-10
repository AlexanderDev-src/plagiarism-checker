from io import BytesIO

import pytest

from plagiarism_checker import app


@pytest.fixture
def client():
    return app.test_client()


def upload(client, data, name):
    return client.post("/", data={"document": (BytesIO(data), name)}, content_type="multipart/form-data")


def test_get_shows_form(client):
    assert b'name="document"' in client.get("/").data


def test_valid_txt(client):
    r = upload(client, "สวัสดี hello".encode(), "a.txt")
    assert r.status_code == 200 and b"12 characters" in r.data


@pytest.mark.parametrize("data,name", [(b"x", "a.pdf"), (b"\xff\xfe", "a.txt"), (b"  \n", "a.txt")])
def test_rejects_bad_input(client, data, name):
    assert upload(client, data, name).status_code == 400


def test_missing_file(client):
    assert client.post("/", data={}).status_code == 400
