# Plumb Setup and Troubleshooting

## Install

```bash
make plumb-install   # pins to the tested version
plumb init           # initialize in your project
```

## API Key Configuration

By default plumb 0.2.4 is hardcoded to use `anthropic/claude-sonnet-4-20250514` and expects `ANTHROPIC_API_KEY`.

### Using a non-Anthropic key (e.g. OpenAI)

Patch `~/.local/pipx/venvs/plumb-dev/lib/python3.13/site-packages/plumb/programs/__init__.py`:

1. Replace `get_lm()`:
   ```python
   def get_lm() -> dspy.LM:
       model = os.environ.get("PLUMB_MODEL", "anthropic/claude-sonnet-4-20250514")
       default_max = 16384 if not model.startswith("anthropic/") else 28000
       max_tokens = int(os.environ.get("PLUMB_MAX_TOKENS", default_max))
       return dspy.LM(model, max_tokens=max_tokens)
   ```

2. Replace the key check in `validate_api_access()`:
   ```python
   model = os.environ.get("PLUMB_MODEL", "anthropic/claude-sonnet-4-20250514")
   provider = model.split("/")[0] if "/" in model else "anthropic"
   key_map = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}
   required_key = key_map.get(provider, "ANTHROPIC_API_KEY")
   if not os.environ.get(required_key):
       raise PlumbAuthError(...)
   ```

3. Add to `.env`:
   ```
   PLUMB_MODEL=openai/gpt-4o
   OPENAI_API_KEY=sk-...
   ```

4. Source before running plumb: `set -a && source .env && set +a`

## Spec File Format

`plumb parse-spec` works reliably only on **clean, declarative bullet-point requirements**.

**Works:**
```
- The export-table command exports a table to CSV format given a document ID and table ID.
- The CLI reads the API key from CODA_API_KEY environment variable.
```

**Fails silently (returns 0 requirements):** narrative docs, design docs with code blocks, CLAUDE.md developer guides.

Point `.plumb/config.json` at your spec: `{ "spec_paths": ["spec.md"] }`

## Manual requirements.json Fallback (no API key)

The ID is `req-<sha256(text.strip().lower())[:8]>`:

```python
import hashlib, json
from datetime import datetime, timezone

requirements = ["The CLI reads the API key from CODA_API_KEY...", ...]
now = datetime.now(timezone.utc).isoformat()
result = [{"id": f"req-{hashlib.sha256(t.strip().lower().encode()).hexdigest()[:8]}",
           "source_file": "spec.md", "source_section": "", "text": t,
           "ambiguous": False, "created_at": now, "last_seen_commit": None}
          for t in requirements]
with open(".plumb/requirements.json", "w") as f:
    json.dump(result, f, indent=2)
```

## Installing plumb-gaps

`plumb-gaps` writes `.plumb/gaps.json` without an LLM call. Install globally and optionally copy to a project:

```bash
# Global install only
make setup

# Global install + copy to a project
TARGET_PROJECT=/path/to/your/project make setup
```

The copied `plumb_gaps.py` can be committed so all contributors have it without a separate install step.
