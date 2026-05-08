from __future__ import annotations

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import Settings
from app.schemas.telegram import OverdueReminderMessage
from app.services.supabase_service import SupabaseService
from app.services.telegram_service import TelegramService


logger = logging.getLogger(__name__)


class OverdueChecker:
	def __init__(
		self,
		settings: Settings,
		telegram_service: TelegramService,
		supabase_service: SupabaseService,
	) -> None:
		self._settings = settings
		self._telegram_service = telegram_service
		self._supabase_service = supabase_service
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
		overdue_items = await self._fetch_overdue_transactions()
		for item in overdue_items:
			await self._telegram_service.send_overdue_reminder(item)

	async def _fetch_overdue_transactions(self) -> list[OverdueReminderMessage]:
		return await self._supabase_service.fetch_overdue_transactions()
