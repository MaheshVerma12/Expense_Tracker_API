"""Currency conversion utilities."""
import logging
from decimal import Decimal
from typing import Optional

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def get_exchange_rate(
    from_currency: str, to_currency: str
) -> Optional[tuple[Decimal, str]]:
    """
    Fetch exchange rate from an external API with caching.

    Returns tuple of (rate, date) or None if fetch fails.
    Caches for 1 hour.
    """
    if from_currency == to_currency:
        return Decimal("1"), ""

    cache_key = f"exchange_rate_{from_currency}_{to_currency}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        url = f"{settings.EXCHANGE_RATE_API_URL}/latest"
        response = requests.get(
            url, params={"base": from_currency, "symbols": to_currency}, timeout=5
        )
        response.raise_for_status()

        data = response.json()

        if not data.get("success", True):
            logger.warning(
                f"Exchange rate API error: {data.get('error', {}).get('info')}"
            )
            return None

        rates = data.get("rates", {})
        rate = rates.get(to_currency)

        if rate is None:
            logger.warning(f"No rate found for {from_currency} to {to_currency}")
            return None

        date = data.get("date", "")
        result = (Decimal(str(rate)), date)

        # Cache for 1 hour
        cache.set(cache_key, result, 3600)
        return result

    except requests.RequestException as e:
        logger.error(f"Failed to fetch exchange rate: {e}")
        return None
    except (ValueError, KeyError) as e:
        logger.error(f"Failed to parse exchange rate response: {e}")
        return None


def convert_amount(
    amount: Decimal, from_currency: str, to_currency: str
) -> Optional[tuple[Decimal, Decimal, str]]:
    """
    Convert amount from one currency to another.

    Returns tuple of (converted_amount, rate, date) or None if conversion fails.
    """
    if from_currency == to_currency:
        return amount, Decimal("1"), ""

    rate_data = get_exchange_rate(from_currency, to_currency)
    if rate_data is None:
        return None

    rate, date = rate_data
    converted = (amount * rate).quantize(Decimal("0.01"))
    return converted, rate, date
