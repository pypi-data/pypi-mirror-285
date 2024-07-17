import os

from unittest.mock import patch, MagicMock
from second_opinion import review_code


@patch("second_opinion.AzureOpenAI")
def test_review_code(mock_azure):
    # Arrange
    mock_azure.return_value.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Test content"))]
    )

    diff = "Test diff"
    os.environ["PR_TITLE"] = "Test title"
    os.environ["PR_BODY"] = "Test body"

    # Act
    result = review_code(diff)

    # Assert
    assert "## Second Opinion 🩺 (AI Code Review)\n\nTest content" in result
    mock_azure.return_value.chat.completions.create.assert_called_once()
    messages = mock_azure.return_value.chat.completions.create.call_args[1]["messages"]
    assert messages[1]["content"] == "PR TITLE: Test title"
    assert messages[2]["content"] == "PR DESCRIPTION: Test body"
    assert messages[3]["content"] == diff
