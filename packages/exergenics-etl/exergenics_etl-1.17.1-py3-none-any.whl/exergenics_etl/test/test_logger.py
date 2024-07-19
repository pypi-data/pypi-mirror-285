import os
import pytest
from ..src.logger import Singleton
from ..src.logger import ETLLogger as Logger


class TestETLLoggerClass:

    def test_initialise(self):
        logger = Logger(loggerName='Exergenics-ETL',
                        component='python_package', subComponent='exergenics_etl')
        assert (isinstance(logger, Logger))
        del logger
