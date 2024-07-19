from http import HTTPStatus

import pytest

# Test data URLs
URLS = {
    '/sessions/',
    '/sessions/2020-01-01/',
    '/sessions/2020-01-01/set_A',
    '/sessions/2020-01-01/set_A/device_1',
    '/sessions/2020-01-01/set_A/device_1/camera_1',
    '/sessions/2020-01-01/set_A/device_1/camera_1/20200101_094359.123456_000001.np',
}


@pytest.mark.parametrize('url', URLS)
def test_session_list(client, url):
    # Run the HTTP request
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    # Check response contents
    # It should be a list of strings e.g.
    # ["session_1", "session_2"]
    sessions: list[str] = response.json
    assert isinstance(sessions, list)
    for session_id in sessions:
        assert isinstance(session_id, str)
