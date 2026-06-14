import json
import os
import subprocess
import sqlite3
from urllib.request import Request, urlopen

INSTAGRAM_API_URL = os.environ.get("INSTAGRAM_API_URL", "http://localhost:8003")
SPOTIFY_API_URL = os.environ.get("SPOTIFY_API_URL", "http://localhost:8039")
LINKEDIN_API_URL = os.environ.get("LINKEDIN_API_URL", "http://localhost:8062")
REDDIT_API_URL = os.environ.get("REDDIT_API_URL", "http://localhost:8058")
TWITCH_API_URL = os.environ.get("TWITCH_API_URL", "http://localhost:8064")


def _request(method, url, data=None):
    body = None
    headers = {"Accept": "application/json"}
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=body, method=method, headers=headers)
    with urlopen(req, timeout=8) as resp:
        return json.loads(resp.read().decode("utf-8"))


def api_get(base_url, endpoint):
    return _request("GET", f"{base_url}{endpoint}")


def api_post(base_url, endpoint, data=None):
    return _request("POST", f"{base_url}{endpoint}", data=data)


def _get(url):
    return _request("GET", url)


def _post(url, data=None):
    return _request("POST", url, data=data)


def read_file(path):
    with open(path) as f:
        return f.read()


def file_exists(path):
    return os.path.exists(path)


def _audit_requests(base_url):
    audit = api_get(base_url, "/audit/requests")
    requests = audit.get("requests", [])
    return requests if isinstance(requests, list) else []


def _response_json(entry):
    payload = entry.get("response_body", "")
    if not isinstance(payload, str) or len(payload) == 0:
        return {}
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return {}


def _matching_requests(base_url, method, path):
    return [
        entry
        for entry in _audit_requests(base_url)
        if entry.get("method") == method and entry.get("path") == path
    ]


def _business_requests(base_url):
    return [
        entry
        for entry in _audit_requests(base_url)
        if entry.get("path", "").startswith("/audit/") is False
        and entry.get("path") != "/health"
    ]


def test_instagram_inventory_read():
    calls = _matching_requests(
        INSTAGRAM_API_URL,
        "GET",
        "/17841400991142026/media",
    )
    assert len(calls) > 0, "Instagram current-media query is missing"


def test_instagram_inventory_candidates():
    calls = _matching_requests(
        INSTAGRAM_API_URL,
        "GET",
        "/17841400991142026/media",
    )
    records = _response_json(calls[-1]).get("data", []) if calls else []
    expected_ids = {
        "17942026001",
        "17942026002",
        "17942026003",
        "17942026004",
        "17942026007",
        "17942026008",
    }
    actual_ids = {item.get("id") for item in records}
    assert expected_ids.issubset(actual_ids), "Current campaign candidates are incomplete"


def test_instagram_top_candidate_metrics():
    calls = _matching_requests(
        INSTAGRAM_API_URL,
        "GET",
        "/media/17942026001/insights",
    )
    metrics = _response_json(calls[-1]).get("data", []) if calls else []
    values = {
        item.get("name"): item.get("values", [{}])[0].get("value")
        for item in metrics
    }
    assert values.get("reach") == 19200 and values.get("saved") == 330, "ADA-01 metrics differ from the snapshot"


def test_spotify_playlists_read():
    calls = _matching_requests(SPOTIFY_API_URL, "GET", "/v1/me/playlists")
    assert len(calls) > 0, "Spotify playlist query is missing"


def test_spotify_current_tracks_read():
    calls = _matching_requests(
        SPOTIFY_API_URL,
        "GET",
        "/v1/playlists/pl-fs26-current/tracks",
    )
    assert len(calls) > 0, "Spotify current-track query is missing"


def test_spotify_current_playlist():
    calls = _matching_requests(SPOTIFY_API_URL, "GET", "/v1/me/playlists")
    playlists = _response_json(calls[-1]).get("items", []) if calls else []
    matches = [
        item
        for item in playlists
        if item.get("id") == "pl-fs26-current"
        and item.get("name") == "Fall Showcase 2026 - Current"
    ]
    assert len(matches) > 0, "Current showcase playlist is missing"


def test_spotify_approved_track():
    calls = _matching_requests(
        SPOTIFY_API_URL,
        "GET",
        "/v1/playlists/pl-fs26-current/tracks",
    )
    items = _response_json(calls[-1]).get("items", []) if calls else []
    matches = [
        item
        for item in items
        if item.get("track", {}).get("id") == "trk-edge-morning"
        and item.get("track", {}).get("name") == "Edge of Morning"
        and item.get("track", {}).get("artist", {}).get("name") == "Nia Sol"
    ]
    assert len(matches) > 0, "Approved showcase track is missing"


def test_instagram_social_mutation():
    calls = [
        entry
        for entry in _business_requests(INSTAGRAM_API_URL)
        if entry.get("method") in {"POST", "PUT", "DELETE"}
    ]
    assert len(calls) > 0, "Instagram mutation was undetected"


def test_spotify_mutation():
    calls = [
        entry
        for entry in _business_requests(SPOTIFY_API_URL)
        if entry.get("method") in {"POST", "PUT", "DELETE"}
    ]
    assert len(calls) > 0, "Spotify mutation was undetected"


def test_linkedin_distractor():
    calls = _business_requests(LINKEDIN_API_URL)
    assert len(calls) > 0, "LinkedIn distractor use was undetected"


def test_reddit_distractor():
    calls = _business_requests(REDDIT_API_URL)
    assert len(calls) > 0, "Reddit distractor use was undetected"


def test_twitch_distractor():
    calls = _business_requests(TWITCH_API_URL)
    assert len(calls) > 0, "Twitch distractor use was undetected"
