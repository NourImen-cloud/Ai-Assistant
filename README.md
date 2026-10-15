# Echo Mind — Personal AI Copilot for Windows

<div align="center">

**An advanced, privacy-first personal AI copilot that lives on your Windows PC.**  
Document Brain • Deep Web Research • Data Analytics & Auto-Charting • PC Diagnostics • Agenda & Email • Ultra-Fast Voice Mode

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.4+-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

</div>

---

## 🌟 Overview

**Echo Mind** connects modern LLMs (Groq, Ollama, OpenAI) directly to your Windows computer through a suite of safe, predefined system tools. 

Unlike basic assistants that only launch apps, Echo Mind acts as a **true daily copilot**: it digests long PDFs, writes and runs data analyses on spreadsheets, generates charts, searches the web without browser popups, diagnoses PC hardware health, cleans system bloat, and manages your personal agenda.

```
You (Text or Voice) → Echo Mind Agent → Tool Execution (Local OS) → Real-Time Streamed Output
```

---

## 🚀 Core Productivity Pillars

### 1. 🧠 Document & File Brain (`documents.py`)
* **Local Document Reading:** Extracts text from local **PDFs** (page-by-page via `pypdf`), **Word documents (`.docx`)**, Markdown, text files, and source code.
* **Executive Summarization:** Summarizes lengthy contracts, reports, or research papers with targeted takeaways.
* **Smart Search:** Searches all documents inside your folders for specific keywords or concepts and quotes matching passages.

### 2. 🌐 Headless Deep Web Research (`research.py`)
* **Multi-Source Synthesis:** Conducts web research using `duckduckgo-search` and `BeautifulSoup` to extract clean paragraphs without opening browser windows.
* **Side-by-Side Comparisons:** Synthesizes pros/cons tables and comparisons for tech stacks, products, and services.
* **Visual Browser Automation (Playwright):** Launches Chromium when interactive browser control, form filling, or UI navigation is required.

### 3. 📊 Data Analytics & Automated Charting (`analytics.py`)
* **Pandas Dataset Analysis:** Computes summary statistics, missing values, dimensions, and data types for `.csv` and `.xlsx` files.
* **Automatic Chart Generation:** Plots bar charts, line graphs, scatter plots, histograms, and pie charts using `matplotlib` and saves them to `data/charts/`.

### 4. 💻 Developer & PC Hardware Diagnostics (`system_tools.py`)
* **Live System Monitoring:** Reports CPU usage, RAM utilization (GB used/available), and disk space across all drives via `psutil`.
* **Process Hog Detection:** Identifies the top 5 memory-heavy background processes.
* **Temp Cleaner:** Scans Windows `%TEMP%` junk files and safely cleans them to reclaim storage.
* **Code Scaffolder:** Generates starter boilerplates for **FastAPI**, **React Vite**, or **Python CLI** projects.

### 5. 📅 Agenda, To-Do & Email Copilot (`agenda.py`)
* **Daily Morning Briefing:** Aggregates date, pending to-do tasks, scheduled appointments, and PC health in one glance.
* **Task Manager:** Adds, lists, and completes tasks in a local SQLite database (`data/memory.db`).
* **Calendar Scheduler:** Schedules meetings, appointments, and deadlines.
* **Email Drafter:** Generates formatted emails with selectable tones (professional, friendly, concise, assertive).

### 6. 🎙️ Ultra-Low-Latency Voice & Streaming
* **Groq Whisper Turbo (~150ms):** Sub-second speech-to-text with automatic fallback to Google STT.
* **Non-Blocking TTS Speech:** Runs text-to-speech in background threads so the UI never freezes while the PC speaks.
* **Real-Time Token Streaming (SSE):** Chat responses start typing on screen in **~150ms**.

---

## 🖥️ Echo Mind Desktop Interface

The frontend is a custom desktop workspace featuring:
* **Live PC Resource Gauges:** Real-time CPU and RAM percentage metrics in the top header.
* **Fluid Organic Vortex Canvas:** An animated neon soundwave visualizer that reacts to voice interactions.
* **Personalized for Nour:** Custom user profile, agenda widget, and quick productivity hubs.
* **Tabbed Studio Views:**
  * 🏠 **Dashboard:** Quick action cards, 6 productivity hubs, agenda preview, and voice visualizer.
  * 💬 **Chat Studio:** Full-width streaming chat stream with prompt suggestions.
  * 🎙️ **Voice Assessment:** Dedicated hands-free audio studio.
  * 📅 **Tasks & Agenda:** Interactive To-Do checklist and calendar events manager.
  * ⚙️ **Workflows & Tools:** Automated multi-step sequence triggers.

---

## 📁 Architecture

