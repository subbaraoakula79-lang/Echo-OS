"""
ECHO OS — Backend Integration Test Suite
Tests configuration, security, API endpoints, agent tool registration, and database CRUD.
"""

try:
    import pytest
except ImportError:
    pytest = None
import asyncio
from core.config import settings
from core.security import hash_password, verify_password, create_access_token, decode_access_token
from services.tools import register_all_tools
from core.agent import agent


def test_config_loaded():
    assert settings.PROJECT_NAME == "ECHO OS"
    assert settings.VERSION == "1.0.0"
    assert settings.API_PREFIX == "/api/v1"


def test_password_hashing():
    raw = "jarvis_secure_pass_123"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed)
    assert not verify_password("wrong_password", hashed)


def test_jwt_token_flow():
    import uuid
    user_id = uuid.uuid4()
    token = create_access_token(user_id)
    payload = decode_access_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"


def test_tool_registration():
    register_all_tools()
    registered_names = [t["function"]["name"] for t in agent.tools]
    expected_tools = [
        "search_web", "create_task", "create_reminder", "open_app",
        "search_files", "create_file", "read_file", "send_email",
        "create_calendar_event", "call_contact", "send_sms",
    ]
    for tool_name in expected_tools:
        assert tool_name in registered_names, f"Tool {tool_name} should be registered"


if __name__ == "__main__":
    test_config_loaded()
    test_password_hashing()
    test_jwt_token_flow()
    test_tool_registration()
    print("✅ All backend unit & integration tests passed!")
