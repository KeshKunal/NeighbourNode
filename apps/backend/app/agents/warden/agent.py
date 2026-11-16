from __future__ import annotations

import logging
from datetime import datetime, timezone
from app.db.mongodb import db
from app.schemas.transaction import TransactionStatus
from ..state import OrchestrationState

logger = logging.getLogger(__name__)


async def run_warden(state: OrchestrationState) -> OrchestrationState:
    """
    Warden Agent: inspects active transaction states in MongoDB
    and safely updates any overdue records.
    """
    if db.database is not None:
        now = datetime.now(timezone.utc)
        res = await db.database["transactions"].update_many(
            {
                "status": {"$in": [TransactionStatus.RESERVED.value, TransactionStatus.ACTIVE.value]},
                "approved_end": {"$lt": now},
            },
            {"$set": {"status": TransactionStatus.OVERDUE.value, "updated_at": now}},
        )
        if res.modified_count > 0:
            logger.info("Warden updated %d overdue transactions.", res.modified_count)
    return state
