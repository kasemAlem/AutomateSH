# **Automate.sh \- AI Business Implementation Blueprint v1.0**

## **Objective**

Build a **fully faceless AI-powered content business** that publishes short-form videos about:

* AI Coding Assistants  
* Linux Productivity  
* GitHub Actions & CI/CD

The system should automate as much as possible using **LangGraph** and open-source tools.

**Target:**

* 2 videos/day  
* 60 videos/month  
* Build audience  
* Sell digital products  
* Eventually launch SaaS  
* Reach $5,000+/month

---

# **Phase 1: MVP**

## **Goal**

Build a content generation engine.

Input:

```
Topic
```

Output:

```
Video Title
Video Script
Code Example
Video Description
Hashtags
Thumbnail Text
Markdown File
```

---

# **Technology Stack**

## **Language**

* Python 3.12+

---

## **AI Framework**

* LangGraph  
* LangChain

---

## **LLM**

Priority order:

* OpenCode  
* BigPick (free providers)  
* Ollama fallback  
* Any OpenAI-compatible endpoint

The LLM provider should be abstracted.

Create:

```py
class LLMProvider:
    def generate(prompt)
```

so providers can be swapped easily.

---

## **Storage**

```
PostgreSQL (Docker)
```
*(Note: Initially SQLite was planned, but upgraded to PostgreSQL for production readiness)*

---

## **Configuration**

Use:

```
.env
```

Variables:

```
LLM_PROVIDER=
LLM_API_KEY=
MODEL_NAME=
DATABASE_URL=
```

---

## **Project Structure**

```
automate-sh-content-engine/

├── app/
│
├── langgraph/
│   ├── graph.py
│   ├── nodes.py
│   ├── state.py
│
├── prompts/
│   ├── research.md
│   ├── script.md
│   ├── title.md
│   ├── hashtags.md
│   ├── code.md
│
├── providers/
│   ├── base.py
│   ├── opencode.py
│   ├── ollama.py
│
├── database/
│
├── output/
│
├── content/
│   ├── scripts/
│   ├── published/
│
├── cli.py
│
├── .env
│
└── README.md
```

---

# **Phase 2: LangGraph Workflow**

Build the following graph:

```
                 Start
                   |
                   V
           Topic Normalizer
                   |
                   V
            Research Agent
                   |
                   V
          Script Writer Agent
                   |
                   V
          Code Example Agent
                   |
                   V
            Title Generator
                   |
                   V
        Thumbnail Text Agent
                   |
                   V
          Hashtag Generator
                   |
                   V
         Description Generator
                   |
                   V
             Markdown Export
                   |
                   V
                 End
```

---

# **Graph State**

```py
class ContentState:
    topic
    audience
    research
    script
    code_example
    title
    thumbnail
    hashtags
    description
    markdown_path
```

---

# **Agent Definitions**

---

## **Agent 1**

### **Research Agent**

Input:

```
GitHub Actions cache
```

Output:

```
Problem developers face

Why it matters

Best practice

Interesting fact
```

---

## **Agent 2**

### **Script Writer**

Create:

20-40 second script.

Structure:

```
HOOK

PROBLEM

SOLUTION

QUICK DEMO

CTA
```

Example:

```
Stop waiting for your CI pipeline.

GitHub cache can save minutes every build.

Add these three lines.

(Show code)

Your builds become much faster.

Follow Automate.sh.
```

---

## **Agent 3**

### **Code Generator**

Generate a realistic example.

Example:

```
- uses: actions/cache@v4
```

Requirements:

* production quality  
* syntactically valid  
* short enough for video

---

## **Agent 4**

### **Title Generator**

Generate 5 titles.

Example:

```
GitHub Actions Secret Nobody Uses

This One YAML Line Saves Minutes

Speed Up CI With One Trick
```

---

## **Agent 5**

### **Thumbnail Generator**

Generate:

Maximum 5 words.

Examples:

```
Stop Slow CI

AI Writes My Code

Linux Hack
```

---

## **Agent 6**

### **Hashtag Generator**

Generate:

```
#github
#devops
#linux
#automation
#aicoding
```

---

## **Agent 7**

### **Description Generator**

Generate SEO-friendly description.

Maximum:

100 words.

---

# **Export Format**

Generate:

```
# Title

...

# Script

...

# Code

...

# Description

...

# Hashtags

...
```

Save to:

```
output/YYYY-MM-DD-topic.md
```

---

# **CLI**

Implement:

## **Generate content**

