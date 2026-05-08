from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from google.oauth2 import service_account
from googleapiclient.discovery import build

from app.core.config import Settings
from app.schemas.api import CalendarEventRequest, CalendarEventResult


logger = logging.getLogger(__name__)


class CalendarService:
	def __init__(self, settings: Settings) -> None:
		self._settings = settings
		self._timezone = ZoneInfo("Asia/Kolkata")

	def build_borrow_handoff_event(
		self,
		item_name: str,
		borrower_name: str,
		lender_name: str,
		pickup_spot: str,
		borrow_start: datetime,
		return_deadline: datetime,
	) -> CalendarEventRequest:
		return CalendarEventRequest(
			summary="NeighbourNode Borrow Handoff",
			start_time=borrow_start,
			end_time=return_deadline,
			timezone="Asia/Kolkata",
			description=(
				"Borrow details:\n"
				f"Item: {item_name}\n"
				f"Borrower: {borrower_name}\n"
				f"Lender: {lender_name}\n"
				f"Pickup: {pickup_spot}\n"
				"Return deadline: "
				f"{return_deadline.astimezone(self._timezone).isoformat()}"
			),
			location=pickup_spot,
		)

	def _get_credentials(self) -> service_account.Credentials | None:
		if self._settings.google_credentials_json:
			return service_account.Credentials.from_service_account_info(
				self._settings.google_credentials_json,
				scopes=["https://www.googleapis.com/auth/calendar"],
			)

		if self._settings.google_credentials_path:
			return service_account.Credentials.from_service_account_file(
				self._settings.google_credentials_path,
				scopes=["https://www.googleapis.com/auth/calendar"],
			)

		return None

	def create_handoff_event(
		self,
		payload: CalendarEventRequest,
	) -> CalendarEventResult:

		if self._settings.mock_external_services:
			logger.info(
				"calendar.create.mock",
				extra={"summary": payload.summary},
			)

			return CalendarEventResult(
				ok=True,
				event_id="mock-event",
				html_link="https://calendar.google.com",
			)

		if not self._settings.google_calendar_id:
			return CalendarEventResult(
				ok=False,
				error="Google Calendar ID missing",
			)

		credentials = self._get_credentials()

		if not credentials:
			return CalendarEventResult(
				ok=False,
				error="Google credentials missing",
			)

		try:
			service = build(
				"calendar",
				"v3",
				credentials=credentials,
			)

			# NOTE:
			# Service accounts cannot invite attendees
			# without Domain-Wide Delegation.
			# We create the event and share the
			# calendar link manually via Telegram.

			event = {
				"summary": payload.summary,
				"description": payload.description,
				"location": payload.location,
				"start": {
					"dateTime": payload.start_time.isoformat(),
					"timeZone": payload.timezone,
				},
				"end": {
					"dateTime": payload.end_time.isoformat(),
					"timeZone": payload.timezone,
				},
			}

			created = (
				service.events()
				.insert(
					calendarId=self._settings.google_calendar_id,
					body=event,
				)
				.execute()
			)

			logger.info(
				"calendar.create.success",
				extra={
					"event_id": created.get("id"),
					"summary": payload.summary,
				},
			)

			return CalendarEventResult(
				ok=True,
				event_id=created.get("id"),
				html_link=created.get("htmlLink"),
			)

		except Exception as exc:  # noqa: BLE001
			logger.exception("calendar.create.failed")

			return CalendarEventResult(
				ok=False,
				error=str(exc),
			)