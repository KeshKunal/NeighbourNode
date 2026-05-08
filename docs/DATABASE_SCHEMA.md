# Database Schema

The database is PostgreSQL (Supabase). Schema is the single source of truth for workflow state. Do not change column names without team agreement.

## Transaction Status Enum

Use a strict enum everywhere:

```
AVAILABLE
PENDING_APPROVAL
RESERVED
ACTIVE
OVERDUE
RETURNED
CANCELLED
```

## Tables

### users

- id: uuid, pk
- full_name: text, not null
- phone: text, unique, not null
- email: text, unique, null
- building: text, null
- unit: text, null
- created_at: timestamp with time zone, not null

Indexes: phone, email

### items

- id: uuid, pk
- owner_id: uuid, fk -> users.id
- name: text, not null
- description: text, null
- category: text, null
- condition: text, null
- location_hint: text, null
- is_active: boolean, not null, default true
- created_at: timestamp with time zone, not null

Indexes: owner_id, name, category

### transactions

- id: uuid, pk
- item_id: uuid, fk -> items.id
- borrower_id: uuid, fk -> users.id
- owner_id: uuid, fk -> users.id
- requested_start: timestamp with time zone, not null
- requested_end: timestamp with time zone, not null
- approved_start: timestamp with time zone, null
- approved_end: timestamp with time zone, null
- status: text, not null (TransactionStatus)
- calendar_event_id: text, null
- created_at: timestamp with time zone, not null
- updated_at: timestamp with time zone, not null

Indexes: item_id, borrower_id, owner_id, status

### messages

- id: uuid, pk
- transaction_id: uuid, fk -> transactions.id
- sender_user_id: uuid, fk -> users.id
- channel: text, not null (telegram)
- direction: text, not null (inbound, outbound)
- payload: jsonb, not null
- created_at: timestamp with time zone, not null

Indexes: transaction_id, sender_user_id

### notifications

- id: uuid, pk
- user_id: uuid, fk -> users.id
- transaction_id: uuid, fk -> transactions.id
- type: text, not null
- status: text, not null (queued, sent, failed)
- payload: jsonb, not null
- created_at: timestamp with time zone, not null

Indexes: user_id, transaction_id, status

## Migration Rules

- Only the Database and API owner edits schema.
- Any status change must be reflected in shared schemas.
- If a migration is needed, add SQL under infra/sql/ with a date prefix.