```shell
python cli.py generate \
--topic "GitHub Actions Cache"
```

---

## **Generate batch**

```shell
python cli.py batch \
--file topics.txt
```

---

## **List history**

```shell
python cli.py history
```

---

# **Content Strategy Database**

Create table:

```sql
topics

id
title
category
difficulty
status
created_at
```

Categories:

```
AI_CODING
LINUX
GITHUB_ACTIONS
```

Status:

```
TODO
GENERATED
RECORDED
PUBLISHED
```

---

# **Phase 3**

## **Trend Agent**

Daily:

Generate 10 new ideas.

Based on:

* GitHub  
* Hacker News  
* Reddit  
* Dev.to  
* AI trends

Store them automatically.

---

# **Phase 4**

## **Video Asset Generator (✅ FULLY AUTOMATED)**

Generate:

```
voice.txt
subtitles.srt
thumbnail.txt
recording_notes.md
```
*(Implemented: `audio/tts.py` and `video/builder.py` fully handle TTS, subtitles, and video generation)*

---

# **Recording & Publishing Workflow (✅ FULLY AUTOMATED)**

**PREVIOUS MANUAL WORKFLOW:**
~~Human does:~~
~~Step 1: Open markdown.~~
~~Step 2: Record terminal (OBS).~~
~~Step 3: Generate AI voice.~~
~~Step 4: Import to CapCut.~~
~~Step 5: Export.~~
~~Step 6: Publish.~~

**NEW AUTOMATED WORKFLOW:**
System executes:
1. `cli.py auto-publish` fetches oldest `TODO` topic from PostgreSQL.
2. LangGraph pipeline generates script and code.
3. `tts.py` generates voiceover using OpenAI.
4. `video/builder.py` renders syntax-highlighted code video syncing with TTS.
5. Composio SDK automatically uploads and publishes to TikTok (`social/tiktok.py`).
6. Topic status updated to `PUBLISHED` in database.

---

# **Daily Workflow (✅ READY)**

Every morning (via cron job):

```
python cli.py trends
python cli.py auto-publish
```

Time required:
```
0 minutes/day (100% Faceless & Autonomous)
```

---

# **First 100 Videos Plan**

## **AI Coding Assistant (40)**

Examples:

* AI reviews PRs  
* AI generates tests  
* AI explains repositories  
* AI writes Bash scripts  
* AI fixes Dockerfiles

---

## **Linux (30)**

Examples:

* fzf  
* xargs  
* jq  
* ripgrep  
* rsync  
* tmux  
* ssh config

---

## **GitHub Actions (30)**

Examples:

* matrix builds  
* cache  
* artifacts  
* reusable workflows  
* release automation  
* AI release notes  
* self-hosted runners

---

# **Phase 5**

## **Newsletter**

Create:

```
Automate.sh Weekly
```

Every Friday.

Use generated content.

---

# **Phase 6**

## **First Digital Product**

Create:

```
50 GitHub Actions Templates
```

Contents:

* CI  
* CD  
* Docker  
* Go  
* Python  
* AI workflows

Price:

```
$19
```

---

# **Future SaaS**

Do NOT build before audience exists.

Potential products:

* AI Repository Explainer  
* AI GitHub Action Generator  
* AI Release Notes Generator  
* AI CI/CD Assistant

---

# **Coding Standards**

* Python type hints  
* Black  
* Ruff  
* Pytest  
* Modular architecture  
* Provider abstraction  
* No vendor lock-in

---

# **Development Milestones**

## **Week 1**

* Project skeleton  
* LangGraph  
* LLM provider  
* CLI

---

## **Week 2**

* All agents  
* Markdown export  
* SQLite

---

## **Week 3**

* Batch generation  
* Trend agent  
* Topic database

---

## **Week 4**

* Produce first 30 videos  
* Publish daily  
* Collect analytics

---

# **Success Criteria**

After 30 days:

```
60 published videos

1000 followers

100 email subscribers

1 digital product

First sale

Working LangGraph automation engine
```

---

# **Final instruction for AI IDE**

**Build this project incrementally.**

Priorities:

1. Working LangGraph pipeline.  
2. Provider abstraction.  
3. Markdown output.  
4. CLI interface.  
5. Topic database.  
6. Batch generation.  
7. Future extensibility.

**Do not over-engineer. Deliver a working MVP first, then iterate.**

I would actually treat this repository as the **first product of Automate.sh itself**, because later you can open-source part of it and sell a "Pro Content Engine" version.
