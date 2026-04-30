"""Unit tests for KTC scraper — HTML parsing logic."""

from __future__ import annotations

import json

from gridiron.scrapers.ktc import _parse_players


_SAMPLE_HTML = """
<html><body>
<script>
var playersArray = [
  {"playerID": 1, "playerName": "Patrick Mahomes", "position": "QB", "team": "KC", "age": 28, "value": 9500, "trend30Day": 50},
  {"playerID": 2, "playerName": "Tyreek Hill", "position": "WR", "team": "MIA", "age": 29, "value": 8200, "trend30Day": -100},
  {"playerID": 3, "playerName": "Travis Kelce", "position": "TE", "team": "KC", "age": 34, "value": 6500, "trend30Day": -200}
];
</script>
</body></html>
"""


def test_parse_players_1qb() -> None:
    result = _parse_players(_SAMPLE_HTML, is_sf=False)
    assert len(result) == 3
    mahomes = result.get("patrick mahomes")
    assert mahomes is not None
    assert mahomes["value_1qb"] == 9500
    assert mahomes["trend_1qb"] == 50
    assert mahomes["position"] == "QB"
    assert mahomes["team"] == "KC"


def test_parse_players_sf() -> None:
    result = _parse_players(_SAMPLE_HTML, is_sf=True)
    assert len(result) == 3
    mahomes = result.get("patrick mahomes")
    assert mahomes is not None
    assert mahomes["value_sf"] == 9500
    assert mahomes["trend_sf"] == 50
    # 1QB fields should NOT be present in SF mode
    assert "value_1qb" not in mahomes


def test_parse_players_no_array() -> None:
    result = _parse_players("<html><body>no array here</body></html>", is_sf=False)
    assert result == {}


def test_parse_players_negative_trend() -> None:
    result = _parse_players(_SAMPLE_HTML, is_sf=False)
    kelce = result.get("travis kelce")
    assert kelce is not None
    assert kelce["trend_1qb"] == -200
