import logging
from pathlib import Path
from typing import Any

from fluent.runtime import FluentBundle, FluentResource

logger = logging.getLogger(__name__)

LOCALES_DIR = Path(__file__).parent / "locales"
SUPPORTED_LOCALES = ["ru", "en"]
DEFAULT_LOCALE = "ru"


class I18n:
    def __init__(self, locale: str = DEFAULT_LOCALE):
        self.locale = locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE
        self._bundle = FluentBundle([self.locale])
        resource = FluentResource(
            (LOCALES_DIR / f"{self.locale}.ftl").read_text(encoding="utf-8")
        )
        self._bundle.add_resource(resource)

    def get(self, key: str, **kwargs: Any) -> str:
        msg = self._bundle.get_message(key)
        if msg is None or msg.value is None:
            logger.warning(f"Translation not found: {key}")
            return key
        result, errors = self._bundle.format_pattern(msg.value, kwargs)
        if errors:
            logger.warning(f"Translation errors for {key}: {errors}")
        return result


def create_i18n(locale: str = DEFAULT_LOCALE) -> I18n:
    return I18n(locale)
