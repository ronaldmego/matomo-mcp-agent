#!/usr/bin/env python3
"""
Matomo MCP Chat Interface
Talk to your website analytics in natural language.

Author: Ronald Mego
License: MIT
"""

import os
import json
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.tools import tool as langchain_tool

# Import MCP tools
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
)

load_dotenv()

# Page config
st.set_page_config(
    page_title="Matomo Analytics Chat",
    page_icon="📊",
    layout="wide",
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #7c3aed, #ea580c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #94a3b8;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #7c3aed;
    }
    .stat-label {
        color: #94a3b8;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📊 Matomo Analytics Chat</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Talk to your website analytics in natural language</p>', unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []


# Create tools for LangChain using @tool decorator (LangChain 1.x API)
@langchain_tool
def tool_get_visits_summary(site: str = None, period: str = "today") -> str:
    """Get visit summary for a site. Args: site (name or ID, optional), period (today/yesterday/week/month/year/last 7 days/last 30 days)."""
    return json.dumps(get_visits_summary(site=site, period=period))


@langchain_tool
def tool_get_top_pages(site: str = None, period: str = "today", limit: int = 10) -> str:
    """Get top visited pages. Args: site (optional), period, limit."""
    return json.dumps(get_top_pages(site=site, period=period, limit=limit))


@langchain_tool
def tool_get_referrers(site: str = None, period: str = "today", limit: int = 10) -> str:
    """Get traffic sources/referrers. Args: site (optional), period, limit."""
    return json.dumps(get_referrers(site=site, period=period, limit=limit))


@langchain_tool
def tool_get_countries(site: str = None, period: str = "today", limit: int = 10) -> str:
    """Get visitor countries. Args: site (optional), period, limit."""
    return json.dumps(get_countries(site=site, period=period, limit=limit))


@langchain_tool
def tool_get_devices(site: str = None, period: str = "today") -> str:
    """Get device breakdown (desktop/mobile/tablet). Args: site (optional), period."""
    return json.dumps(get_devices(site=site, period=period))


@langchain_tool
def tool_get_live_visitors(site: str = None, minutes: int = 30) -> str:
    """Get live visitor count in last N minutes. Args: site (optional), minutes."""
    return json.dumps(get_live_visitors(site=site, minutes=minutes))


@langchain_tool
def tool_get_search_keywords(site: str = None, period: str = "month", limit: int = 10) -> str:
    """Get search keywords that brought visitors. Args: site (optional), period, limit."""
    return json.dumps(get_search_keywords(site=site, period=period, limit=limit))


@langchain_tool
def tool_get_weekly_comparison(site: str = None) -> str:
    """Compare this week vs last week. Args: site (optional)."""
    return json.dumps(get_weekly_comparison(site=site))


@langchain_tool
def tool_get_site_info() -> str:
    """Get information about the tracked site. No arguments needed."""
    return json.dumps(get_site_info())


tools = [
    tool_get_visits_summary,
    tool_get_top_pages,
    tool_get_referrers,
    tool_get_countries,
    tool_get_devices,
    tool_get_live_visitors,
    tool_get_search_keywords,
    tool_get_weekly_comparison,
    tool_get_site_info,
]

SYSTEM_PROMPT = """You are an analytics assistant that helps users understand their website performance.

You have access to Matomo Analytics data through the available tools.

When the user asks about analytics:
1. Use the available tools to fetch real data
2. Present the data clearly and in a friendly way
3. Offer insights when relevant
4. If no site is specified, use the default site
5. If no period is specified, default to "today"
"""


@st.cache_resource
def get_agent():
    """Create the LangChain agent."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.3,
    )

    return create_agent(llm, tools, system_prompt=SYSTEM_PROMPT)


# Sidebar with quick stats
with st.sidebar:
    st.markdown("### 🚀 Quick Stats")

    try:
        stats = get_visits_summary()

        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{stats['unique_visitors']}</div>
            <div class="stat-label">Unique visitors today</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="stat-card" style="margin-top: 1rem;">
            <div class="stat-value">{stats['pageviews']}</div>
            <div class="stat-label">Pageviews</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="stat-card" style="margin-top: 1rem;">
            <div class="stat-value">{stats['bounce_rate']}</div>
            <div class="stat-label">Bounce Rate</div>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading stats: {e}")

    st.markdown("---")
    st.markdown("### 💡 Examples")
    st.markdown("""
    - "How is my site doing today?"
    - "How many visits did I get this week?"
    - "What countries are my visitors from?"
    - "What are the most visited pages?"
    - "Is anyone on the site right now?"
    """)

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about your analytics..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Querying Matomo..."):
            try:
                agent = get_agent()
                result = agent.invoke(
                    {"messages": [{"role": "user", "content": prompt}]}
                )
                # Extract the last AI message content
                raw = result["messages"][-1].content
                # Handle structured content (list of blocks with type/text/extras)
                if isinstance(raw, list):
                    answer = "\n".join(
                        block.get("text", "") for block in raw
                        if isinstance(block, dict) and block.get("type") == "text"
                    )
                else:
                    answer = str(raw)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
