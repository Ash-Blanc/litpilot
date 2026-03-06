# Repository Guidelines

## Project Structure & Module Organization

The repository is split into backend and frontend apps:

- `BE/`: FastAPI + AgentOS backend (Python 3.11+).
- `BE/agents/`: Agent definitions (`intent.py`, `executor.py`, `knowledge.py`).
- `BE/tools/`: TinyFish integration and utility tools.
- `BE/server.py`: API entrypoint (`/api/*` routes and agent registration).
- `FE/`: Vue 3 + Vite frontend.
- `FE/src/components/`: UI components (PascalCase `.vue` files).
- `FE/src/composables/`: API/data hooks (`useApi.js`).
- `FE/src/views/`: Page-level views.

## Build, Test, and Development Commands

### Backend (Python/FastAPI)

```bash
# Install dependencies
cd BE && uv sync

# Run development server (http://localhost:7777)
cd BE && uv run python server.py

# Run a single test (pytest)
cd BE && uv run pytest tests/ -v                    # all tests
cd BE && uv run pytest tests/test_file.py::test_name # specific test

# Linting
cd BE && uv run ruff check .                        # lint
cd BE && uv run ruff format .                       # format check
```

### Frontend (Vue 3/Vite)

```bash
# Install dependencies
cd FE && bun install

# Run development server (http://localhost:5173)
cd FE && bun run dev

# Build for production
cd FE && bun run build

# Preview production build
cd FE && bun run preview
```

## Python Code Style (Backend)

### General Rules

- Follow **PEP 8**, 4-space indentation.
- Use `snake_case` for functions, variables, and file names.
- Use `PascalCase` for classes and types.
- Use `UPPER_SNAKE_CASE` for constants.
- Add clear module docstrings at the top of each file.
- Prefer small, focused modules over large mixed-responsibility files.

### Imports

Order imports in the following groups (separate each group with a blank line):

1. Standard library (`asyncio`, `json`, `logging`, `typing`, etc.)
2. Third-party packages (`agno`, `fastapi`, `pydantic`, etc.)
3. Local project modules (`from agents...`, `from tools...`)

Example:
```python
import asyncio
import json
import logging
from textwrap import dedent
from typing import List, Dict, Any, Optional

from agno.agent import Agent
from agno.models.mistral import MistralChat

from agents.intent import some_agent
from tools.tinyfish import TinyFishTools
```

### Type Annotations

- Use type hints for all function parameters and return values.
- Use `Optional[X]` instead of `X | None` for compatibility.
- Use `Any` sparingly; prefer specific types when possible.

```python
async def scout_task(agent: Agent, intent: str) -> str:
    ...
```

### Error Handling

- Use structured error handling with specific exception types when possible.
- Log errors with context using the `logging` module.
- Return sensible defaults or error messages rather than raising unhandled exceptions.

```python
logger = logging.getLogger(__name__)

try:
    final_data = json.loads(cleaned)
except json.JSONDecodeError as e:
    logger.error(f"Failed to parse JSON: {e}")
    final_data = {"inferred_intent": final_intent_text, "confidence": 0.5}
```

### Logging

- Use `logging.getLogger(__name__)` for module-level loggers.
- Use appropriate log levels: `DEBUG` for detailed flow, `INFO` for key events, `WARNING`/`ERROR` for issues.

## Vue/JS Code Style (Frontend)

### General Rules

- 4-space indentation (as used in existing files).
- Components in `PascalCase.vue` (e.g., `InputForm.vue`, `ReportDisplay.vue`).
- Composables as `useX.js` (e.g., `useApi.js`).
- Use Vue 3 Composition API with `<script setup>`.
- Prefer Tailwind CSS classes over custom CSS.

### Imports

- Use absolute imports from `./` or `../` paths.
- Group imports: Vue built-ins first, then third-party, then local.

```javascript
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { SomeIcon } from 'lucide-vue-next'
import { someFunction } from '../composables/useApi.js'
```

### Components

- Use `defineProps` and `defineEmits` with the runtime API (as shown in existing files).
- Keep template logic simple; move complex logic to functions.
- Use descriptive names for event handlers (e.g., `@click="handleSubmit"`).

```javascript
const props = defineProps({
    modelValue: { type: String, default: '' },
    loading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'submit', 'files-changed'])
```

### Error Handling

- Use try/catch with user-friendly error messages.
- Show alerts or toast notifications for user-facing errors.
- Handle API errors gracefully with fallbacks.

```javascript
try {
    const data = await someApiCall()
    // handle data
} catch (err) {
    alert('Failed to fetch: ' + err.message)
}
```

## API Route Conventions

- Keep API route names and agent IDs explicit and stable (see `BE/server.py`).
- Custom routes go under `/api/*` (e.g., `/api/health`, `/api/browser-history`).
- Agent endpoints use AgentOS conventions: `/agents/{agent_id}/runs`.

## Testing Guidelines

There is no automated test suite checked in yet. Until tests are added:

- Validate backend with `GET /api/health` and key route smoke checks.
- Validate frontend manually through the full infer -> execute -> report flow.
- For new features, include at least one reproducible manual test note in the PR.

To add tests:
- Backend: Use `pytest`, place tests in `BE/tests/`.
- Frontend: Use Vitest or similar, place tests in `FE/src/__tests__/`.

## Commit & Pull Request Guidelines

- Use concise imperative commit messages with occasional Conventional Commit prefixes.
- Recommended format: `<type>: <short summary>` (e.g., `feat: add new agent`, `fix: handle empty intent`).

### PRs should include:
- What changed and why.
- Linked issue/task (if available).
- UI screenshots or recordings for frontend changes.
- Env/config changes (especially keys in `BE/.env.example`).

## Security & Configuration Tips

- **Never commit secrets**; keep keys in `BE/.env`.
- When adding environment variables, update `BE/.env.example` and document in `README.md`.
- Use `.env` for local development only.
