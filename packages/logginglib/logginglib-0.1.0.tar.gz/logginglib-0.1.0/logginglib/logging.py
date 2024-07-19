import copy
import logging

from logging import LogRecord
from typing import Any, Dict, List, Optional

from pythonjsonlogger import jsonlogger


logger = logging.getLogger(__name__)

MESSAGE_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
REQUEST_ID_MESSAGE_FORMAT = (
    "[%(asctime)s] [%(levelname)s] [%(name)s] request_id=[%(request_id)s] %(message)s"
)


class JSONFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict) -> None:
        super().add_fields(log_record, record, message_dict)

        if getattr(record, "request_id", None):
            log_record["request_id"] = record.request_id


class StreamFormatter(logging.Formatter):
    def __init__(self, fmt: Optional[str] = None, datefmt=None, style: str = "%"):
        super().__init__(MESSAGE_FORMAT, datefmt, style)
        self.__initial_style = style

    def formatMessage(self, record: LogRecord) -> str:  # noqa
        if getattr(record, "request_id", None):
            fmt = REQUEST_ID_MESSAGE_FORMAT
        else:
            fmt = MESSAGE_FORMAT

        style = logging._STYLES[self.__initial_style][0](fmt)
        return style.format(record)


class SensitiveDataFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.SENSITIVE_FIELDS = {
            # Credit card
            "credit_card_number": self.mask_card_number,
            "CreditCardNumber": self.mask_card_number,
            "sensitiveData": self.mask_card_number,
            "credit_card_identifier": self.mask_credit_card_identifier,
            "creditcard": self.mask_creditcards,
            # Email
            "email": self.mask_email_address,
            # Token
            "token": self.mask_token,
            "api_key": self.mask_token,
            # Phone number
            "Telephone": self.mask_phone_number,
            "phone_number": self.mask_phone_number,
            "credit_card_phone": self.mask_phone_number,
            # Name
            "first_name": self.mask_name,
            "last_name": self.mask_name,
            "name": self.mask_name,
        }

    def mask_credit_card_identifier(self, credit_card_identifier: str) -> str:
        return len(credit_card_identifier) * "*"

    def mask_card_number(self, card_number: Optional[int]) -> Optional[str]:
        if not card_number:
            return

        card_number = str(card_number)
        return card_number[:4] + (len(card_number) - 8) * "*" + card_number[-4:]

    def mask_passport_number(self, passport_number: Optional[str]) -> Optional[str]:
        if not isinstance(passport_number, str):
            return

        return passport_number[-4:].rjust(len(passport_number), "*")

    def mask_creditcards(
        self, creditcards: List[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        if not isinstance(creditcards, list):
            return

        creditcards = copy.deepcopy(creditcards)
        for creditcard in creditcards:
            if not isinstance(creditcard, dict):
                return

            creditcard["CreditCardNumber"] = self.mask_card_number(
                creditcard.get("CreditCardNumber")
            )
        return creditcards

    def mask_email_address(self, email: Optional[str]) -> Optional[str]:
        if not isinstance(email, str):
            return

        local, domain = email.split("@")
        return f"{local[0].ljust(10, '*')}@****.{domain.split('.')[-1]}"

    def mask_email_addresses(self, emails: str) -> Optional[str]:
        if not isinstance(emails, str):
            return

        mask_emails = []
        for email in emails.split(";"):
            mask_emails.append(self.mask_email_address(email))
        return ";".join(mask_emails)

    def mask_token(self, token: str) -> Optional[str]:
        if not isinstance(token, str):
            return

        return "**********"

    def mask_phone_number(self, telephone_number: str) -> Optional[str]:
        if not isinstance(telephone_number, str):
            return

        return f"{telephone_number[:3]}********{telephone_number[-3:]}"

    def mask_name(self, name: Optional[str]) -> Optional[str]:
        if not isinstance(name, str):
            return

        return name[0].ljust(5, "*")

    def mask_name_with_slash(self, name: Optional[str]) -> Optional[str]:
        if not isinstance(name, str):
            return

        if "/" not in name:
            return

        lastname, firstname = name.split("/")
        return f"{lastname[0].ljust(5, '*')}/{firstname[0].ljust(5, '*')}"

    def filter(self, record: logging.LogRecord) -> bool:
        self.filter_sensitive_attributes(record)

        if isinstance(record.args, dict):
            record.args = self.filter_sensitive_args(record.args)
        else:
            record.args = tuple(self.filter_sensitive_args(arg) for arg in record.args)

        return True

    def _filter_sensitive_value_in_dict(self, key, dictionary):
        for k, v in dictionary.items():
            if k == key:
                dictionary[key] = self.SENSITIVE_FIELDS[key](dictionary[key])
                yield dictionary
            elif isinstance(v, dict):
                for result in self._filter_sensitive_value_in_dict(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    if isinstance(d, dict):
                        for result in self._filter_sensitive_value_in_dict(key, d):
                            yield result

    def filter_sensitive_args(self, d: dict) -> dict:
        if isinstance(d, dict):
            d = copy.deepcopy(d)
            for sensitive_field in self.SENSITIVE_FIELDS:
                list(self._filter_sensitive_value_in_dict(sensitive_field, d))
        return d

    def filter_sensitive_attributes(self, record: logging.LogRecord) -> None:
        for sensitive_field in self.SENSITIVE_FIELDS.keys():
            value = getattr(record, sensitive_field, None)
            if not value:
                continue
            setattr(record, sensitive_field, self.SENSITIVE_FIELDS[sensitive_field](value))


def get_basic_config(use_stream_logging_format: bool) -> Dict[str, Any]:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "stream": {"()": StreamFormatter},
            "json": {"()": JSONFormatter, "format": MESSAGE_FORMAT},
        },
        "filters": {
            "sensitive_data": {"()": SensitiveDataFilter},
        },
        "handlers": {
            "stream": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "stream" if use_stream_logging_format else "json",
                "filters": [
                    "sensitive_data",
                ],
            },
        },
        "loggers": {
            "": {
                "level": "INFO",
                "handlers": ["stream"],
            },
        },
    }

    logger.info("Handlers: %s", logging.root.handlers)

    return logging_config
