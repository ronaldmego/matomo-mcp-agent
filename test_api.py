#!/usr/bin/env python3
"""Test suite for Matomo MCP tools."""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Pre-flight checks before importing server (which raises on missing env)
MATOMO_URL = os.getenv("MATOMO_URL")
MATOMO_TOKEN = os.getenv("MATOMO_TOKEN")

if not MATOMO_URL or not MATOMO_TOKEN:
    print("ERROR: MATOMO_URL and MATOMO_TOKEN must be set in .env")
    sys.exit(1)

from server import (
    get_visits_summary,
    get_top_pages,
    get_referrers,
    get_countries,
    get_devices,
    get_live_visitors,
    get_search_keywords,
    get_weekly_comparison,
    get_site_info,
    resolve_site_id,
    get_period_params,
    DEFAULT_SITE_ID,
)

passed = 0
failed = 0


def run_test(name, fn):
    """Run a single test and track results."""
    global passed, failed
    try:
        fn()
        print(f"  PASS  {name}")
        passed += 1
    except Exception as e:
        print(f"  FAIL  {name}: {e}")
        failed += 1


# --- Unit tests (no API calls) ---

def test_resolve_site_id_default():
    assert resolve_site_id(None) == DEFAULT_SITE_ID

def test_resolve_site_id_int():
    assert resolve_site_id(7) == 7

def test_resolve_site_id_numeric_string():
    assert resolve_site_id("3") == 3

def test_period_today():
    p = get_period_params("today")
    assert p == {"period": "day", "date": "today"}

def test_period_week():
    p = get_period_params("week")
    assert p == {"period": "week", "date": "today"}

def test_period_last_30():
    p = get_period_params("last 30 days")
    assert p == {"period": "range", "date": "last30"}

def test_period_unknown_defaults_today():
    p = get_period_params("something_invalid")
    assert p == {"period": "day", "date": "today"}


# --- Integration tests (call Matomo API) ---

def test_get_site_info():
    result = get_site_info()
    assert isinstance(result, dict)
    assert "id" in result
    assert "name" in result

def test_get_visits_summary_default():
    result = get_visits_summary()
    assert isinstance(result, dict)
    assert "visits" in result
    assert "bounce_rate" in result
    assert result["site_id"] == DEFAULT_SITE_ID

def test_get_visits_summary_with_period():
    result = get_visits_summary(period="month")
    assert isinstance(result, dict)
    assert result["period"] == "month"

def test_get_visits_summary_with_site_id():
    result = get_visits_summary(site=str(DEFAULT_SITE_ID))
    assert isinstance(result, dict)
    assert result["site_id"] == DEFAULT_SITE_ID

def test_get_top_pages():
    result = get_top_pages(limit=3)
    assert isinstance(result, dict)
    assert "top_pages" in result
    assert isinstance(result["top_pages"], list)

def test_get_referrers():
    result = get_referrers()
    assert isinstance(result, dict)
    assert "referrer_types" in result
    assert isinstance(result["referrer_types"], list)

def test_get_countries():
    result = get_countries(limit=5)
    assert isinstance(result, dict)
    assert "countries" in result
    assert isinstance(result["countries"], list)

def test_get_devices():
    result = get_devices()
    assert isinstance(result, dict)
    assert "devices" in result
    assert isinstance(result["devices"], list)

def test_get_live_visitors():
    result = get_live_visitors(minutes=10)
    assert isinstance(result, dict)
    assert "visitors" in result
    assert result["last_minutes"] == 10

def test_get_search_keywords():
    result = get_search_keywords(limit=5)
    assert isinstance(result, dict)
    assert "keywords" in result
    assert isinstance(result["keywords"], list)

def test_get_weekly_comparison():
    result = get_weekly_comparison()
    assert isinstance(result, dict)
    assert "this_week" in result
    assert "last_week" in result
    assert "visitors" in result["this_week"]
    assert "visitors" in result["last_week"]


if __name__ == "__main__":
    print(f"Matomo MCP Test Suite")
    print(f"URL: {MATOMO_URL}")
    print(f"Default Site ID: {DEFAULT_SITE_ID}")
    print()

    print("Unit tests:")
    run_test("resolve_site_id(None) → default", test_resolve_site_id_default)
    run_test("resolve_site_id(int) → passthrough", test_resolve_site_id_int)
    run_test("resolve_site_id('3') → parsed int", test_resolve_site_id_numeric_string)
    run_test("period 'today' → day/today", test_period_today)
    run_test("period 'week' → week/today", test_period_week)
    run_test("period 'last 30 days' → range/last30", test_period_last_30)
    run_test("period unknown → defaults to today", test_period_unknown_defaults_today)

    print("\nIntegration tests (calling Matomo API):")
    run_test("get_site_info()", test_get_site_info)
    run_test("get_visits_summary() default", test_get_visits_summary_default)
    run_test("get_visits_summary(period='month')", test_get_visits_summary_with_period)
    run_test("get_visits_summary(site=ID)", test_get_visits_summary_with_site_id)
    run_test("get_top_pages(limit=3)", test_get_top_pages)
    run_test("get_referrers()", test_get_referrers)
    run_test("get_countries(limit=5)", test_get_countries)
    run_test("get_devices()", test_get_devices)
    run_test("get_live_visitors(minutes=10)", test_get_live_visitors)
    run_test("get_search_keywords(limit=5)", test_get_search_keywords)
    run_test("get_weekly_comparison()", test_get_weekly_comparison)

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")

    if failed > 0:
        sys.exit(1)
    print("All tests passed!")
