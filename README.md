# factory-workshop-starter

A tiny FastAPI link shortener. It is the starter for the Tares software factory workshop (Claude Code Berlin, 22 Oct 2026): you make your own copy, plan a small feature with Tares, and watch a factory crew build it to pull requests merged on main. Links live in memory, so every restart starts empty.

## Run

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Then, in another terminal:

```bash
curl -X POST localhost:8000/links -H 'content-type: application/json' -d '{"url":"https://glassflow.ai"}'
curl -i localhost:8000/<code from above>
curl localhost:8000/links/<code from above>/stats
curl localhost:8000/links
```

Each redirect counts as a click and counts reset when the server restarts, so after two redirects the stats look like this:

```json
{"code":"fPsQgf","url":"https://glassflow.ai/","clicks":2,"created_at":"2026-10-29T19:50:57.353790Z","last_clicked_at":"2026-10-29T19:50:57.379245Z"}
```

## Test

```bash
uv run pytest
uv run ruff check .
```

## Feature ideas for the workshop

- **Tags:** add tags to a link on create, and filter with `GET /links?tag=`.
- **Expiry:** accept `expires_at` on create; an expired code returns 410.
