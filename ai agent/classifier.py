"""
AI-Driven Customer Support Ticket Classifier
Uses OpenAI API to classify messages by category and priority.
"""

import json
import os
import sys
import time
from typing import Optional
from openai import OpenAI, RateLimitError, APIError

# ── Configuration ─────────────────────────────────────────────────────────────

VALID_CATEGORIES = {"Billing", "Technical Issue", "Account", "General Inquiry"}
VALID_PRIORITIES = {"High", "Medium", "Low"}

SYSTEM_PROMPT = """You are a customer support ticket classifier.

Classify the given message into exactly one category and one priority level.

Categories:
- Billing: payment issues, charges, invoices, subscriptions, refunds
- Technical Issue: bugs, crashes, errors, performance problems, outages
- Account: login, password, profile settings, email changes, account access
- General Inquiry: how-to questions, feature requests, general information

Priority:
- High: urgent or blocking issues (payment failures, service down, can't access account)
- Medium: moderate issues that impact usage but have workarounds (bugs, errors)
- Low: general or informational queries (how-to, settings, non-urgent questions)

Return ONLY valid JSON with no extra text, no markdown, no explanation:
{
  "category": "<one of the four categories>",
  "priority": "<High|Medium|Low>"
}"""


# ── Core Classifier ───────────────────────────────────────────────────────────

class SupportClassifier:
    def __init__(self, api_key: Optional[str] = None):
        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError(
                "OpenAI API key not found. "
                "Set the OPENAI_API_KEY environment variable or pass it directly."
            )
        self.client = OpenAI(api_key=key)

    def _classify_single(self, message: str, retries: int = 3) -> dict:
        """Call OpenAI API to classify one message, with retry on rate limit."""
        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f'Message: "{message}"'},
                    ],
                    temperature=0,
                    max_tokens=60,
                    response_format={"type": "json_object"},
                )
                raw = response.choices[0].message.content.strip()
                result = json.loads(raw)
                return self._validate(result)

            except RateLimitError:
                if attempt < retries - 1:
                    wait = 2 ** attempt
                    print(f"  Rate limited. Retrying in {wait}s...", file=sys.stderr)
                    time.sleep(wait)
                else:
                    raise
            except json.JSONDecodeError as e:
                raise ValueError(f"OpenAI returned invalid JSON: {raw!r}") from e
            except APIError as e:
                raise RuntimeError(f"OpenAI API error: {e}") from e

    def _validate(self, result: dict) -> dict:
        """Validate and sanitise the LLM's JSON response."""
        category = result.get("category", "").strip()
        priority = result.get("priority", "").strip()

        if category not in VALID_CATEGORIES:
            raise ValueError(
                f"Unexpected category '{category}'. "
                f"Expected one of: {', '.join(sorted(VALID_CATEGORIES))}"
            )
        if priority not in VALID_PRIORITIES:
            raise ValueError(
                f"Unexpected priority '{priority}'. "
                f"Expected one of: {', '.join(sorted(VALID_PRIORITIES))}"
            )
        return {"category": category, "priority": priority}

    def classify(self, messages: list[str]) -> list[dict]:
        """Classify a list of messages and return structured output."""
        if not isinstance(messages, list) or not messages:
            raise ValueError("`messages` must be a non-empty list of strings.")

        results = []
        for i, message in enumerate(messages, 1):
            if not isinstance(message, str) or not message.strip():
                raise ValueError(f"Message at index {i-1} is empty or not a string.")

            print(f"  [{i}/{len(messages)}] Classifying: {message[:60]}...")
            classification = self._classify_single(message.strip())
            results.append({
                "message": message,
                "category": classification["category"],
                "priority": classification["priority"],
            })

        return results


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    messages = [
        "My payment got deducted but service is not activated",
        "App crashes every time I login",
        "How to change my email address?",
        "I was charged twice for the same subscription",
        "The dashboard is loading very slowly since yesterday",
        "Can I upgrade my plan to Pro?",
        "I can't reset my password — the email never arrives",
        "When will the iOS app support dark mode?",
    ]

    print("=" * 60)
    print("  Customer Support Ticket Classifier (OpenAI)")
    print("=" * 60)
    print(f"\nProcessing {len(messages)} messages...\n")

    classifier = SupportClassifier(api_key="sk-your-openai-key-here")

    try:
        results = classifier.classify(messages)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  Results")
    print("=" * 60)
    print(json.dumps(results, indent=2))

    output_path = "output.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {output_path}")

    return results


if __name__ == "__main__":
    main()