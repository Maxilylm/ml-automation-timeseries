"""Shared pytest fixtures for ml-automation-timeseries."""

import pytest
from pathlib import Path
from datetime import datetime, timedelta


@pytest.fixture
def mock_llm_response():
    """LLM-response dict fixture."""
    return {
        "id": "msg-test-123",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "This is a test LLM response."
            }
        ],
        "model": "claude-opus-4-7",
        "usage": {
            "input_tokens": 100,
            "output_tokens": 50
        }
    }


@pytest.fixture
def sample_dataset():
    """Sample dataset fixture with 10 row dicts."""
    base_date = datetime(2024, 1, 1)
    return [
        {
            "timestamp": (base_date + timedelta(days=i)).isoformat(),
            "value": 100 + (i * 2),
            "category": "A" if i % 2 == 0 else "B"
        }
        for i in range(10)
    ]


@pytest.fixture
def temp_workspace(tmp_path):
    """Temporary workspace fixture."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace
