"""
Matomo MCP Server - Conversational Analytics
Talk to your website analytics in natural language.

Author: Ronald Mego
License: MIT
"""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

# Configuration — requires .env file with MATOMO_URL and MATOMO_TOKEN
MATOMO_URL = os.getenv("MATOMO_URL")
MATOMO_TOKEN = os.getenv("MATOMO_TOKEN")
DEFAULT_SITE_ID = int(os.getenv("DEFAULT_SITE_ID", "1"))

if not MATOMO_URL:
    raise ValueError("MATOMO_URL is required. Set it in your .env file.")
if not MATOMO_TOKEN:
    raise ValueError("MATOMO_TOKEN is required. Set it in your .env file.")

# Site mapping — customize with your own sites
# Format: {"alias": site_id}
# Configure via MATOMO_SITES env var as "alias1:id1,alias2:id2" or use defaults
SITES = {}
sites_env = os.getenv("MATOMO_SITES", "")
if sites_env:
    for entry in sites_env.split(","):
        entry = entry.strip()
        if ":" in entry:
            name, sid = entry.rsplit(":", 1)
            SITES[name.strip().lower()] = int(sid.strip())

mcp = FastMCP("Matomo Analytics")


def matomo_api(method: str, params: dict = None) -> dict:
    """Make a request to Matomo API."""
    base_params = {
        "module": "API",
        "method": method,
        "format": "JSON",
        "token_auth": MATOMO_TOKEN,
    }
    if params:
        base_params.update(params)

    # Use POST — some Matomo configs require it for token auth
    response = requests.post(f"{MATOMO_URL}/index.php", data=base_params)
    response.raise_for_status()
    return response.json()


def resolve_site_id(site: str = None) -> int:
    """Resolve site name to ID."""
    if site is None:
        return DEFAULT_SITE_ID
    if isinstance(site, int):
        return site
    try:
        return int(site)
    except (ValueError, TypeError):
        pass
    site_lower = site.lower().strip()
    return SITES.get(site_lower, DEFAULT_SITE_ID)


def get_period_params(period: str = "today") -> dict:
    """Get date parameters for Matomo API."""
    period_lower = period.lower()

    period_map = {
        "today": {"period": "day", "date": "today"},
        "yesterday": {"period": "day", "date": "yesterday"},
        "week": {"period": "week", "date": "today"},
        "this week": {"period": "week", "date": "today"},
        "month": {"period": "month", "date": "today"},
        "this month": {"period": "month", "date": "today"},
        "year": {"period": "year", "date": "today"},
        "this year": {"period": "year", "date": "today"},
        "last 7 days": {"period": "range", "date": "last7"},
        "7 days": {"period": "range", "date": "last7"},
        "last 30 days": {"period": "range", "date": "last30"},
        "30 days": {"period": "range", "date": "last30"},
    }

    return period_map.get(period_lower, {"period": "day", "date": "today"})


@mcp.tool
def get_visits_summary(site: str = None, period: str = "today") -> dict:
    """
    Get visit summary for a site.

    Args:
        site: Site name or numeric ID (uses default if not specified)
        period: Time period (today, yesterday, week, month, year, last 7 days, last 30 days)

    Returns:
        Visit statistics including unique visitors, visits, actions, bounce rate, etc.
    """
    site_id = resolve_site_id(site)
    params = {"idSite": site_id, **get_period_params(period)}

    data = matomo_api("VisitsSummary.get", params)

    return {
        "site_id": site_id,
        "period": period,
        "unique_visitors": data.get("nb_uniq_visitors", 0),
        "visits": data.get("nb_visits", 0),
        "actions": data.get("nb_actions", 0),
        "pageviews": data.get("nb_pageviews", 0),
        "avg_time_on_site": data.get("avg_time_on_site", 0),
        "bounce_rate": data.get("bounce_rate", "0%"),
        "actions_per_visit": data.get("nb_actions_per_visit", 0),
    }


@mcp.tool
def get_top_pages(site: str = None, period: str = "today", limit: int = 10) -> dict:
    """
    Get top visited pages for a site.

    Args:
        site: Site name or numeric ID (uses default if not specified)
        period: Time period
        limit: Number of pages to return (default 10)

    Returns:
        List of top pages with visit counts
    """
    site_id = resolve_site_id(site)
    params = {
        "idSite": site_id,
        "filter_limit": limit,
        **get_period_params(period)
    }

    data = matomo_api("Actions.getPageUrls", params)

    pages = []
    for page in data[:limit] if isinstance(data, list) else []:
        pages.append({
            "url": page.get("label", ""),
            "pageviews": page.get("nb_hits", 0),
            "unique_pageviews": page.get("nb_visits", 0),
            "avg_time_on_page": page.get("avg_time_on_page", 0),
            "bounce_rate": page.get("bounce_rate", "0%"),
        })

    return {"site_id": site_id, "period": period, "top_pages": pages}


@mcp.tool
def get_referrers(site: str = None, period: str = "today", limit: int = 10) -> dict:
    """
    Get traffic sources (referrers) for a site.

    Args:
        site: Site name or numeric ID (uses default if not specified)
        period: Time period
        limit: Number of referrers to return

    Returns:
        Traffic sources breakdown
    """
    site_id = resolve_site_id(site)
    params = {
        "idSite": site_id,
        "filter_limit": limit,
        **get_period_params(period)
    }

    types_data = matomo_api("Referrers.getReferrerType", params)

    types = []
    for ref in types_data if isinstance(types_data, list) else []:
        types.append({
            "type": ref.get("label", ""),
            "visits": ref.get("nb_visits", 0),
            "actions": ref.get("nb_actions", 0),
        })

    return {"site_id": site_id, "period": period, "referrer_types": types}


@mcp.tool
def get_countries(site: str = None, period: str = "today", limit: int = 10) -> dict:
    """
    Get visitor countries for a site.

    Args:
        site: Site name or numeric ID (uses default if not specified)
        period: Time period
        limit: Number of countries to return

    Returns:
        List of countries with visit counts
    """
    site_id = resolve_site_id(site)
    params = {
        "idSite": site_id,
        "filter_limit": limit,
        **get_period_params(period)
    }

    data = matomo_api("UserCountry.getCountry", params)

    countries = []
    for country in data[:limit] if isinstance(data, list) else []:
        countries.append({
            "country": country.get("label", ""),
            "visits": country.get("nb_visits", 0),
            "actions": country.get("nb_actions", 0),
        })

    return {"site_id": site_id, "period": period, "countries": countries}


@mcp.tool
def get_devices(site: str = None, period: str = "today") -> dict:
    """
    Get device types used by visitors.

    Args:
        site: Site name or numeric ID (uses default if not specified)
        period: Time period

    Returns:
        Breakdown by device type (desktop, mobile, tablet)
    """
    site_id = resolve_site_id(site)
    params = {"idSite": site_id, **get_period_params(period)}

    data = matomo_api("DevicesDetection.getType", params)

    devices = []
    for device in data if isinstance(data, list) else []:
        devices.append({
            "type": device.get("label", ""),
            "visits": device.get("nb_visits", 0),
            "percentage": device.get("nb_visits_percentage", 0),
        })

    return {"site_id": site_id, "period": period, "devices": devices}


@mcp.tool
def get_live_visitors(site: str = None, minutes: int = 30) -> dict:
    """
    Get live visitor information (last N minutes).

    Args:
        site: Site name or numeric ID (uses default if not specified)
        minutes: Minutes to look back (default 30)

    Returns:
        Live visitor count and recent visits
    """
    site_id = resolve_site_id(site)

    counter = matomo_api("Live.getCounters", {
        "idSite": site_id,
        "lastMinutes": minutes
    })

    return {
        "site_id": site_id,
        "last_minutes": minutes,
        "visitors": counter[0].get("visitors", 0) if counter else 0,
        "visits": counter[0].get("visits", 0) if counter else 0,
        "actions": counter[0].get("actions", 0) if counter else 0,
    }


@mcp.tool
def get_search_keywords(site: str = None, period: str = "month", limit: int = 10) -> dict:
    """
    Get search keywords that brought visitors to the site.

    Args:
        site: Site name or numeric ID (uses default if not specified)
        period: Time period
        limit: Number of keywords to return

    Returns:
        List of search keywords with visit counts
    """
    site_id = resolve_site_id(site)
    params = {
        "idSite": site_id,
        "filter_limit": limit,
        **get_period_params(period)
    }

    data = matomo_api("Referrers.getKeywords", params)

    keywords = []
    for kw in data[:limit] if isinstance(data, list) else []:
        keywords.append({
            "keyword": kw.get("label", ""),
            "visits": kw.get("nb_visits", 0),
        })

    return {"site_id": site_id, "period": period, "keywords": keywords}


@mcp.tool
def get_weekly_comparison(site: str = None) -> dict:
    """
    Compare this week vs last week for a site.

    Args:
        site: Site name or numeric ID (uses default if not specified)

    Returns:
        Comparison of this week vs last week
    """
    site_id = resolve_site_id(site)

    this_week = matomo_api("VisitsSummary.get", {"idSite": site_id, "period": "week", "date": "today"})
    last_week = matomo_api("VisitsSummary.get", {"idSite": site_id, "period": "week", "date": "lastWeek"})

    return {
        "site_id": site_id,
        "this_week": {
            "visitors": this_week.get("nb_uniq_visitors", 0),
            "pageviews": this_week.get("nb_pageviews", 0),
        },
        "last_week": {
            "visitors": last_week.get("nb_uniq_visitors", 0),
            "pageviews": last_week.get("nb_pageviews", 0),
        }
    }


@mcp.tool
def get_site_info() -> dict:
    """
    Get information about the default tracked site from Matomo API.

    Returns:
        Site details (name, URL, creation date)
    """
    data = matomo_api("SitesManager.getSiteFromId", {"idSite": DEFAULT_SITE_ID})
    if isinstance(data, list) and data:
        site = data[0]
        return {
            "id": site.get("idsite"),
            "name": site.get("name", ""),
            "url": site.get("main_url", ""),
            "created": site.get("ts_created", ""),
        }
    return {"id": DEFAULT_SITE_ID, "name": "Unknown", "url": "", "created": ""}


if __name__ == "__main__":
    mcp.run()
