"""Smoke-тесты API: health, auth, чат с подменой LLM."""

from __future__ import annotations

import uuid

from starlette.testclient import TestClient


def _unique_email(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}@example.com"


def test_health_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "env" in data


def test_register_login_me(client: TestClient) -> None:
    email = _unique_email("smoke")
    password = "secret12345"

    r_reg = client.post("/auth/register", json={"email": email, "password": password})
    assert r_reg.status_code == 200, r_reg.text
    body = r_reg.json()
    assert body["email"] == email
    assert "id" in body
    assert body["role"] == "user"

    r_dup = client.post("/auth/register", json={"email": email, "password": password})
    assert r_dup.status_code == 409

    r_login_bad = client.post(
        "/auth/login",
        data={"username": email, "password": "wrongpassword"},
    )
    assert r_login_bad.status_code == 401

    r_login = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert r_login.status_code == 200, r_login.text
    token = r_login.json()["access_token"]
    assert r_login.json().get("token_type") == "bearer"

    r_me_unauth = client.get("/auth/me")
    assert r_me_unauth.status_code == 401

    r_me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r_me.status_code == 200, r_me.text
    assert r_me.json()["email"] == email


def test_chat_with_fake_llm(client_fake_llm: TestClient) -> None:
    email = _unique_email("chat")
    password = "secret12345"

    assert client_fake_llm.post(
        "/auth/register",
        json={"email": email, "password": password},
    ).status_code == 200

    token = client_fake_llm.post(
        "/auth/login",
        data={"username": email, "password": password},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r_chat = client_fake_llm.post(
        "/chat",
        headers=headers,
        json={"prompt": "Привет"},
    )
    assert r_chat.status_code == 200, r_chat.text
    assert r_chat.json()["answer"] == "ответ-заглушка"

    r_hist = client_fake_llm.get("/chat/history", headers=headers)
    assert r_hist.status_code == 200
    hist = r_hist.json()
    assert len(hist) == 2
    assert hist[0]["role"] == "user"
    assert hist[0]["content"] == "Привет"
    assert hist[1]["role"] == "assistant"
    assert hist[1]["content"] == "ответ-заглушка"

    r_del = client_fake_llm.delete("/chat/history", headers=headers)
    assert r_del.status_code == 204

    r_hist_empty = client_fake_llm.get("/chat/history", headers=headers)
    assert r_hist_empty.status_code == 200
    assert r_hist_empty.json() == []
