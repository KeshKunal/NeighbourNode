# Agent Flow

Agents are orchestrated via LangGraph with deterministic state transitions. All state is typed and stored in shared schemas.

## Matchmaker (Discovery and Negotiation)

Trigger: User request via API or Telegram.

Flow:

1. Parse intent and required time window.
2. Query Supabase for matching items.
3. If match found, request owner approval via Telegram.
4. On approval, propose schedule and update transaction status.

Inputs:

- BorrowRequest

Outputs:

- MatchResult
- TransactionResponse

## Warden (Lifecycle and Overdue)

Trigger: Scheduled job every hour.

Flow:

1. Find transactions past approved_end with status ACTIVE.
2. Send Telegram reminder to borrower.
3. If borrower confirms return, notify owner.
4. Update transaction to RETURNED or OVERDUE.

## Scavenger (External Discovery)

Trigger: Matchmaker finds no local item.

Flow:

1. Invoke search tool with item query and locality.
2. Rank results by distance and price.
3. Return top results with summary.

## Shared LangGraph State

```
user_id: str
item_name: str
item_id: str | None
owner_id: str | None
requested_start: str
requested_end: str
status: str
telegram_message_id: str | None
errors: list[str]
```

State transitions are only valid if they align with TransactionStatus.
