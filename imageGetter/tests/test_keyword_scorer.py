# ABOUTME: Tests for KeywordScorer proximity-based scoring algorithm
# ABOUTME: Validates scoring based on keyword distance from image URLs, subject bonuses, and multipliers

import pytest
from keyword_scorer import KeywordScorer


def test_scorer_initialization():
    """Test that KeywordScorer initializes with correct URL position"""
    body = "Here is my firewall build"
    subject = "Firewall installation"
    scorer = KeywordScorer(body, subject, image_url_position=10)
    assert scorer.url_position == 10


def test_score_keyword_in_subject():
    """Test that keywords in subject line get high scores (200+ bonus)"""
    body = "Here is the build"
    subject = "Firewall installation"
    scorer = KeywordScorer(body, subject, image_url_position=10)
    scores = scorer.score_keywords_batch(["firewall", "wing"])
    assert scores["firewall"] > 200  # Subject bonus
    assert scores["wing"] == 0


def test_score_keyword_near_url():
    """Test that keywords near image URL score higher than zero"""
    body = "Here is my firewall build at position [IMAGE]"
    subject = "Build update"
    image_pos = body.find("[IMAGE]")
    scorer = KeywordScorer(body, subject, image_url_position=image_pos)
    scores = scorer.score_keywords_batch(["firewall", "wing"])
    assert scores["firewall"] > 0  # Near image
    assert scores["wing"] == 0


def test_score_keyword_far_from_url():
    """Test that proximity affects scoring - closer keywords score higher"""
    body = "Wing discussion here. [IMAGE] Later: firewall stuff"
    subject = "Build update"
    image_pos = body.find("[IMAGE]")
    scorer = KeywordScorer(body, subject, image_url_position=image_pos)
    scores = scorer.score_keywords_batch(["wing", "firewall"])
    # Firewall appears AFTER image (closer), wing appears BEFORE (farther)
    # So firewall should score higher
    assert scores["firewall"] > scores["wing"]


def test_score_multiple_keywords():
    """Test scoring multiple keywords in one batch"""
    body = "Working on firewall and cowling today near the image [IMG]"
    subject = "Engine work"
    image_pos = body.find("[IMG]")
    scorer = KeywordScorer(body, subject, image_url_position=image_pos)
    scores = scorer.score_keywords_batch(["firewall", "cowling", "wing", "engine"])

    # Keywords present in body should score > 0
    assert scores["firewall"] > 0
    assert scores["cowling"] > 0
    # Keyword in subject should score high
    assert scores["engine"] > 200
    # Absent keyword should score 0
    assert scores["wing"] == 0


def test_score_returns_zero_for_absent_keywords():
    """Test that keywords not in text return score of 0"""
    body = "This is about firewall work"
    subject = "Build update"
    scorer = KeywordScorer(body, subject, image_url_position=10)
    scores = scorer.score_keywords_batch(["nonexistent", "missing", "absent"])

    assert scores["nonexistent"] == 0
    assert scores["missing"] == 0
    assert scores["absent"] == 0


def test_score_case_insensitive():
    """Test that scoring is case-insensitive"""
    body = "FIREWALL work here [IMG]"
    subject = "Build Update"
    image_pos = body.find("[IMG]")
    scorer = KeywordScorer(body, subject, image_url_position=image_pos)
    scores = scorer.score_keywords_batch(["firewall", "build"])

    # Should match despite case differences
    assert scores["firewall"] > 0
    assert scores["build"] > 0


def test_score_frequency_affects_score():
    """Test that multiple occurrences increase score"""
    body = "Firewall here. More firewall. Even more firewall. [IMG]"
    subject = "Build"
    image_pos = body.find("[IMG]")
    scorer = KeywordScorer(body, subject, image_url_position=image_pos)

    # Score with 3 occurrences
    scores_multiple = scorer.score_keywords_batch(["firewall"])

    # Compare to single occurrence
    body_single = "Firewall here. [IMG]"
    image_pos_single = body_single.find("[IMG]")
    scorer_single = KeywordScorer(body_single, subject, image_url_position=image_pos_single)
    scores_single = scorer_single.score_keywords_batch(["firewall"])

    # Multiple occurrences should score higher
    assert scores_multiple["firewall"] > scores_single["firewall"]
