# 🤖 Automate.sh Content Engine

> **AI-powered short-form video content generation for developers.**  
> Build audience. Sell products. Reach $5,000+/month.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What This Does

Automate.sh Content Engine takes a developer topic and generates:

| Output | Details |
|---|---|
| 🎬 Video Script | 20-40 second, HOOK→PROBLEM→SOLUTION→DEMO→CTA structure |
| 💻 Code Example | Production-quality, max 15 lines, correct language |
| 📢 5 Title Options | Viral-optimized, ranked best-first |
| 🖼️ Thumbnail Text | Max 5 words, high-impact |
| 🏷️ 15 Hashtags | Tiered: broad + niche + brand |
| 📝 SEO Description | 100-word, keyword-optimized |
| ✅ Quality Gate | Auto-retries if score < 7/10 |
| 📁 Markdown File | `output/YYYY-MM-DD-topic.md` |

All in **~60 seconds** per topic.

---

## Pipeline

```
Topic Input
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                   LangGraph Pipeline                     │
│                                                         │
│  Normalize → Research → Script → Code → Titles →       │
│  Thumbnail → Hashtags → Description → Quality Review    │
│                              │                          │
│                    ┌─────────┴──────────┐               │
│                    │  Score >= 7?       │               │
│                    │  Yes → Export      │               │
│                    │  No  → Retry (max 2)│              │
│                    └────────────────────┘               │
└─────────────────────────────────────────────────────────┘
    │
    ▼
output/YYYY-MM-DD-topic.md
```

---

## Quick Start

### 1. Setup

```bash
# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install
pip install -e ".[dev]"

# Configure
cp .env.example .env
```

### 2. Choose Your LLM

**Option A: Ollama (free, local, private)**
```bash
# Install Ollama: https://ollama.ai
ollama pull llama3.2   # or mistral, codellama, qwen2.5-coder

# .env settings:
# LLM_PROVIDER=ollama
# MODEL_NAME=llama3.2
```

**Option B: OpenCode / BigPick (free cloud providers)**
```bash
# .env settings:
# LLM_PROVIDER=opencode
# LLM_API_KEY=your-key
# LLM_BASE_URL=https://your-provider.com/v1
# MODEL_NAME=your-model
```

**Option C: OpenAI (paid, highest quality)**
```bash
# .env settings:
# LLM_PROVIDER=openai
# LLM_API_KEY=sk-...
# MODEL_NAME=gpt-4o-mini
```

### 3. Generate Content

```bash
# Single topic
python cli.py generate --topic "GitHub Actions Cache"

# With options
python cli.py generate \
  --topic "fzf Linux terminal search" \
  --category LINUX \
  --audience "Linux developers"

# Batch from file
python cli.py batch topics.txt

# View history
python cli.py history --limit 20

# Content schedule
python cli.py schedule --days 7

# Statistics
python cli.py stats
```

---

## Output Example

```markdown
# Your CI Is Wasting 8 Minutes Every Run

> Quality Score: 🟢 8/10

## 🎬 Script

Your CI re-downloads the same packages every single run.
That's minutes wasted on every push.
GitHub Actions cache fixes it with three lines of YAML.
Add actions/cache and point it at your node_modules.
Builds go from 8 minutes to under 2.
Follow Automate.sh for daily dev shortcuts.

## 💻 Code Example

- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}

## 🏷️ Hashtags

#automatesh #github #githubactions #devops #cicd ...
```

---

## Project Structure

```
automateSh/
├── app/
│   ├── config.py          # Pydantic Settings (env-based config)
│   └── logger.py          # Structlog + Rich logging
│
├── engine/
│   ├── state.py           # ContentState TypedDict
│   ├── nodes.py           # All 9 agent node functions
│   └── graph.py           # LangGraph with quality retry edge
│
├── providers/
│   ├── base.py            # Abstract LLMProvider
│   ├── ollama.py          # Local Ollama
│   ├── opencode.py        # OpenAI-compatible
│   └── factory.py         # Provider factory + cache
│
├── database/
│   ├── models.py          # SQLAlchemy Topic model
│   └── connection.py      # SQLite engine + session
│
├── prompts/               # 8 prompt templates (markdown)
│   ├── research.md
│   ├── script.md
│   ├── code.md
│   ├── title.md
│   ├── thumbnail.md
│   ├── hashtags.md
│   ├── description.md
│   └── quality_review.md
│
├── output/                # Generated content files
├── content/               # Scripts and published assets
├── tests/                 # Pytest test suite
├── cli.py                 # Rich CLI entry point
└── pyproject.toml         # Dependencies + tooling config
```

---

## Daily Workflow

```bash
# Handled automatically via Docker background worker:
# 1. 08:00 AM: Discovers 10 new trends
# 2. 12:00 PM: Auto-publishes Video 1
# 3. 05:00 PM: Auto-publishes Video 2
# 4. Fridays 09:00 AM: Generates weekly newsletter
```

Time required: **0 min/day (100% Faceless & Autonomous)**.

---

## Content Categories

| Category | Topics |
|---|---|
| `AI_CODING` | AI code review, test generation, PR explanations, Copilot tips |
| `LINUX` | fzf, jq, ripgrep, tmux, ssh config, bash tricks |
| `GITHUB_ACTIONS` | cache, matrix builds, artifacts, reusable workflows, runners |

---

## Coding Standards

- Python 3.12+ with full type hints
- `black` for formatting
- `ruff` for linting
- `pytest` for testing
- Modular architecture — no vendor lock-in
- Provider abstraction — swap LLMs without changing pipeline code

---

## Roadmap

- [x] Phase 1: MVP content generation engine
- [x] Phase 2: LangGraph multi-agent pipeline
- [x] Phase 3: Trend discovery agent (GitHub, HN, Reddit)
- [x] Phase 4: Video asset generator (SRT, voice script, video rendering, auto-publishing)
- [x] Phase 5: Newsletter automation (Automate.sh Weekly)
- [x] Phase 6: Digital product (50 GitHub Actions Templates — $19)
- [ ] Future: SaaS (AI Repository Explainer, AI CI/CD Assistant)

---

*Built with Automate.sh Content Engine — the first product of Automate.sh itself.*
