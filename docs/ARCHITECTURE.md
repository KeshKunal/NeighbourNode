# Architecture Overview

NeighbourNode is a monorepo with a clear separation of concerns across frontend, backend, agents, and shared contracts. The system is built for deterministic orchestration of borrowing workflows with a Telegram-driven action layer and a FastAPI backend.

## Monorepo Layout

```
neighbournode/
	apps/
		frontend/           # Next.js UI
		backend/            # FastAPI + agents
		telegram-bot/       # Telegram webhook handlers (optional split)
	packages/
		shared-types/       # Shared schemas and enums
		prompts/            # Agent prompt files
		config/             # Shared constants and env schema
	docs/
	infra/
```

## Logical Components

### Frontend (apps/frontend)

- Item catalog, dashboards, map view
- Reads API contracts from backend
- No AI logic

### Backend API (apps/backend/app/api)

- FastAPI routers and dependencies
- Validates requests and returns typed responses
- No direct DB SQL; uses services

### Agents (apps/backend/app/agents)

- Matchmaker: local discovery and negotiation
- Warden: overdue checks and reminders
- Scavenger: external discovery
- Orchestrator: Google ADK workflow routing

### Services (apps/backend/app/services)

- Telegram, Calendar, Supabase, Search, Notifications
- All external actions live here

### Schemas (apps/backend/app/schemas, packages/shared-types)

- Pydantic models and TypedDict state
- Shared enums for transaction state

## Core Data Flow

1. User requests item via UI or Telegram.
2. API validates request, calls Matchmaker agent.
3. Matchmaker queries Supabase and finds owner.
4. Telegram service sends approval request with inline buttons.
5. On approval, Calendar invite is created.
6. Transaction status updates to RESERVED.

## Integration Contracts

- All payloads use shared schemas.
- All state transitions use TransactionStatus enum.
- No ad-hoc dictionaries across services.

## Observability

- Structured logs for each action with agent name, transaction_id, status.
- Errors must be caught and surfaced with clear HTTP errors.

## Demo Path (Protected)

Request item -> Match found -> Telegram approval -> Calendar invite -> Reservation complete.

This path must remain stable even if scavenger or UI enhancements are incomplete.
