import pytest
import pandas as pd
from pandas import Timestamp


@pytest.fixture(scope='session')
def my_summary_statistics_table_test_case1():
    myTestPoint1 = 'Test data point1'
    myTestDf = pd.DataFrame({'timepretty': [Timestamp('2023-05-19 15:08:00'), Timestamp('2023-05-19 15:09:00'), Timestamp('2023-05-19 15:10:00')],
                             'observation': [myTestPoint1, myTestPoint1, myTestPoint1],
                             'datapoint': [0, 'a', 2]})
    expectedPointSummary = pd.DataFrame({'count': {myTestPoint1: 2.0},
                                         'mean': {myTestPoint1: 1.0},
                                         'std': {myTestPoint1: 1.414},
                                         'min': {myTestPoint1: 0.0},
                                         '25%': {myTestPoint1: 0.5},
                                         '50%': {myTestPoint1: 1.0},
                                         '75%': {myTestPoint1: 1.5},
                                         'max': {myTestPoint1: 2.0}})
    return myTestPoint1, myTestDf, expectedPointSummary


@pytest.fixture(scope='session')
def my_summary_statistics_table_test_case2():
    myTestPoint2 = 'Test data point2'
    myTestDf = pd.DataFrame({'timepretty': [Timestamp('2023-05-19 15:08:00'), Timestamp('2023-05-19 15:09:00'), Timestamp('2023-05-19 15:10:00')],
                             'observation': [myTestPoint2, myTestPoint2, myTestPoint2],
                             'datapoint': [True, True, False]})
    expectedPointSummary = pd.DataFrame({'count': {myTestPoint2: 3}}, dtype="object")
    return myTestPoint2, myTestDf, expectedPointSummary


@pytest.fixture(scope='session')
def my_summary_statistics_table_test_case3():
    myTestPoint3 = 'Test data point3'
    myTestDf = pd.DataFrame({'timepretty': [Timestamp('2023-05-19 15:08:00'), Timestamp('2023-05-19 15:09:00'), Timestamp('2023-05-19 15:10:00')],
                             'observation': [myTestPoint3, myTestPoint3, myTestPoint3],
                             'datapoint': ['On', 'Off', 'On']})
    expectedPointSummary = pd.DataFrame({'count': {myTestPoint3: 0.0},
                                         'mean': {myTestPoint3: ''},
                                         'std': {myTestPoint3: ''},
                                         'min': {myTestPoint3: ''},
                                         '25%': {myTestPoint3: ''},
                                         '50%': {myTestPoint3: ''},
                                         '75%': {myTestPoint3: ''},
                                         'max': {myTestPoint3: ''}})
    return myTestPoint3, myTestDf, expectedPointSummary

