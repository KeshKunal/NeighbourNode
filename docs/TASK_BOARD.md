# Task Board

Use this as the single source of ownership and sequencing. Update daily.

## Team Ownership

Member 1 - AI and Orchestration (Owner)

- Owns: agents/, prompts/, orchestrator.py
- Responsibilities: LangGraph, Gemini integration, intent routing, agent state, scavenger logic
- Does not touch: frontend, Telegram infra, UI
- Deliverables: working agent pipelines, deterministic outputs

Member 2 - Telegram and Actions (Owner)

- Owns: services/telegram_service.py, calendar_service.py, jobs/, api/routes/telegram.py
- Responsibilities: Telegram bot, inline buttons, webhook handling, APScheduler, Calendar integration
- Deliverables: reliable external actions

Member 3 - Database and API (Owner)

- Owns: schemas/, api/routes/, supabase_service.py, infra/sql/
- Responsibilities: DB schema, Supabase, CRUD APIs, auth, transactions, persistence
- Rule: nobody edits schemas except this owner

Member 4 - Frontend and Demo (Owner)

- Owns: apps/frontend/, docs/DEMO_SCRIPT.md
- Responsibilities: catalog, dashboard, map, UX polish, demo flow

## Build Order

Phase 1 - Foundation

- Repo and folder structure
- Shared schemas and enums
- Supabase schema and seed data

Phase 2 - Core Demo Path

- Items CRUD and transactions
- Telegram approval flow
- Reservation state updates
- Calendar invite creation
- Minimal frontend view

Phase 3 - Enhancements

- Scavenger external search
- Smart negotiation and summaries
- Overdue reminders

## Integration Rules

- Merge every few hours.
- No schema changes without team approval.
- Use shared enums everywhere.
- Protect the Golden Demo Flow.
