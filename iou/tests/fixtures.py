import dataclasses

import pytest
import requests_mock
from django.contrib.auth.models import User
from django.test import Client
from requests_mock.adapter import _Matcher


@pytest.fixture()
def test_account_password():
    return "secret"


@pytest.fixture()
def user(test_account_password):
    return User.objects.create_user(username="fred", password=test_account_password)


@pytest.fixture()
def client(user: User, test_account_password: str):
    c = Client()
    c.login(username=user.username, password=test_account_password)
    return c


@dataclasses.dataclass
class MockSlackRequest:
    """
    Attributes
    ----------

    request : _Matcher
        The call_count should be asserted in tests.

    is_slack_configured : bool
        Whether or not the slack webhook is configured.
        If False, the request.call_count should be 0.
        If True, the request.call_count should equal the number
        of Debts created or deleted during the test.
    """

    request: _Matcher
    is_slack_configured: bool


@dataclasses.dataclass
class MockSlackScenario:
    is_slack_configured: bool
    slack_response_status_code: int | None = None


@pytest.fixture(
    autouse=True,
    ids=[
        "slack not configured",
        "slack post success",
        "slack post fail",
    ],
    params=[
        MockSlackScenario(
            is_slack_configured=False,
        ),
        MockSlackScenario(
            is_slack_configured=True,
            slack_response_status_code=200,
        ),
        MockSlackScenario(
            is_slack_configured=True,
            slack_response_status_code=400,
        ),
    ],
)
def mock_slack_request(
    request,
    monkeypatch: pytest.MonkeyPatch,
    requests_mock: requests_mock.Mocker,
) -> MockSlackRequest:
    """
    Parametrized fixture for different scenarios of slack configuration and behavior.
    """
    mock_slack_scenario: MockSlackScenario = request.param
    slack_webhook_url = "https://hooks.slack.com/services/some/webhook"

    if mock_slack_scenario.is_slack_configured:
        monkeypatch.setenv("SLACK_WEBHOOK", slack_webhook_url)
    else:
        monkeypatch.delenv("SLACK_WEBHOOK")

    slack_request = requests_mock.post(
        url=slack_webhook_url,
        status_code=mock_slack_scenario.slack_response_status_code,
    )
    return MockSlackRequest(
        request=slack_request,
        is_slack_configured=mock_slack_scenario.is_slack_configured,
    )
