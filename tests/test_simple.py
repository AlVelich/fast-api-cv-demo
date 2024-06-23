import os
import logging.config
import json
from fastapi.testclient import TestClient
import uuid
import asyncio
import requests

from main import app

client = TestClient(app)


class TestSimple:
    def setup_method(self):
        self.target_endpoint = 'test_s3'

    def teardown_method(self):
        pass

    def test_get_session(self):
        resp = requests.post("http://localhost:8000/get-session/")
        assert resp.status_code == 200
        assert "session_id" in resp.json()
        #response = client.post("/get-session/")
       # assert response.status_code == 200
       # assert "session_id" in response.json()


    def test_read_item_by_hash_name_401(self):
        resp = requests.get("http://localhost:8000/order/", params={"json_data": json.dumps({"key": "1"}), "session_id": "definitely not session-id", "client_order_id": str(uuid.uuid4())})
        #response = client.get("/order/", params={"json_data": json.dumps({"key": "1"}), "session_id": "definitely", "client_order_id": str(uuid.uuid4())})
        assert resp.status_code == 401

    def test_read_item_by_hash_name_413(self):
        too_big_json_data = "{'" + "a" * 16000 + "': " + "'1'" + "}"

        response = client.post("/get-session/")
        data = response.json()

        logging.info(data["session_id"])

        resp = requests.get("http://localhost:8000/order/", params={"json_data": too_big_json_data, "session_id": data["session_id"], "client_order_id": str(uuid.uuid4())})
        #response = client.get("/order/", params={"json_data": too_big_json_data, "session_id": data["session_id"], "client_order_id": str(uuid.uuid4())})
        assert resp.status_code == 413
