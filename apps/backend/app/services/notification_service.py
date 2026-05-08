from __future__ import annotations

import logging

from app.core.config import Settings


logger = logging.getLogger(__name__)


class NotificationService:
	def __init__(self, settings: Settings) -> None:
		self._settings = settings

	def send_whatsapp_message(self, to_number: str, text: str) -> bool:
		"""
		Placeholder for Twilio WhatsApp integration.

		TODO: wire to Twilio when approved, keeping a consistent interface
		for the rest of the system.
		"""
		if self._settings.mock_external_services:
			logger.info("whatsapp.send.mock", extra={"to": to_number, "text": text})
			return True

		logger.warning("whatsapp.send.placeholder", extra={"to": to_number})
		return False
