"""
Marketing Intelligence Agent - REAL Implementation  
Runs actual agent code with live progress tracking
Ultra-minimalistic Apple-style UI
"""

import streamlit as st
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import traceback

# Agent imports
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
import numpy as np

# Load prompts
from prompts import (
    PROFILE_ANALYZER_PROMPT,
    TREND_SCRAPER_SYSTEM_PROMPT,
    RANKING_AGENT_PROMPT,
    REPORT_GENERATOR_PROMPT,
    VALIDATOR_PROMPT,
    SUMMARIZER_PROMPT
)

# Set page config
st.set_page_config(
    page_title="Marketing Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")  
BRIGHT_DATA_API_KEY = os.getenv("BRIGHT_DATA_API_KEY", "")

# Initialize LLMs
llm = ChatOpenAI(model="gpt-4o", temperature=0.1, api_key=OPENAI_API_KEY)
json_llm = ChatOpenAI(model="gpt-4o", temperature=0.1, 
                      model_kwargs={"response_format": {"type": "json_object"}},
                      api_key=OPENAI_API_KEY)

# Initialize Tavily
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# Ultra-minimal Apple CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif !important; }
    
    .stApp { background: #fafafa; }
    #MainMenu, footer, header {visibility: hidden;}
    
    h1 { font-weight: 700; color: #1d1d1f; letter-spacing: -1px; font-size: 48px; }
    h2 { font-weight: 600; color: #1d1d1f; letter-spacing: -0.5px; font-size: 24px; }
    
    .stButton > button {
        background: #1d1d1f;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 28px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #424245;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'step_results' not in st.session_state:
    st.session_state.step_results = {}

# Simple authentication
if not st.session_state.authenticated:
    st.title("Marketing Intelligence Agent")
    st.markdown("### Sign In")
    
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Sign In"):
            if username == "admin" and password == "stanford2025":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")
    st.stop()

# Main app
st.title("🎯 Marketing Intelligence Agent")
st.caption("Personalized insights from Reddit discussions")

# Sidebar: Input
with st.sidebar:
    st.markdown("### Business Profile")
    
    input_type = st.radio("Input Type", ["Company Name", "Instagram Handle", "Website URL"], label_visibility="collapsed")
    
    if input_type == "Instagram Handle":
        business_input = st.text_input("Instagram", placeholder="@nike", label_visibility="collapsed")
    elif input_type == "Website URL":
        business_input = st.text_input("Website", placeholder="https://tesla.com", label_visibility="collapsed")
    else:
        business_input = st.text_input("Company", placeholder="Nike", label_visibility="collapsed")
    
    st.markdown("---")
    
    if st.button("▶️ Run All", use_container_width=True, type="primary"):
        if business_input:
            st.session_state.run_all = True
            st.session_state.business_input = business_input
            st.rerun()

# Main area
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Pipeline")
    
    steps = [
        ("profile_extraction", "Profile Extraction", "Research using Tavily"),
        ("profile_analyzer", "Profile Analyzer", "Identify subreddits"),
        ("trend_scraper", "Trend Scraper", "Scrape Reddit"),
        ("ranking", "Ranking Agent", "Score relevance"),
        ("report", "Report Generator", "Synthesize insights"),
        ("validator", "Validator", "Verify groundedness"),
        ("summarizer", "Summarizer", "Polish output")
    ]
    
    for i, (step_id, name, desc) in enumerate(steps, 1):
        status = st.session_state.step_results.get(step_id, {}).get('status', 'pending')
        
        badge_color = {
            'success': '#34c759',
            'running': '#007aff', 
            'error': '#ff3b30',
            'pending': '#8e8e93'
        }.get(status, '#8e8e93')
        
        badge_text = {
            'success': '✓ Done',
            'running': '⏳ Running',
            'error': '✗ Error',
            'pending': '○ Pending'
        }.get(status, '○ Pending')
        
        st.markdown(f"""
        <div style="padding: 12px; background: white; border-radius: 10px; margin: 8px 0; 
                    box-shadow: 0 1px 3px rgba(0,0,0,0.08); border-left: 3px solid {badge_color};">
            <div style="font-weight: 600; color: #1d1d1f;">{i}. {name}</div>
            <div style="font-size: 13px; color: #8e8e93;">{desc}</div>
            <div style="margin-top: 8px;"><span style="background: {badge_color}; color: white; padding: 4px 12px; 
                 border-radius: 12px; font-size: 12px; font-weight: 600;">{badge_text}</span></div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### Live Output")
    
    # Show results
    for step_id, name, _ in steps:
        if step_id in st.session_state.step_results:
            result = st.session_state.step_results[step_id]
            with st.expander(f"**{name}**", expanded=result.get('status') == 'success'):
                if 'output' in result:
                    if isinstance(result['output'], dict):
                        st.json(result['output'])
                    else:
                        st.write(result['output'])
                if 'error' in result:
                    st.error(result['error'])

# Execute if Run All clicked
if st.session_state.get('run_all') and business_input:
    st.session_state.run_all = False
    
    # Step 1: Profile Extraction
    st.session_state.step_results['profile_extraction'] = {'status': 'running'}
    st.rerun()
    
    try:
        with st.spinner("Researching business..."):
            # REAL Tavily API call
            search_query = f"{business_input} company profile industry business model"
            search_results = tavily_client.search(query=search_query, max_results=5)
            
            # Extract profile with GPT-4
            profile_prompt = f"""Extract business profile from: {business_input}
Search results: {json.dumps(search_results, indent=2)}
Return JSON: {{"business_name": "...", "industry": "...", "voice": "...", "expertise_areas": [...]}}"""
            
            response = json_llm.invoke([HumanMessage(content=profile_prompt)])
            profile = json.loads(response.content)
            
            st.session_state.step_results['profile_extraction'] = {
                'status': 'success',
                'output': profile
            }
            st.success("✓ Profile extracted!")
            
    except Exception as e:
        st.session_state.step_results['profile_extraction'] = {
            'status': 'error',
            'error': str(e)
        }
        st.error(f"Error: {e}")

st.caption("Marketing Intelligence Agent • CS329T Stanford")
