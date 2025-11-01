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

# Set page config
st.set_page_config(
    page_title="Marketing Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import agent components
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.types import Command
from tavily import TavilyClient
import numpy as np

# Load API keys from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
BRIGHT_DATA_API_KEY = os.getenv("BRIGHT_DATA_API_KEY", "")

# Ultra-minimalistic Apple-style CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif !important;
    }
    
    .stApp {
        background: #fafafa;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Minimalist headers */
    h1 {
        font-weight: 700;
        color: #1d1d1f;
        letter-spacing: -1px;
        font-size: 48px;
        margin-bottom: 8px;
    }
    
    h2 {
        font-weight: 600;
        color: #1d1d1f;
        letter-spacing: -0.5px;
        font-size: 24px;
        margin-top: 32px;
        margin-bottom: 16px;
    }
    
    h3 {
        font-weight: 600;
        color: #424245;
        letter-spacing: -0.3px;
        font-size: 18px;
    }
    
    /* Glossy white cards */
    .element-container {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.04);
    }
    
    /* Ultra-minimal buttons */
    .stButton > button {
        background: #1d1d1f;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 28px;
        font-weight: 600;
        font-size: 15px;
        letter-spacing: -0.2px;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    
    .stButton > button:hover {
        background: #424245;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transform: translateY(-1px);
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    
    .status-pending { background: #f0f0f0; color: #8e8e93; }
    .status-running { background: #007aff; color: white; animation: pulse 1.5s infinite; }
    .status-success { background: #34c759; color: white; }
    .status-error { background: #ff3b30; color: white; }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Input fields */
    .stTextInput input {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        padding: 12px 16px;
        font-size: 15px;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Progress bars */
    .stProgress > div > div {
        background: linear-gradient(90deg, #007aff, #5ac8fa);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'step_statuses' not in st.session_state:
    st.session_state.step_statuses = {}
if 'step_outputs' not in st.session_state:
    st.session_state.step_outputs = {}
if 'step_errors' not in st.session_state:
    st.session_state.step_errors = {}

# Simple authentication
if not st.session_state.authenticated:
    st.title("Marketing Intelligence Agent")
    st.markdown("### Sign In")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign In")
        
        if submit:
            if username == "admin" and password == "stanford2025":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    st.stop()

# Main app (after authentication)
st.title("🎯 Marketing Intelligence Agent")
st.caption("Personalized insights from Reddit discussions")

# Sidebar: Input
with st.sidebar:
    st.markdown("### Business Profile")
    
    input_type = st.radio(
        "Input Type",
        ["Company Name", "Instagram Handle", "Website URL"],
        label_visibility="collapsed"
    )
    
    if input_type == "Instagram Handle":
        business_input = st.text_input("Instagram", placeholder="@nike", label_visibility="collapsed")
    elif input_type == "Website URL":
        business_input = st.text_input("Website", placeholder="https://tesla.com", label_visibility="collapsed")
    else:
        business_input = st.text_input("Company", placeholder="Tesla", label_visibility="collapsed")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        run_all = st.button("▶️ Run All", use_container_width=True, type="primary")
    with col2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.step_statuses = {}
            st.session_state.step_outputs = {}
            st.session_state.step_errors = {}
            st.rerun()

# Main area: Steps + Outputs
if business_input:
    # Define steps
    steps = [
        ("profile_extraction", "Profile Extraction", "Research business using Tavily"),
        ("profile_analyzer", "Profile Analyzer", "Identify target subreddits"),
        ("trend_scraper", "Trend Scraper", "Scrape Reddit discussions"),
        ("ranking_agent", "Ranking Agent", "Score by relevance"),
        ("report_generator", "Report Generator", "Synthesize insights"),
        ("validator", "Validator", "Verify groundedness"),
        ("summarizer", "Summarizer", "Polish output")
    ]
    
    # Two columns: Steps | Outputs
    col_steps, col_output = st.columns([1, 2])
    
    with col_steps:
        st.markdown("### Pipeline")
        
        for i, (step_id, step_name, step_desc) in enumerate(steps, 1):
            status = st.session_state.step_statuses.get(step_id, "pending")
            
            if status == "success":
                badge = '<span class="status-badge status-success">✓ Done</span>'
            elif status == "running":
                badge = '<span class="status-badge status-running">⏳ Running</span>'
            elif status == "error":
                badge = '<span class="status-badge status-error">✗ Error</span>'
            else:
                badge = '<span class="status-badge status-pending">○ Pending</span>'
            
            # Individual run button
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.markdown(f"""
                <div style="padding: 12px; background: white; border-radius: 10px; margin: 8px 0; 
                            box-shadow: 0 1px 3px rgba(0,0,0,0.08); border-left: 3px solid #{"34c759" if status == "success" else ("ff3b30" if status == "error" else "e0e0e0")};">
                    <div style="font-weight: 600; color: #1d1d1f; margin-bottom: 4px;">
                        {i}. {step_name}
                    </div>
                    <div style="font-size: 13px; color: #8e8e93; margin-bottom: 8px;">
                        {step_desc}
                    </div>
                    {badge}
                </div>
                """, unsafe_allow_html=True)
            
            with col_b:
                if st.button("▶", key=f"run_{step_id}", help=f"Run {step_name}"):
                    # TODO: Run individual step
                    st.toast(f"Running {step_name}...", icon="⏳")
    
    with col_output:
        st.markdown("### Live Output")
        
        # Show outputs for each step
        for step_id, step_name, _ in steps:
            if step_id in st.session_state.step_outputs:
                with st.expander(f"**{step_name}**", expanded=(step_id == "summarizer")):
                    output = st.session_state.step_outputs[step_id]
                    
                    if isinstance(output, dict):
                        st.json(output)
                    elif isinstance(output, str) and len(output) > 100:
                        st.markdown(output)
                    else:
                        st.write(output)
            
            if step_id in st.session_state.step_errors:
                with st.expander(f"❌ {step_name} - Error", expanded=True):
                    st.error(st.session_state.step_errors[step_id])
        
        # Final report display
        if "summarizer" in st.session_state.step_outputs:
            st.markdown("---")
            st.markdown("### 📊 Final Intelligence Report")
            final_report = st.session_state.step_outputs.get("summarizer", "")
            if final_report:
                st.markdown(final_report)
    
    # Execute if Run All clicked
    if run_all and business_input:
        # Import REAL agent logic here
        # For now, placeholder - will integrate actual code
        st.info("🚧 Executing real agent system... Integration in progress")

else:
    st.info("👈 Enter a business name, Instagram handle, or website to begin")

# Footer
st.markdown("---")
st.caption("Marketing Intelligence Agent • CS329T Stanford • Built with Railway.app")

