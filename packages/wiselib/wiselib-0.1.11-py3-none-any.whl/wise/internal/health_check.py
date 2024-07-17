import logging
from abc import ABC, abstractmethod
from typing import List

from django.db import connections
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.utils import OperationalError

logger = logging.getLogger(__name__)


class BaseCheck(ABC):
    @abstractmethod
    def check(self) -> bool:
        """
        :return: True, if check is successful. False, otherwise.
        """
        pass


class DBCheck(BaseCheck):
    def __init__(self):
        super(DBCheck, self).__init__()

    def check(self) -> bool:
        try:
            conn: BaseDatabaseWrapper = connections["default"]
            conn.ensure_connection()
            return True
        except OperationalError as oe:
            logger.error(f"DB Check error: {oe}")
            return False


class KafkaCheck(BaseCheck):
    def __init__(self):
        super(KafkaCheck, self).__init__()

    def check(self) -> bool:
        # TODO: implement
        return True


class HealthCheck:
    def __init__(self) -> None:
        self._checks: List[BaseCheck] = []

    def add(self, c: BaseCheck) -> None:
        self._checks.append(c)

    def check_all(self) -> bool:
        for c in self._checks:
            if not c.check():
                return False
        return True


health_check = HealthCheck()
health_check.add(DBCheck())
health_check.add(KafkaCheck())
