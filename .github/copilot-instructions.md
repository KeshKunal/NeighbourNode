# NeighbourNode — AI Coding & Architecture Rules

# File: .github/copilot-instructions.md

You are an expert senior software engineer specializing in:

- FastAPI
- Python async systems
- Google ADK agent orchestration
- Telegram Bot development
- Supabase/PostgreSQL
- Gemini 1.5 Flash / Gemini 1.5 Pro
- Next.js + React frontend systems
- Production-grade API architecture

You are working on a hackathon project called:

# NeighbourNode

"The Autonomous Hyper-Local Sharing Economy & Marketplace"

The system enables neighbors within apartments, dorms, and gated communities to:

- borrow items
- lend items
- negotiate requests
- schedule handoffs
- manage returns
- discover unavailable items externally

using AI agents and Telegram workflows.

---

## 1. CORE PRODUCT VISION

---

This is NOT:

- a chatbot
- a generic AI assistant
- a passive recommendation system

This IS:

- an AI-driven action orchestration platform

The AI must:

- trigger actions
- coordinate workflows
- manage lifecycle states
- communicate with users
- update the database
- automate reminders
- broker negotiations

The system should feel like:
"an autonomous logistics coordinator for neighborhood sharing."

Every major feature should result in:

- a reservation
- a notification
- a scheduled meeting
- a lifecycle update
- a marketplace discovery
- or another tangible action.

Avoid building passive conversational flows.

---

## 2. PRIMARY ARCHITECTURE PRINCIPLES

---

### 2.1 Deterministic Systems > Autonomous Chaos

The project must remain:

- stable
- debuggable
- deterministic
- demo-safe

Do NOT generate:

- recursive autonomous agents
- self-modifying prompts
- infinite loops
- uncontrolled planning systems

AI should only assist:

- routing
- extraction
- negotiation
- recommendation
- summarization
- external search synthesis

Core business logic must remain deterministic.

---

### 2.2 Strict Separation of Concerns

Never mix:

- API logic
- AI logic
- database logic
- Telegram logic
- scheduling logic
- prompt definitions

Each must remain isolated.

---

### 2.3 Shared Contracts Are Mandatory

All APIs, agents, and services MUST use shared typed schemas.

Never create ad-hoc dictionaries.

Use:

- Pydantic v2 models
- TypedDict
- Enum
- dataclasses where appropriate

---

## 3. OFFICIAL TECH STACK

---

### Backend

- Python 3.11+
- FastAPI
- AsyncIO
- Uvicorn

### AI / Agents

- Gemini 1.5 Flash
- Gemini 1.5 Pro
- Google ADK

### Database

- Supabase
- PostgreSQL

### Frontend

- Next.js
- React
- Tailwind CSS
- Shadcn/ui

### Messaging Layer

- Telegram Bot API

### Scheduling

- APScheduler

### Mapping

- React Leaflet

### Deployment

- Vercel (frontend)
- Render / Google Cloud Run (backend)

---

## 4. PROJECT STRUCTURE (MANDATORY)

---

Maintain this exact architecture.

```txt
neighbournode/
│
├── apps/
│   ├── frontend/
│   ├── backend/
│   └── telegram-bot/
│
├── packages/
│   ├── shared-types/
│   ├── prompts/
│   └── config/
│
├── docs/
├── infra/
└── README.md
```

Backend structure:

```txt
backend/
│
├── app/
│   ├── api/
│   │   ├── routes/
│   │   └── dependencies.py
│   │
│   ├── agents/
│   │   ├── matchmaker/
│   │   ├── scavenger/
│   │   ├── warden/
│   │   └── orchestrator.py
│   │
│   ├── services/
│   │   ├── telegram_service.py
│   │   ├── calendar_service.py
│   │   ├── search_service.py
│   │   ├── supabase_service.py
│   │   └── notification_service.py
│   │
│   ├── schemas/
│   ├── core/
│   ├── jobs/
│   └── main.py
│
├── tests/
└── requirements.txt
```

Never collapse these layers together.

---

## 5. AGENT RESPONSIBILITIES

---

### Matchmaker Agent

Responsibilities:

- item discovery
- matching borrowers with owners
- negotiation
- reservation coordination

Must NOT:

- scrape the internet
- modify database schemas
- manage overdue returns

---

### Warden Agent

Responsibilities:

- overdue detection
- return reminders
- extension handling
- lifecycle enforcement

Must run:

- asynchronously
- periodically via APScheduler

Must NOT:

- perform marketplace search
- make item recommendations

---

### Scavenger Agent

Responsibilities:

- external discovery
- local marketplace search
- Reddit/OLX synthesis
- recommendation formatting

Must NOT:

- directly reserve items
- modify local transaction states

---

## 6. DATABASE RULES

---

Use PostgreSQL relational design.

Expected core tables:

- users
- items
- transactions
- messages
- notifications

Always use:

- UUID primary keys
- timestamps
- foreign keys
- indexed searchable fields

Never hardcode SQL strings inside routes.

Database access must go through:

```python
services/supabase_service.py
```

---

## 7. TRANSACTION STATE MACHINE

---

Use strict enums.

```python
class TransactionStatus(str, Enum):
		AVAILABLE = "available"
		PENDING_APPROVAL = "pending_approval"
		RESERVED = "reserved"
		ACTIVE = "active"
		OVERDUE = "overdue"
		RETURNED = "returned"
		CANCELLED = "cancelled"
```

Never invent additional status strings.

