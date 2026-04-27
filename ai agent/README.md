# AI Customer Support Ticket Classifier

Classifies customer support messages by **category** and **priority** using the OpenAI API (`gpt-4o-mini`).

## Output Example

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

## Setup

### 1. Clone and install

```bash
git clone <your-repo-url>
cd support-classifier
pip install -r requirements.txt
```

### 2. Set your OpenAI API key

```bash
export OPENAI_API_KEY="sk-..."
```

### 3. Run the classifier

```bash
python classifier.py
```

Results are printed to stdout and saved to `output.json`.

### 4. Run as a REST API (optional)

```bash
python app.py
```

Then POST to `http://localhost:5000/classify`:

```bash
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{"messages": ["My payment failed", "App keeps crashing"]}'
```

### 5. Run tests

```bash
python -m pytest test_classifier.py -v
```

---

## Project Structure

```
support-classifier/
├── classifier.py        # Core classification logic
├── app.py               # Flask REST API wrapper
├── test_classifier.py   # Unit tests (no API key needed)
├── output.json          # Sample output
├── requirements.txt
└── README.md
```

## Approach

### Classification
Each message is sent to `gpt-4o-mini` with a structured system prompt that defines the four categories and three priority levels with clear rules. `temperature=0` ensures deterministic output. `response_format: json_object` forces valid JSON responses.

### Error Handling
- **Rate limits**: exponential backoff (1s → 2s → 4s) with up to 3 retries
- **Invalid JSON**: caught and re-raised with context
- **Schema validation**: category and priority values are validated against allowed sets
- **Input validation**: empty lists, non-string messages, and missing API keys raise clear errors

### Design Decisions
- `gpt-4o-mini` — fast and cheap, sufficient for classification tasks
- `temperature=0` — reproducible results for the same input
- `response_format: json_object` — eliminates JSON parsing failures
- Single API call per message — simple, debuggable, and easy to parallelize later

## Categories & Priority Logic

| Category | Examples |
|---|---|
| Billing | Payment failures, double charges, refunds, invoices |
| Technical Issue | Crashes, bugs, slow performance, outages |
| Account | Login, password reset, profile settings, email change |
| General Inquiry | How-to questions, feature requests, non-urgent info |

| Priority | Criteria |
|---|---|
| High | Blocking issues — can't use the service, payment problem |
| Medium | Impactful but not blocking — bugs with workarounds |
| Low | Informational, how-to, non-urgent requests |
