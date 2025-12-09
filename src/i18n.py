import logging
from pathlib import Path
from typing import Any

from fluent.runtime import FluentLocalization, FluentResourceLoader

logger = logging.getLogger(__name__)

LOCALES_DIR = Path(__file__).parent / "locales"
SUPPORTED_LOCALES = ["ru", "en"]
DEFAULT_LOCALE = "ru"


class I18n:
    def __init__(self, locale: str = DEFAULT_LOCALE):
        self.locale = locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE
        self._loader = FluentResourceLoader(str(LOCALES_DIR / "{locale}.ftl"))
        self._l10n = FluentLocalization(
            locales=[self.locale],
            resource_ids=[f"{self.locale}.ftl"],
            resource_loader=self._loader,
        )

    def get(self, key: str, **kwargs: Any) -> str:
        result = self._l10n.format_value(key, kwargs)
        if result is None:
            logger.warning(f"Translation not found: {key}")
            return key
        return result


def create_i18n(locale: str = DEFAULT_LOCALE) -> I18n:
    return I18n(locale)