All services and agents must use this enum consistently.

---

## 8. API DEVELOPMENT RULES

---

Use:

- FastAPI routers
- async endpoints
- dependency injection
- Pydantic request/response models

Every route must:

- validate input
- return typed responses
- handle errors gracefully

Never return raw dictionaries.

Example:

```python
@router.post("/borrow", response_model=BorrowResponse)
async def create_borrow_request(
		payload: BorrowRequest
):
```

---

## 9. TELEGRAM BOT RULES

---

Telegram is the PRIMARY interaction layer.

Use:

- Inline keyboards
- Callback queries
- Structured payloads

Avoid:

- free-text parsing whenever possible

Prefer:
[ ✅ Approve ]
[ ❌ Decline ]
[ ⏰ Suggest Time ]

over requiring typed responses.

All Telegram logic must live in:

```txt
telegram_service.py
```

Never place Telegram business logic directly inside routes.

---

## 10. GEMINI USAGE RULES

---

Use Gemini only for:

- intent classification
- semantic extraction
- marketplace result synthesis
- negotiation phrasing
- natural language understanding

Do NOT use Gemini for:

- database integrity
- transaction state logic
- authorization
- scheduling calculations
- deterministic workflows

Business rules must remain code-driven.

---

## 11. GOOGLE ADK RULES

---

Use Google ADK for:

- predictable stateful workflows
- agent orchestration
- controlled execution chains

Do NOT build:

- recursive autonomous planners
- self-improving agents
- open-ended loops

Preferred workflow structure:

```txt
Request
	↓
Intent Detection
	↓
Matchmaker
	↓
Approval Workflow
	↓
Reservation
	↓
Warden Lifecycle
```

Keep graphs:

- linear
- observable
- debuggable

---

## 12. SHARED STATE RULES

---

All orchestration state must use TypedDict.

Example:

```python
class BorrowWorkflowState(TypedDict):
		user_id: str
		item_id: str
		owner_id: str
		requested_start: str
		requested_end: str
		status: str
		telegram_message_id: str | None
		errors: list[str]
```

Never mutate state unpredictably.

---

## 13. PROMPT ENGINEERING RULES

---

ALL prompts must live in:

```txt
packages/prompts/
```

Never hardcode prompts inside:

- routes
- services
- agents

Prompt files should be:

- modular
- reusable
- versionable

Preferred format:

```txt
matchmaker_prompt.md
scavenger_prompt.md
warden_prompt.md
```

---

## 14. FRONTEND RULES

---

Frontend responsibilities:

- browsing items
- displaying maps
- transaction dashboards
- analytics
- visual polish

Frontend must NEVER:

- directly implement AI logic
- duplicate backend business rules

Frontend should consume:

- typed APIs
- typed DTOs
- shared contracts

Use:

- Tailwind CSS
- Shadcn/ui
- responsive layouts
- mobile-first design

Avoid excessive custom CSS.

---

## 15. CODE STYLE RULES

---

Mandatory:

- Python type hints everywhere
- Async-first architecture
- Small focused functions
- Files under 300 lines where possible
- Reusable services
- Docstrings for complex logic

Avoid:

- giant files
- deeply nested logic
- duplicated business rules
- magic strings

---

## 16. ERROR HANDLING RULES

---

Never crash the application.

External API failures must:

- be caught
- logged
- return clean errors

Example:

- Telegram unavailable
- Gemini timeout
- Supabase failure
- Calendar API failure

Use:

- structured logging
- try/except blocks
- meaningful HTTP status codes

---

## 17. LOGGING & OBSERVABILITY

---

Use structured logs.

Every major action should log:

- agent name
- transaction ID
- item ID
- action taken
- success/failure

Example:

```json
{
  "agent": "warden",
  "transaction_id": "abc123",
  "action": "send_overdue_reminder",
  "status": "success"
}
```

Avoid vague print statements.

---

## 18. TESTING RULES

---

Critical flows must be testable independently.

Create tests for:

- reservation creation
- approval handling
- overdue detection
- Telegram callbacks
- status transitions

Never tightly couple services together.

---

## 19. DEMO SAFETY RULES

---

The hackathon demo MUST remain stable.

Provide:

```env
MOCK_EXTERNAL_SERVICES=true
```

When enabled:

- Telegram sends become mocked
- Calendar invites become simulated
- Search results can use fallback mock data

The demo should NEVER fail because:

- API quota exceeded
- internet unstable
- third-party outage

---

## 20. GOLDEN DEMO FLOW (PROTECTED)

---

This workflow must NEVER break.

```txt
User requests item
		↓
Matchmaker finds owner
		↓
Telegram approval sent
		↓
Owner approves
		↓
Reservation created
		↓
Calendar invite generated
		↓
Item marked RESERVED
```

This is the primary judging demonstration.

Protect this flow above all other features.

---

## 21. HACKATHON PRIORITIES

---

Priority order:

1. Stable end-to-end demo
2. Clean UX
3. Reliable workflows
4. Visible AI actions
5. Modular architecture
6. Advanced AI features

Do NOT overengineer.

A reliable simple workflow is better than:

- complex autonomous systems
- unstable AI chains
- unfinished features

---

## 22. WHAT TO OPTIMIZE FOR

---

Optimize for:

- speed of development
- demo reliability
- modular collaboration
- clean architecture
- low integration friction
- visible automation
- strong storytelling

This project should feel like:
"A real AI-powered neighborhood operating system."

Not:
"another chatbot wrapper."
