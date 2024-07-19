import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Set

if TYPE_CHECKING:
    from pytest_stats.test_session_data import TestSessionData
    from pytest_stats.test_item_data import TestItemData

logger = logging.getLogger(__name__)


class ResultsReporter(ABC):
    @abstractmethod
    def report_session_start(self, session_data: 'TestSessionData') -> None:
        pass

    @abstractmethod
    def report_session_finish(self, session_data: 'TestSessionData') -> None:
        pass

    @abstractmethod
    def report_test(self, test_data: 'TestItemData') -> None:
        pass


# noinspection PyBroadException
class ReportersRegistry:
    def __init__(self) -> None:
        self._reporters: Set[ResultsReporter] = set()

    def register(self, reporter: ResultsReporter) -> None:
        self._reporters.add(reporter)
        logger.debug('registered reporter %s', reporter)

    def report_test(self, test_data: 'TestItemData') -> None:
        for reporter in self._reporters:
            try:
                reporter.report_test(test_data=test_data)
            except Exception:  # pylint:disable=broad-exception-caught
                logger.exception('failed to report test to %s', reporter)

    def report_session_start(self, session_data: 'TestSessionData') -> None:
        for reporter in self._reporters:
            try:
                reporter.report_session_start(session_data=session_data)
            except Exception:  # pylint:disable=broad-exception-caught
                logger.exception('failed to report session start to %s', reporter)

    def report_session_finish(self, session_data: 'TestSessionData') -> None:
        for reporter in self._reporters:
            try:
                reporter.report_session_finish(session_data=session_data)
            except Exception:  # pylint:disable=broad-exception-caught
                logger.exception('failed to report session finish to %s', reporter)
