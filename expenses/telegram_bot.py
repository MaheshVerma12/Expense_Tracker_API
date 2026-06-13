"""Telegram bot utilities for budget alerts."""
import logging
import threading
from decimal import Decimal

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_budget_alert(category_name: str, spent: Decimal, limit: Decimal, month_year: str, currency: str = "USD"):
    """
    Send a budget alert via Telegram asynchronously.
    
    Args:
        category_name: Name of the category
        spent: Total spent in the category for the month
        limit: Monthly limit for the category
        month_year: Month and year (e.g., "June 2026")
        currency: Base currency code
    """
    # Send in background thread to avoid blocking the request
    thread = threading.Thread(
        target=_send_telegram_message,
        args=(category_name, spent, limit, month_year, currency),
        daemon=True,
    )
    thread.start()


def _send_telegram_message(category_name: str, spent: Decimal, limit: Decimal, month_year: str, currency: str):
    """Send the actual Telegram message."""
    bot_token = settings.BOT_TOKEN
    chat_id = settings.BOT_CHAT_ID

    if not bot_token or not chat_id:
        logger.warning("BOT_TOKEN or BOT_CHAT_ID not configured")
        return

    message = (
        f"⚠️ Budget alert: \"{category_name}\" is over its monthly limit.\n"
        f"Spent {spent:.2f} / {limit:.2f} {currency} for {month_year}."
    )

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        logger.info(f"Budget alert sent for category: {category_name}")
    except requests.RequestException as e:
        logger.error(f"Failed to send Telegram alert: {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending Telegram alert: {e}")
