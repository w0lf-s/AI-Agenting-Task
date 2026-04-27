# 🎫 AI Customer Support Ticket Classifier

An AI-powered system that automatically classifies customer support messages by **category** and **priority** using the OpenAI API (`gpt-4o-mini`). Built with Python and Flask.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-gpt--4o--mini-412991?logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Table of Contents

- [Demo](#-demo)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Setup](#-setup)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [How It Works](#-how-it-works)
- [Error Handling](#-error-handling)
- [Running Tests](#-running-tests)

---

## 🎬 Demo

**Input:**
```json
[
  "My payment got deducted but service is not activated",
  "App crashes every time I login",
  "How to change my email address?"
]
```

**Output:**
```json
[
  {
    "message": "My payment got deducted but service is not activated",
    "category": "Billing",
    "priority": "High"
  },
  {
    "message": "App crashes every time I login",
    "category": "Technical Issue",
    "priority": "High"
  },
  {
    "message": "How to change my email address?",
    "category": "Account",
    "priority": "Low"
  }
]
```

---

## ✨ Features

- **AI Classification** — Uses `gpt-4o-mini` to understand message intent and classify accurately
- **REST API** — Flask server exposes a `/classify` endpoint for easy integration
- **Input Validation** — Rejects empty, malformed, or missing inputs with clear error messages
- **Output Validation** — Validates every AI response against allowed categories and priorities
- **Retry Logic** — Exponential backoff on rate limits (1s → 2s → 4s)
- **Structured JSON** — Clean, consistent output format every time
- **Standalone Mode** — Run directly as a script without the API server

---

## 📁 Project Structure

```
support-classifier/
├── classifier.py        # Core AI classification logic
├── app.py               # Flask REST API wrapper
├── test_classifier.py   # Unit tests (no API key required)
├── output.json          # Sample output
├── requirements.txt     # Dependencies
└── README.md
```

---

## ⚙️ Setup

### Prerequisites
- Python 3.10 or higher
- An OpenAI API key → [Get one here](https://platform.openai.com/api-keys)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/support-classifier.git
cd support-classifier
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your API key

Open `classifier.py` and replace the key on the last few lines:

```python
classifier = SupportClassifier(api_key="sk-your-openai-key-here")
```

Or set it as an environment variable:

```bash
# Mac/Linux
export OPENAI_API_KEY="sk-your-key-here"

# Windows (Command Prompt)
set OPENAI_API_KEY=sk-your-key-here

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-your-key-here"
```

---

## 🚀 Usage

### Option A — Run as a script

```bash
python classifier.py
```

Classifies the built-in sample messages, prints results, and saves to `output.json`.

### Option B — Run as a REST API

**Terminal 1** — Start the server:
```bash
python app.py
```

**Terminal 2** — Send a request:

**Mac/Linux:**
```bash
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{"messages": ["My payment failed", "App keeps crashing", "How do I reset my password?"]}'
```

**Windows PowerShell:**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/classify -Method POST -ContentType "application/json" -Body '{"messages": ["My payment failed", "App keeps crashing", "How do I reset my password?"]}'
```

---

## 📡 API Reference

### `POST /classify`

Classifies a list of support messages.

**Request body:**
```json
{
  "messages": ["string", "string", "..."]
}
```

**Response `200 OK`:**
```json
[
  {
    "message": "original message text",
    "category": "Billing | Technical Issue | Account | General Inquiry",
    "priority": "High | Medium | Low"
  }
]
```

**Error responses:**

| Status | Reason |
|--------|--------|
| `400` | Missing or malformed request body |
| `422` | Valid JSON but invalid message data |
| `500` | Classification failed (API error) |

### `GET /health`

Returns server status.

```json
{ "status": "ok" }
```

---

## 🧠 How It Works

### Classification Logic

Each message is sent to `gpt-4o-mini` with a system prompt that defines the categories and priority rules. The model returns a JSON object which is then validated before being returned to the caller.

```
User message
     │
     ▼
System prompt + message → OpenAI gpt-4o-mini
     │
     ▼
Raw JSON response
     │
     ▼
Schema validation (category + priority)
     │
     ▼
Structured output
```

### Categories

| Category | Covers |
|----------|--------|
| `Billing` | Payment failures, double charges, refunds, invoices, subscriptions |
| `Technical Issue` | Crashes, bugs, slow performance, outages, errors |
| `Account` | Login issues, password reset, profile settings, email changes |
| `General Inquiry` | How-to questions, feature requests, non-urgent information |

### Priority Levels

| Priority | Criteria |
|----------|----------|
| `High` | Blocking issues — service down, payment failed, can't log in |
| `Medium` | Impactful but not blocking — bugs with workarounds |
| `Low` | Informational, how-to questions, non-urgent requests |

### Key Design Decisions

**`temperature=0`** — Makes classification deterministic. The same message always returns the same result, which is essential for a reliable classifier.

**`response_format: json_object`** — Forces the model to return valid JSON, eliminating failures from markdown-wrapped responses.

**`gpt-4o-mini`** — Fast and cost-effective. Classification doesn't require the full power of GPT-4o.

**`max_tokens=60`** — The JSON response is small. Capping tokens reduces cost and latency.

---

## 🛡️ Error Handling

| Scenario | Handling |
|----------|----------|
| Rate limit (429) | Exponential backoff — retries after 1s, 2s, 4s |
| Invalid JSON from API | Caught, re-raised with context |
| Unexpected category/priority | Validated against allowed sets, raises `ValueError` |
| Empty message list | Raises `ValueError` with clear message |
| Missing API key | Raises `ValueError` on startup |
| Network/API error | Caught and returned as `500` with details |

---

## 🧪 Running Tests

Unit tests use mocks — no API key or internet connection needed:

```bash
python -m pytest test_classifier.py -v
```

**Test coverage includes:**
- Valid category and priority combinations
- Invalid category rejection
- Invalid priority rejection
- Empty list input guard
- Non-string message guard
- Full classify pipeline with mocked API
- Output key structure validation

---

## 📄 License

MIT License — free to use, modify, and distribute.
