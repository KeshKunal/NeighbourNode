from __future__ import annotations

import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import Settings
from app.db.mongodb import db, serialize_doc
from app.schemas.telegram import OverdueReminderMessage
from app.schemas.transaction import TransactionStatus
from app.services.mongodb_service import MongoDBService
from app.services.telegram_service import TelegramService

logger = logging.getLogger(__name__)


class OverdueChecker:
    def __init__(
        self,
        settings: Settings,
        telegram_service: TelegramService,
        mongodb_service: MongoDBService,
    ) -> None:
        self._settings = settings
        self._telegram_service = telegram_service
        self._mongodb_service = mongodb_service
        self._scheduler = AsyncIOScheduler(timezone=timezone.utc)

    def start(self) -> None:
        if not self._scheduler.running:
            self._scheduler.add_job(
                self._run_once,
                trigger=IntervalTrigger(minutes=60),
                id="overdue-checker",
                replace_existing=True,
            )
            self._scheduler.start()
            logger.info("overdue.scheduler.started")

    def shutdown(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown()
            logger.info("overdue.scheduler.stopped")

    async def _run_once(self) -> None:
        """
        Warden background job:
        1. Queries MongoDB for loans past approved_end still marked RESERVED or ACTIVE
        2. Sets them to OVERDUE
        3. Creates in-app notifications and sends Telegram reminders
        """
        if db.database is None:
            return

        now = datetime.now(timezone.utc)
        query = {
            "status": {"$in": [TransactionStatus.RESERVED.value, TransactionStatus.ACTIVE.value]},
            "approved_end": {"$lt": now},
        }

        try:
            cursor = db.database["transactions"].find(query)
            overdue_txs = await cursor.to_list(length=100)

            for tx in overdue_txs:
                # Update status to OVERDUE
                await db.database["transactions"].update_one(
                    {"_id": tx["_id"]},
                    {"$set": {"status": TransactionStatus.OVERDUE.value, "updated_at": now}},
                )
                await db.database["resources"].update_one(
                    {"_id": tx["resource_id"]},
                    {"$set": {"status": TransactionStatus.OVERDUE.value, "updated_at": now}},
                )

                # Fetch details for notification
                resource = await db.database["resources"].find_one({"_id": tx["resource_id"]})
                res_title = resource.get("title", "Item") if resource else "Item"
                borrower = await self._mongodb_service.get_user_by_id(tx["borrower_id"])

                # In-app notification
                await self._mongodb_service.create_notification(
                    user_id=str(tx["borrower_id"]),
                    type="RESOURCE_RETURN_REMINDER",
                    title="Resource Return Overdue ⚠️",
                    message=f"Your borrowing period for '{res_title}' has ended. Please return it to the owner promptly.",
                    related_entity_id=str(tx["_id"]),
                )

                # Optional Telegram notification
                if borrower and borrower.get("telegram_chat_id"):
                    reminder = OverdueReminderMessage(
                        transaction_id=str(tx["_id"]),
                        borrower_chat_id=int(borrower["telegram_chat_id"]),
                        item_name=res_title,
                        overdue_since=tx.get("approved_end", now).isoformat()
                        if isinstance(tx.get("approved_end"), datetime)
                        else str(tx.get("approved_end")),
                    )
                    await self._telegram_service.send_overdue_reminder(reminder)

            logger.info("Warden overdue check completed. Processed %d transactions.", len(overdue_txs))
        except Exception as e:
            logger.error("Warden overdue checker encountered an error: %s", e)
