# Working Preferences

## Learning Style

**Deep learning over quick answers.** When making decisions or writing code, explain the *why* — not just the *what*. This includes:
- Why a particular GCP service or operator was chosen
- Trade-offs between approaches
- How a concept fits into the broader GCP ecosystem
- When a simpler alternative exists, say so and explain the difference

Explanations should be proportionate — brief for small decisions, thorough for architecture or new concepts.

---

## Coding Standards

No strict standard has been enforced yet. The guiding principle is **readability first**. Evolving preferences:

- **Language:** Python 3
- **Style:** Follow PEP 8 as a baseline; don't be rigid about it
- **Names:** Descriptive names preferred over abbreviations; `snake_case` for variables and functions
- **Docstrings:** Add them when a function's purpose isn't obvious from the name and signature
- **Type hints:** Use them when they genuinely clarify intent; skip when they add noise
- **Config:** All GCP resource names, table names, and environment-specific values live in `utils/config.py` — do not hardcode them elsewhere
- **Secrets:** Sensitive values (API keys, emails) read from Airflow Variables, not committed to source
- **SQL:** Keep transformation SQL in `sql/` files, loaded via `utils/sql_utils.load_sql()` — do not embed SQL strings in DAG code

---

## Project Conventions (Observed)

These patterns are already in use and should be continued:

- DAG operators are wired with `>>` chaining, not `set_downstream()`
- GCP resource identifiers flow from `utils/config.py` into the DAG via named imports
- Validation logic lives in `services/ingestion_service.py` and `utils/validations.py`, not inside the DAG
- SQL templates use Python `.format()` with named keys (e.g., `{project_id}`, `{dataset}`)
- Email alerts use the `on_failure_callback` / `on_success_callback` hooks on the DAG, not on individual tasks

---

## How I Like to Work with AI

- **Explain decisions, not just code.** If you make a design choice, say why.
- **Don't over-engineer.** Add only what's needed to solve the problem at hand. No speculative abstractions.
- **Surface trade-offs.** When multiple approaches exist, briefly outline the options before picking one.
- **Teach as you go.** Use the work as a teaching moment for GCP concepts when relevant.
- **Ask if uncertain.** If the intent behind a request is unclear, ask rather than assume.
- **Respect existing patterns.** Match the code style and conventions already in the project.
- **Wiki updates.** After a task, offer to update the wiki if durable knowledge was produced. Wait for approval before writing.

---

## Communication

- Direct and technical is preferred — no filler phrases ("Great!", "Certainly!", etc.)
- Code blocks for any code, commands, or file paths
- Keep explanations concise unless depth is the point
- If a task is blocked on missing context, say so explicitly rather than guessing
