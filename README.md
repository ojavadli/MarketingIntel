# Agentic Systems for Marketing Intelligence

> **Team**: Anni Zimina, Orkhan Javadli  
> **Course**: CS329T - Trustworthy Machine Learning, Stanford University

A personalized multi-agent system that generates actionable marketing intelligence by analyzing Reddit discussions tailored to a user's professional profile.

---

## 🎯 What It Does

1. **Extracts User Profile** (via SUNet ID)
   - Identifies industry, professional activity, voice, and expertise areas

2. **Scrapes Trending Discussions** (Reddit)
   - Finds relevant discussions in user's industry
   - Extracts pain points, preferences, and sentiment

3. **Ranks by Relevance**
   - Scores communities/threads by audience fit
   - Prioritizes most valuable insights

4. **Generates Intelligence Reports**
   - Synthesizes findings into actionable insights
   - Connects trends to user's professional context

---

## 🏗️ System Architecture

```
Profile Extraction (SUNet ID)
        ↓
    Orchestrator
        ↓
    Profile Analyzer → Trend Scraper → Ranking Agent
                              ↓
                      Report Generator
                              ↓
                         Validator
                              ↓
                        Summarizer
                              ↓
              Intelligence Report Output
```

**6 Specialized Agents**:
1. **Profile Analyzer**: Validates user profile, identifies target subreddits
2. **Trend Scraper**: Scrapes Reddit via Bright Data MCP
3. **Ranking Agent**: Scores discussions by relevance
4. **Report Generator**: Synthesizes insights
5. **Validator**: Ensures groundedness, no hallucinations
6. **Summarizer**: Produces final polished output

See `ARCHITECTURE_REVISED.md` for complete specifications.

---

## 📊 Evaluation Framework

**4 Core Metrics** (LLM Judge via TruLens):

1. **User Identification Relevance** (0-1)
   - How well Profile Analyzer identifies user's industry, activity, voice

2. **Community Relevance** (0-1)
   - How well discovered discussions match target audience

3. **Insight Extraction Quality** (0-1)
   - Completeness and accuracy of pain points/preferences

4. **Trend Relevance** (0-1)
   - How well report engages with actual trending topics

**Note**: Evaluation metrics are for system validation (internal), not user-facing.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Node.js** (for Bright Data MCP server)
- **API Keys**:
  - OpenAI API key
  - Bright Data API key

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure Bright Data MCP
# Add to Cursor settings (Gear → Tools & Integrations → Add Custom MCP):
```

```json
{
  "mcpServers": {
    "brightdata-mcp": {
      "command": "npx",
      "args": ["-y", "@brightdata/mcp"],
      "env": {
        "API_TOKEN": "your_bright_data_api_key"
      }
    }
  }
}
```

### Run the System

```bash
# Open Jupyter notebook
jupyter notebook marketing_intelligence_agent.ipynb
```

---

## 🧪 Test Cases

Example users:

1. **zimina** (ML/AI Research)
   - Subreddits: r/MachineLearning, r/LocalLLaMA
   - Expected: AI agent development trends

2. **Marketing Professional**
   - Subreddits: r/marketing, r/socialmedia
   - Expected: Marketing automation insights

3. **Product Manager**
   - Subreddits: r/SaaS, r/startups
   - Expected: Product management challenges

4. **Content Creator**
   - Subreddits: r/NewTubers, r/podcasting
   - Expected: Audience growth strategies

---

## 📁 Project Structure

```
Project CS329T/
├── ARCHITECTURE_REVISED.md     # Complete system specs
├── README.md                    # This file
├── requirements.txt             # Dependencies
├── marketing_intelligence_agent.ipynb  # Main implementation
├── prompts.py                   # Agent prompts
└── evaluation/
    ├── llm_judges.py           # TruLens evaluation metrics
    └── test_users.json         # Test case definitions
```

---

## ✅ Success Criteria

1. User Identification Relevance ≥ 0.80
2. Community Relevance ≥ 0.75
3. Insight Extraction Quality ≥ 0.80
4. Trend Relevance ≥ 0.75
5. 100% Groundedness (no hallucinations)
6. Execution time < 90 seconds

---

## 🔒 Ethics & Privacy

- Only scrapes publicly available Reddit posts
- No personal information extraction
- Respects Reddit rate limits and ToS
- Insights for legitimate business intelligence only

---

## 📖 Key Differentiators from Homework

| Aspect | Homework | This Project |
|--------|----------|--------------|
| **Personalization** | Generic queries | User profile-based |
| **Data Sources** | Web search (Tavily) | Reddit only (Bright Data) |
| **Agents** | 3 | 6 |
| **Evaluation** | GPA + RAG (7 metrics) | Domain-specific (4 metrics) |
| **Output** | Research reports | Personalized intelligence |

---

**Built with**: 🤖 OpenAI GPT-4 • 📱 Bright Data MCP • 📊 TruLens • 🦜 LangGraph