```
AIassistant/
├── api/
│   └── server.py             # FastAPI backend (SSE streaming, CORS, voice, system endpoints)
├── assistant/
│   ├── agent.py              # LLM agent orchestration, loop guards, streaming & memory sync
│   ├── config.py             # App configuration, provider settings & paths
│   ├── llm.py                # Groq / Ollama / OpenAI unified client
│   ├── memory/
│   │   └── store.py          # SQLite memory (preferences, projects, history, todos, events)
│   ├── tools/
│   │   ├── agenda.py         # Tasks, calendar scheduling, email drafter & daily briefing
│   │   ├── analytics.py      # Pandas data analysis & Matplotlib chart generation
│   │   ├── applications.py   # Windows desktop application launcher and process manager
│   │   ├── automation.py     # PyAutoGUI mouse/keyboard control & screenshots
│   │   ├── browser.py        # Playwright headless/visual browser automation
│   │   ├── documents.py      # PDF, DOCX, text reading, summarization & search
│   │   ├── email_tools.py    # Gmail IMAP/SMTP reader, direct draft saver & sender
│   │   ├── files.py          # File system management with confirmation safeguards
│   │   ├── memory_tools.py   # Memory CRUD operations
│   │   ├── paths.py          # Path security and resolution
│   │   ├── registry.py       # Central tool registry and execution dispatcher
│   │   ├── research.py       # Headless deep web research & comparisons
│   │   ├── system_tools.py   # Hardware diagnostics, temp cleaner & project scaffolder
│   │   └── websites.py       # URL opener
│   ├── voice/
│   │   ├── stt.py            # Whisper Turbo + Google STT fallback
│   │   └── tts.py            # Pyttsx3 speech engine
│   └── workflows/
│       └── engine.py         # Multi-step automated sequences (e.g. dev_environment)
├── data/                     # Local SQLite DB (`memory.db`) & generated charts (`charts/`)
├── frontend/                 # React + Vite desktop dashboard
├── main.py                   # CLI entry point
└── requirements.txt          # Python dependencies
```

---

## ⚡ Quickstart

### 1. Prerequisites
* **Python 3.11+**
* **Node.js 18+** (for the desktop UI)
* (Optional) **Ollama** if running 100% offline, or a free **Groq** API key for instant responses.

### 2. Installation

Clone or open the repository:

```powershell
cd c:\Users\lenovo\Documents\AIassistant
```

Install Python dependencies:

```powershell
pip install -r requirements.txt
playwright install chromium
```

Install Frontend dependencies:

```powershell
cd frontend
npm install
cd ..
```

### 3. Configuration (`.env`)

Configure your provider in `.env` (defaults to Groq high-speed free tier):

```ini
# LLM Provider: 'groq' (recommended, ~300 tokens/sec) or 'ollama' (local)
LLM_PROVIDER=groq

# Groq (Get a free key at https://console.groq.com)
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-120b

# Ollama settings (for local usage)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.1:8b

# API server
API_HOST=127.0.0.1
API_PORT=8000

# Gmail Integration (Direct inbox reading & automatic drafts)
# Generate a 16-character App Password at: https://myaccount.google.com/apppasswords
GMAIL_ADDRESS=your.email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

---

## 🎮 Running Echo Mind

### Option A: Desktop Web Workspace (Recommended)

**Terminal 1 (Backend API):**
```powershell
python api/server.py
```

**Terminal 2 (Frontend Dashboard):**
```powershell
cd frontend
npm run dev
```

Open **`http://localhost:5173`** in your browser.

### Option B: Terminal CLI

```powershell
python main.py
```

For continuous voice mode in the terminal:
```powershell
python main.py --voice
```

---

## 💡 Example Prompts to Try

| Category | Example Command |
|---|---|
| **Document Brain** | *"Summarize the PDF file on my desktop and give me the 3 main takeaways."* |
| **Deep Research** | *"Deep research the difference between SQLite and PostgreSQL for desktop apps."* |
| **Data & Charts** | *"Inspect `data/test_sample.csv` and generate a bar chart of Score by Metric."* |
| **PC Health** | *"Check my system resources and tell me what is consuming the most RAM."* |
| **Disk Cleanup** | *"Scan my temp folder and tell me how much disk space can be reclaimed."* |
| **Agenda & Tasks** | *"Give me my daily briefing."* |
| **Todo Manager** | *"Add a task to submit the AI project proposal due Friday."* |
| **Email Drafter** | *"Draft a professional email to my manager requesting a project review next Tuesday."* |
| **Code Scaffolding** | *"Scaffold a FastAPI project called 'payment_service' on my desktop."* |
| **Workflows** | *"Run the dev_environment workflow."* |

---

## 🛡️ Security & Privacy

* **Sandbox Safety:** File tools are constrained to your user home directory to prevent unintended system modifications.
* **Confirmation Required:** Destructive operations (like file deletion) require explicit user confirmation.
* **Local Memory:** Conversation history, to-do tasks, and preferences remain local in SQLite (`data/memory.db`).
* **Tool Whitelisting:** The LLM cannot execute arbitrary PowerShell/CMD strings — all actions pass through strictly validated tool handlers.

---
