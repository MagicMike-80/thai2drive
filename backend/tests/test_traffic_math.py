"""Regression tests for the educational stopping-distance model."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import traffic_math


@pytest.mark.parametrize("seconds,reaction,total", [(1, 24, 56), (2, 48, 80), (3, 72, 104)])
def test_80_kmh_reaction_buttons_change_stopping_distance(seconds, reaction, total):
    result = traffic_math.stopping_distance_full(80, "dry", seconds)
    assert result["input"]["reaction_time_s"] == seconds
    assert result["results"]["reaction_distance_m"] == reaction
    assert result["results"]["braking_distance_m"] == 32
    assert result["results"]["stopping_distance_m"] == total
    assert result["steps"][1]["result"] == reaction


@pytest.mark.parametrize("condition,factor,braking,total", [
    ("dry", 1, 32, 56), ("wet", 2, 64, 88), ("snow", 4, 128, 152), ("ice", 4, 128, 152),
])
def test_80_kmh_road_condition_changes_braking_only(condition, factor, braking, total):
    result = traffic_math.stopping_distance_full(80, condition, 1)
    assert traffic_math.ROAD_CONDITIONS[condition]["multiplier"] == factor
    assert result["results"]["reaction_distance_m"] == 24
    assert result["results"]["braking_distance_m"] == braking
    assert result["results"]["stopping_distance_m"] == total


def test_following_gap_is_a_separate_three_second_calculation():
    following = traffic_math.following_distance(80)
    stopping = traffic_math.stopping_distance_full(80, "dry", 3)
    assert following["input"]["seconds"] == 3
    assert following["results"]["following_distance_m"] == 66.7
    assert stopping["results"]["reaction_distance_m"] == 72
    assert "huskeregel" in following["rule_note"]["no"]
