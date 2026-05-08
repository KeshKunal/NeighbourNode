# API Contracts

All API payloads must use shared schemas from apps/backend/app/schemas and packages/shared-types. No ad-hoc dictionaries.

## Base Conventions

- Base URL: /api
- All timestamps are ISO 8601 strings
- Responses are typed Pydantic models
- Errors return {"detail": "message"}

## Items

### GET /items

Response: ItemListResponse

### POST /items

Request: ItemCreateRequest
Response: ItemResponse

### GET /items/{item_id}

Response: ItemResponse

## Borrowing

### POST /borrow

Request: BorrowRequest
Response: BorrowResponse

### POST /borrow/{transaction_id}/approve

Request: BorrowApproveRequest
Response: TransactionResponse

### POST /borrow/{transaction_id}/return

Request: BorrowReturnRequest
Response: TransactionResponse

## Users

### POST /users

Request: UserCreateRequest
Response: UserResponse

### GET /users/{user_id}

Response: UserResponse

## Telegram Webhook

### POST /telegram/webhook

Request: TelegramUpdate
Response: TelegramWebhookResponse

## Scavenger

### POST /scavenger/search

Request: ScavengerSearchRequest
Response: ScavengerSearchResponse

## Shared Schemas (Examples)

BorrowRequest

```
item_name: str
borrower_id: str
requested_start: datetime
requested_end: datetime
```

MatchResult

```
success: bool
owner_id: str | None
item_id: str | None
proposed_time: str | None
```

## Versioning

- Add new fields as optional first.
- Never break existing fields during the hackathon.
