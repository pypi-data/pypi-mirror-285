import pytest
import os
import sys
import pandas as pd
from pandas import Timestamp
from pandas.testing import assert_frame_equal
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import numpy as np
import shutil
import zipfile
from dotenv import load_dotenv
import json

try:
    from ..src.logger import ETLLogger as Logger
    from ..src.exergenics_etl import *
except:
    path = os.getcwd()
    sys.path.insert(0, path)
    from app.exergenics_etl.src.logger import ETLLogger as Logger
    from app.exergenics_etl.src.exergenics_etl import *


load_dotenv()

logger = Logger(loggerName='UnitTest',
                component='data_modules', subComponent='pre_merged')

TEST_DATA_DIR = "app/exergenics_etl/test/testData"

class TestCreateApiClass:

    @pytest.fixture(scope='class', params=['production'])
    def my_valid_environment(self, request):
        return request.param

    @pytest.fixture(scope='class')
    def my_invalid_environment(self):
        return 'environment'

    def test_create_api_for_valid_environment(self, my_valid_environment):
        api = create_api(my_valid_environment)
        assert api.authenticate()

    def test_create_api_for_invalid_environment(self, my_invalid_environment):
        with pytest.raises(ValueError):
            api = create_api(my_invalid_environment)


class TestCreateSQLEngineClass:

    @pytest.fixture(scope='class', params=['datastore', 'header-repo'])
    def my_test_database_name(self, request):
        return request.param

    def test_create_sql_engine(self, my_test_database_name):
        """Test if the engine created is connectable."""
        engine = create_sql_engine(databaseName=my_test_database_name,
                                   host="ex-database.mysql.database.azure.com", user="exergenics", password=os.getenv('MYSQL_PASSWORD'))
        engine.connect()

    def test_none_password(self, my_test_database_name):
        """Test raising TypeError when the password is not found in environment variables
        and is None."""
        myMissingMysqlPassword = os.getenv('MISSING_PASSWORD')
        with pytest.raises(TypeError):
            engine = create_sql_engine(databaseName=my_test_database_name,
                                       host="ex-database.mysql.database.azure.com", user="exergenics", password=myMissingMysqlPassword)


class TestGetTimeNow:

    @pytest.fixture(scope='class')
    def my_expected_output_datetime_length(self):
        return 15

    @pytest.fixture(scope='class')
    def my_expected_output_datetime_type(self):
        return str

    def test_output_datetime_length(self, my_expected_output_datetime_length):
        """Test the length of the output datetime in string."""
        assert len(get_time_now()) == my_expected_output_datetime_length

    def test_output_datetime_type(self, my_expected_output_datetime_type):
        """Test the type of the output datetime in string."""
        assert type(get_time_now()) == my_expected_output_datetime_type


class TestCreateTmpFolderClass:

    @pytest.fixture(scope='class')
    def my_test_folder(self):
        return "test_tmp_folder"

    def test_create_tmp_folder_when_not_exist(self, my_test_folder):
        """Test if the function creates a temporary folder when the folder does not exist."""
        assert not os.path.exists(my_test_folder)

        create_tmp_folder(my_test_folder)
        assert os.path.exists(my_test_folder)

        shutil.rmtree(my_test_folder)

    def test_create_tmp_folder_when_exists(self, my_test_folder):
        """Test if the function will not overwrite when the temporary folder
        we want to create already exists."""
        os.makedirs(my_test_folder+"/sub_folder")
        assert os.path.exists(my_test_folder)
        assert os.path.exists(my_test_folder+"/sub_folder")

        create_tmp_folder(my_test_folder)
        assert os.path.exists(my_test_folder+"/sub_folder")

        shutil.rmtree(my_test_folder)


class TestGenerateCSVNameClass:

    @pytest.fixture(scope='class')
    def my_test_point_name(self):
        return "CM-01 VSD INPUT POWER Trend - Present Value () (kW)"

    def test_generate_CSV_name_without_certain_characters(self, my_test_point_name):
        """Test if the following special characterare not in the output CSV name:
        spaces, '/', '~', '&', '%'.
        """
        csvName = generate_CSV_name(my_test_point_name)
        for c in [' ', '/', '~', '&', '%']:
            assert c not in csvName


class TestStrftimeForNaTClass:

    @pytest.fixture(scope='class')
    def my_NaT(self):
        return pd.to_datetime([np.nan]).min()

    @pytest.fixture(scope='class')
    def my_datetime_object_and_string(self):
        return pd.to_datetime(['2023-03-17', '2023-03-18']).min(), "17/03/2023 00:00"

    def test_strftime_for_NaT(self, my_NaT):
        assert strftime_for_NaT(my_NaT) == ""

    def test_strftime_for_datetime_object(self, my_datetime_object_and_string):
        myDatetimeObject = my_datetime_object_and_string[0]
        myDatetimeString = my_datetime_object_and_string[1]
        assert strftime_for_NaT(
            myDatetimeObject) == myDatetimeString


class TestGenerateOneManifestRowClass:

    @pytest.fixture(scope='class')
    def my_test_point_name(self):
        return "CM-01 CH-LOAD TRD1 _ (TRD1) (%)"

    @pytest.fixture(scope='class')
    def my_test_trend_log_dataframe(self, my_test_point_name):
        return pd.DataFrame({"timepretty": pd.Series(pd.to_datetime(['2023-03-18', ''])),
                             'observation': [my_test_point_name, my_test_point_name],
                             'datapoint': [1, 2]})

    def test_generate_one_manifest_row(self, my_test_point_name, my_test_trend_log_dataframe):
        """Test the type of the output manifest data for a test point."""
        manifestRow = generate_one_manifest_row(
            my_test_point_name, my_test_trend_log_dataframe)
        assert type(manifestRow) == dict


class TestGenerateOutputFilePathClass:

    @pytest.fixture(scope='class', params=['', '/temp/', 'temp'])
    def my_test_path(self, request):
        return request.param

    @pytest.fixture(scope='class')
    def my_test_inputs(self):
        return {'module': 'preheader', 'extension': 'zip', 'bCode': 'CROWN-METROPOL',
                'pCode': 'PLANT-117', 'category': 'zipfile', 'jobId': 101}

    def test_generate_output_file_path(self, my_test_path, my_test_inputs):
        """Test generating output file path with different path prefixes."""
        outputFilePath = generate_output_file_path(
            module=my_test_inputs['module'], extension=my_test_inputs['extension'],
            bCode=my_test_inputs['bCode'], pCode=my_test_inputs['pCode'],
            category=my_test_inputs['category'], jobId=my_test_inputs['jobId'],
            path=my_test_path)
        assert '//' not in outputFilePath


class TestGetFileNameListClass:

    @pytest.fixture(scope="class")
    def my_manual_zipfile(self):
        return zipfile.ZipFile(f"{TEST_DATA_DIR}/manual_zipfile.zip")

    def test_get_file_name_list(self, my_manual_zipfile):
        fileNames = get_file_name_list(my_manual_zipfile)
        assert len(fileNames) == 4


class TestSkipRowsMachineClass:

    @pytest.fixture(scope='class')
    def my_expected_columns(self):
        """The expected column headers of the dataframe returned form skipRowsMachine.read."""
        return pd.Series(['Timestamp', 'Test value column'])
    
    @pytest.fixture(scope='function')
    def my_skipRowsMachine(self):
        skipRowsMachine = SkipRowsMachine()
        return skipRowsMachine
        
    def test_skiprows(self, my_expected_columns, my_skipRowsMachine):
        """Test auto skiprows on files with mixed skiprows values and format."""
        myTestFileNames = [
            'test_skipRows/oneSkipRows_noComma.csv', 'test_skipRows/oneSkipRows.csv', 
            'test_skipRows/twoSkipRows.csv', 'test_skipRows/twoSkipRows_noComma.csv', 
            'test_skipRows/zeroSkipRows.csv', 'test_skipRows/zeroSkipRows_emptyColumn.csv', 
            # 'test_skipRows/oneSkipRows.xlsx','test_skipRows/twoSkipRows.xlsx', 'test_skipRows/zeroSkipRows.xlsx'
        ]
        myTestZipfilePath = f"{TEST_DATA_DIR}/test_skipRows.zip"
        myTestZippedFile = zipfile.ZipFile(myTestZipfilePath)

        for fileName in myTestFileNames:
            df = my_skipRowsMachine.read(fileName, myTestZippedFile)
            assert all(df.columns.values == my_expected_columns)


class TestConvertableToFloatClass:

    @pytest.mark.parametrize("string, expected", [
    ("3.14", True),  # Valid float string
    ("0", True),     # Valid float string
    ("-5.2", True),  # Valid float string
    ("1e-5", True),  # Valid float string
    (np.nan, True),  # Convertable nan
    ("abc", False),  # Invalid float string
    ("1.23.45", False),  # Invalid float string
    ("12a", False),  # Invalid float string
    ("", False),     # Empty string
    ])
    def test_convertable_to_float(self, string, expected):
        assert convertable_to_float(string) == expected


class TestInputValidationClass:

    @pytest.fixture(scope='class')
    def my_check_for_wide_format_test_case_wide1(self):
        filePath = f'{TEST_DATA_DIR}/testData_check_for_wide_format/wideData1.csv'
        df = pd.read_csv(filePath)
        timestampColumnNames = ['ui::timestamp']
        return df, timestampColumnNames
    
    @pytest.fixture(scope='class')
    def my_check_for_wide_format_test_case_wide2(self):
        filePath = f'{TEST_DATA_DIR}/testData_check_for_wide_format/wideData2.csv'
        df = pd.read_csv(filePath)
        timestampColumnNames = ['Created time', 'Modified time']
        return df, timestampColumnNames
    
    @pytest.fixture(scope='class')
    def my_check_for_wide_format_test_case_long1(self):
        """Second test case for the _check_for_wide_format method where the 
        input is a long dataframe, and the names column is in the 1st 
        column."""
        filePath = f'{TEST_DATA_DIR}/testData_check_for_wide_format/longData_nameColumnIn1stColumn.csv'
        df = pd.read_csv(filePath)
        namesColumnId = 0
        valuesColumnId = 1
        timestampColumnNames = ['ui::timestamp']
        return df, timestampColumnNames, namesColumnId, valuesColumnId

    @pytest.fixture(scope='class')
    def my_check_for_wide_format_test_case_long2(self):
        """Second test case for the _check_for_wide_format method where the 
        input is a long dataframe, and the names column is in the 2nd 
        column."""
        filePath = f'{TEST_DATA_DIR}/testData_check_for_wide_format/longData_nameColumnIn2ndColumn.csv'
        df = pd.read_csv(filePath)
        namesColumnId = 1
        valuesColumnId = 2
        timestampColumnNames = ['ui::timestamp']
        return df, timestampColumnNames, namesColumnId, valuesColumnId
    
    @pytest.fixture(scope='class')
    def my_check_for_wide_format_test_case_long3(self):
        """Second test case for the _check_for_wide_format method where the 
        input is a long dataframe, and the names column is in the 3rd 
        column."""
        filePath = f'{TEST_DATA_DIR}/testData_check_for_wide_format/longData_nameColumnIn3rdColumn.csv'
        df = pd.read_csv(filePath)
        namesColumnId = 2
        valuesColumnId = 1
        timestampColumnNames = ['ui::timestamp']
        return df, timestampColumnNames, namesColumnId, valuesColumnId

    @pytest.fixture(scope='class')
    def my_valid_timestamp_headers(self):
        return ['datetime', 'timestamp', 'event', 'timepretty', 'ts']

    @pytest.fixture(scope='class')
    def my_generic_column_headers(self):
        return ['value']

    @pytest.fixture(scope='class')
    def my_inputValidation_object(self, my_valid_timestamp_headers, my_generic_column_headers):
        """Instantiate an InputValidation object for testing."""
        inputValidation = InputValidation(
            my_valid_timestamp_headers, my_generic_column_headers)
        return inputValidation

    @pytest.mark.parametrize("my_test_case", ['my_check_for_wide_format_test_case_wide1', 'my_check_for_wide_format_test_case_wide2'])
    def test_check_for_wide_format_on_wide_dataframe(self, my_inputValidation_object, my_test_case, request):
        """Check for wide format when a wide format dataframe is passed."""
        testDf, myTimestampColumnNames = request.getfixturevalue(my_test_case)
        assert my_inputValidation_object._check_for_wide_format(
            testDf, myTimestampColumnNames)

    @pytest.mark.parametrize("my_test_case", ['my_check_for_wide_format_test_case_long1', 'my_check_for_wide_format_test_case_long2', 'my_check_for_wide_format_test_case_long3'])
    def test_check_for_wide_format_on_long_dataframe(self, my_inputValidation_object, my_test_case, request):
        """Check for wide format when a long format dataframe is passed."""
        testLongDf, myTimestampColumnNames, expectedNamesColumnId, expectedValuesColumnId = request.getfixturevalue(my_test_case)
        with pytest.raises(EtlError) as errInfo:
            my_inputValidation_object._check_for_wide_format(
                testLongDf, myTimestampColumnNames)

        assert errInfo.value.args[1] == expectedNamesColumnId
        assert errInfo.value.args[2] == expectedValuesColumnId

    def test_check_for_generic_header1(self, my_inputValidation_object):
        myDfSameName = pd.read_csv(
            f'{TEST_DATA_DIR}/dfSameName.csv', parse_dates=['timepretty'])
        myDfNew = pd.read_csv(
            f'{TEST_DATA_DIR}/dfNew.csv', parse_dates=['timepretty'])
        myPointName = 'Ch1-kwr'

        assert not my_inputValidation_object.check_for_generic_header(
            myPointName, myDfSameName, myDfNew)

    def test_check_for_generic_header2(self, my_inputValidation_object):
        myDfSameName = pd.read_csv(
            f'{TEST_DATA_DIR}/dfSameName_genericHeader.csv', parse_dates=['timepretty'])
        myDfNew = pd.read_csv(
            f'{TEST_DATA_DIR}/dfNew_genericHeader.csv', parse_dates=['timepretty'])
        myPointName = 'Value'

        with pytest.raises(EtlError):
            my_inputValidation_object.check_for_generic_header(
                myPointName, myDfSameName, myDfNew)

    def test_check_for_generic_header_new(self, my_inputValidation_object):
        """Check if the two dataframes share a generic name that is not in our known, generic header name list."""
        myDfSameName = pd.read_csv(
            f'{TEST_DATA_DIR}/dfSameName_newGenericHeader.csv', parse_dates=['timepretty'])
        myDfNew = pd.read_csv(
            f'{TEST_DATA_DIR}/dfNew_newGenericHeader.csv', parse_dates=['timepretty'])
        myPointName = 'Value'

        with pytest.raises(EtlError):
            my_inputValidation_object.check_for_generic_header(
                myPointName, myDfSameName, myDfNew)

    @pytest.mark.parametrize("myTestTimestampHeader", ['timestamp', 'time stamp', 'ui::timestamp', 'ts', 'date', 'time', 'datetime', 'date/time'])
    def test_validate_timestamp_column_header(self, my_inputValidation_object, myTestTimestampHeader):
        myDf = pd.DataFrame(
            {myTestTimestampHeader: [],
             'Some random data point': []})

        assert my_inputValidation_object._validate_timestamp_column_header(
            myDf)


class TestCalculateTimeInterval:

    @pytest.fixture(scope='class')
    def my_test_case1(self):
        myTestDtSeries = pd.Series(pd.to_datetime(
            ['2023-05-19 15:08', '2023-05-19 15:09', '2023-05-19 15:10', '2023-05-19 15:10']))
        expectedTimeInterval = '1'
        return myTestDtSeries, expectedTimeInterval

    @pytest.fixture(scope='class')
    def my_test_case2(self):
        myTestDtSeries = pd.Series(pd.to_datetime(
            ['2023-05-19 15:05', '2023-05-19 15:10', '2023-05-19 15:15', '2023-05-19 15:20']))
        expectedTimeInterval = '5'
        return myTestDtSeries, expectedTimeInterval

    @pytest.fixture(scope='class')
    def my_test_case3(self):
        myTestDtSeries = pd.Series(pd.to_datetime(
            ['2023-05-19 15:05', '']))
        expectedTimeInterval = ''  # No time interval when there are < 2 datetimes
        return myTestDtSeries, expectedTimeInterval

    @pytest.fixture(scope='class')
    def my_test_case4(self):
        myTestDtSeries = pd.Series(pd.to_datetime([]))
        expectedTimeInterval = ''  # No time interval when there are < 2 datetimes
        return myTestDtSeries, expectedTimeInterval

    @pytest.mark.parametrize("my_calculate_time_interval_test_case", ['my_test_case1', 'my_test_case2', 'my_test_case3', 'my_test_case4'])
    def test_calculate_time_interval(self, my_calculate_time_interval_test_case, request):
        myTestDtSeries, expectedTimeInterval = request.getfixturevalue(
            my_calculate_time_interval_test_case)

        assert calculate_time_interval(myTestDtSeries) == expectedTimeInterval


class TestFindTimestampColumns:

    @pytest.fixture(scope='class')
    def my_test_case1(self):
        """Two timestamp column; not unix timestamps."""
        filePath = f"{TEST_DATA_DIR}/testData_for_find_timestamp_column/two timestamp columns.csv"
        df = pd.read_csv(filePath)
        myIsUnixTimestamp = False
        return df, myIsUnixTimestamp

    @pytest.fixture(scope='class')
    def my_test_case2(self):
        """Timestamps in the second column; not unix timestamps."""
        filePath = f"{TEST_DATA_DIR}/testData_for_find_timestamp_column/timestamps in second column.csv"
        df = pd.read_csv(filePath)
        myIsUnixTimestamp = False
        return df, myIsUnixTimestamp

    @pytest.fixture(scope='class')
    def my_test_case3(self):
        """Timestamps in the second column and unix timestamps in the first column."""
        filePath = f"{TEST_DATA_DIR}/testData_for_find_timestamp_column/timestamps in second column (unix timestamps in first column).csv"
        df = pd.read_csv(filePath)
        myIsUnixTimestamp = False
        return df, myIsUnixTimestamp

    @pytest.fixture(scope='class')
    def my_test_case4(self):
        """Timestamps in the third column; not unix timestamps."""
        filePath = f"{TEST_DATA_DIR}/testData_for_find_timestamp_column/timestamps in third column.csv"
        df = pd.read_csv(filePath)
        myIsUnixTimestamp = False
        return df, myIsUnixTimestamp

    @pytest.fixture(scope='class')
    def my_test_case5(self):
        """No timestamp column found."""
        filePath = f"{TEST_DATA_DIR}/testData_for_find_timestamp_column/no timestamp column.csv"
        df = pd.read_csv(filePath)
        return df
    
    @pytest.fixture(scope='class')
    def my_test_case6(self):
        """Unix timestamps in the second column."""
        filePath = f"{TEST_DATA_DIR}/testData_for_find_timestamp_column/unix_timestamps_in_second_column.csv"
        df = pd.read_csv(filePath)
        myIsUnixTimestamp = True
        return df, myIsUnixTimestamp
    
    @pytest.fixture(scope='class')
    def my_expected_timestamp_column_names(self):
        return ['Target column1', 'Target column2']

    @pytest.fixture(scope='class')
    def my_expected_timestamp_column_name(self):
        return ['Target column']
    
    def test_find_two_timestamp_columns(self, my_test_case1, my_expected_timestamp_column_names):
        testDf, expectedIsUnixTimestamp = my_test_case1
        assert find_timestamp_columns(testDf) == (my_expected_timestamp_column_names, expectedIsUnixTimestamp)
    
    @pytest.mark.parametrize("testCase", ["my_test_case2", "my_test_case3", "my_test_case4"])
    def test_find_timestamp_column(self, testCase, my_expected_timestamp_column_name, request):
        testDf, expectedIsUnixTimestamp = request.getfixturevalue(testCase)

        assert find_timestamp_columns(testDf) == (my_expected_timestamp_column_name, expectedIsUnixTimestamp)

    def test_timestamp_column_not_found(self, my_test_case5):
        with pytest.raises(EtlError):
            find_timestamp_columns(my_test_case5)
    
    def test_find_unix_timestamp_column(self, my_test_case6, my_expected_timestamp_column_name):
        testDf, expectedIsUnixTimestamp = my_test_case6
        assert find_timestamp_columns(testDf) == (my_expected_timestamp_column_name, expectedIsUnixTimestamp)


class TestDatetimeParserClass:

    @pytest.fixture(scope='function')
    def my_datetimeParser(self):
        datetimeParser = DatetimeParser()
        return datetimeParser

    @pytest.fixture
    def my_test_case_short_year_parsing(self):
        dtSeries = pd.read_csv(
            f"{TEST_DATA_DIR}/timestamps_dayMonthShortYear.csv", header=None)[0]
        my_dtFinalFormat = '%d/%m/%y %H:%M'
        my_dtObjects = pd.to_datetime(dtSeries, format=my_dtFinalFormat)
        return dtSeries, my_dtObjects

    @pytest.fixture(scope='class')
    def my_test_case_ampm_parsing(self):
        dtSeries = pd.read_csv(
            f"{TEST_DATA_DIR}/timestamps_ampm.csv", header=None)[0]
        my_dtFinalFormat = '%d/%m/%Y %I:%M %p'
        my_dtObjects = pd.to_datetime(dtSeries, format=my_dtFinalFormat)
        return dtSeries, my_dtObjects

    @pytest.fixture(scope='class')
    def my_test_case_month_name_parsing(self):
        dtSeries = pd.read_csv(
            f"{TEST_DATA_DIR}/timestamps_monthName.csv", header=None)[0]
        my_dtFinalFormat = '%B %d, %Y %I:%M:%S %p'
        my_dtObjects = pd.to_datetime(dtSeries, format=my_dtFinalFormat)
        return dtSeries, my_dtObjects

    @pytest.fixture(scope='class')
    def my_test_case_time_zone_parsing(self):
        dtSeries = pd.read_csv(
            f"{TEST_DATA_DIR}/timestamps_timeZones_1.csv", header=None)[0]  # TODO
        expected_output = pd.read_csv(
            f"{TEST_DATA_DIR}/timestamps_timeZones_expectedOutput_1.csv", header=None)[0]
        return dtSeries, expected_output

    @pytest.fixture
    def my_test_dtSeries_with_unrecognisable_time_parts(self):
        dtSeries = pd.read_csv(
            f"{TEST_DATA_DIR}/timestamps_unrecognisableParts.csv", header=None)[0]
        return dtSeries

    @pytest.fixture
    def my_test_case_for_correcting_format_code_with_AMPM_and_seconds(self):
        my_format_code_list = ['%d', '-', '%b', '-',
                               '%y', ' ', '%H:%M:%S', ' ', '%p', ' ', '%Z']
        correct_format_code_list = ['%d', '-', '%b', '-',
                                    '%y', ' ', '%I:%M:%S', ' ', '%p', ' ', '%Z']
        return my_format_code_list, correct_format_code_list

    @pytest.fixture
    def my_test_case_for_correcting_format_code_with_AMPM(self):
        my_format_code_list = ['%d', '-', '%b', '-',
                               '%y', ' ', '%H:%M', ' ', '%p', ' ', '%Z']
        correct_format_code_list = ['%d', '-', '%b', '-',
                                    '%y', ' ', '%I:%M', ' ', '%p', ' ', '%Z']
        return my_format_code_list, correct_format_code_list

    @pytest.fixture
    def my_format_code_with_AMPM_but_no_time(self):
        my_format_code_list = ['%d', '-', '%b', '-',
                               '%y', ' ', '%H%M', ' ', '%p', ' ', '%Z']
        return my_format_code_list

    @pytest.fixture
    def my_test_case_for_removing_time_zone_from_timestamps_with_time_zones(self):
        myDatetimeParts = ['04', '-', 'Nov', '-',
                           '22', ' ', '4:15:09', ' ', 'AM', ' ', 'AEDT']
        myFormatCodeList = ['%d', '-', '%b', '-', '%y',
                            ' ', '%H:%M:%S', ' ', '%p', ' ', '%Z']
        expectedFormatCodeList = ['%d', '-', '%b', '-', '%y',
                                  ' ', '%H:%M:%S', ' ', '%p', ' ']
        return myDatetimeParts, myFormatCodeList, expectedFormatCodeList

    @pytest.fixture
    def my_test_case_for_removing_time_zone_from_timestamps_without_time_zones(self):
        myDatetimeParts = ['04', '-', 'Nov', '-',
                           '22', ' ', '4:15:09', ' ', 'AM']
        myFormatCodeList = ['%d', '-', '%b', '-', '%y',
                            ' ', '%H:%M:%S', ' ', '%p']
        expectedFormatCodeList = ['%d', '-', '%b', '-', '%y',
                                  ' ', '%H:%M:%S', ' ', '%p']
        return myDatetimeParts, myFormatCodeList, expectedFormatCodeList

    @pytest.fixture
    def my_test_case_for_finding_unrecognisable_time_zone(self):
        myDatetimeParts = ['04', '-', 'Nov', '-',
                           '22', ' ', '4:15:09', ' ', 'AM', ' ', 'ABC']
        myFormatCodeList = ['%d', '-', '%b', '-', '%y',
                            ' ', '%H:%M:%S', ' ', '%p', ' ', 'ABC']
        return myDatetimeParts, myFormatCodeList
    
    @pytest.fixture(scope='class')
    def my_test_case_parse_unix_timestamps(self):
        testDtSeries = pd.Series(['315532800', '315532801', '315532802'])
        expectedDtObjects = pd.Series([
            pd.Timestamp('1980-01-01 00:00:00'),
            pd.Timestamp('1980-01-01 00:00:01'),
            pd.Timestamp('1980-01-01 00:00:02')])
        return testDtSeries, expectedDtObjects

    @pytest.fixture
    def my_non_unix_timestamp_flag(self):
        return False
    
    @pytest.fixture
    def my_unix_timestamp_flag(self):
        return True
    
    @pytest.mark.parametrize("testFile", ["test_remove_timezone_abbrev_AEST_AEDT.csv", "test_remove_timezone_abbrev_ACDT_ACST.csv", "test_remove_timezone_abbrev_NT_NUT.csv"])
    def test_parse_timestamps_with_timezone_abbrev(self, testFile, my_datetimeParser, my_non_unix_timestamp_flag):
        testDf = pd.read_csv(f"{TEST_DATA_DIR}/{testFile}")
        expectedDtObject = pd.Series([pd.Timestamp('2023-09-13 05:12:41.211'),
                            pd.Timestamp('2024-03-13 05:12:41.211'),
                            pd.Timestamp('2025-03-13 05:12:41.211'),
                            pd.Timestamp('2026-03-13 05:12:41.211')])
        
        assert my_datetimeParser.parse(testDf['Timestamp'], my_non_unix_timestamp_flag).equals(expectedDtObject)

    def test_parse_for_short_year(self, my_datetimeParser, my_test_case_short_year_parsing, my_non_unix_timestamp_flag):
        dtSeries, my_dtObjects = my_test_case_short_year_parsing
        assert my_datetimeParser.dtFinalFormat is None
        dtObjects = my_datetimeParser.parse(dtSeries, my_non_unix_timestamp_flag)
        assert my_datetimeParser.dtFinalFormat is not None
        assert dtObjects.equals(my_dtObjects)

    def test_parse_for_ampm(self, my_datetimeParser, my_test_case_ampm_parsing, my_non_unix_timestamp_flag):
        dtSeries, my_dtObjects = my_test_case_ampm_parsing
        assert my_datetimeParser.dtFinalFormat is None
        dtObjects = my_datetimeParser.parse(dtSeries, my_non_unix_timestamp_flag)
        assert my_datetimeParser.dtFinalFormat is not None
        assert dtObjects.equals(my_dtObjects)

    def test_parse_for_month_name(self, my_datetimeParser, my_test_case_month_name_parsing, my_non_unix_timestamp_flag):
        dtSeries, my_dtObjects = my_test_case_month_name_parsing
        assert my_datetimeParser.dtFinalFormat is None
        dtObjects = my_datetimeParser.parse(dtSeries, my_non_unix_timestamp_flag)
        assert my_datetimeParser.dtFinalFormat is not None
        assert dtObjects.equals(my_dtObjects)

    def test_checkTimeZone_for_timestamps_with_time_zones(self, my_datetimeParser, my_test_case_time_zone_parsing, my_non_unix_timestamp_flag):
        dtSeries, expected_output = my_test_case_time_zone_parsing
        dtObjects = my_datetimeParser.parse(dtSeries, my_non_unix_timestamp_flag)
        assert my_datetimeParser.containsTimeZone

    def test_find_day_position_when_timestamps_inadequate(self, my_datetimeParser):
        myTestDtSeries = pd.read_csv(
            f"{TEST_DATA_DIR}/timestamps_findDayPosition.csv", header=None)[0]
        positionDay = my_datetimeParser._find_day_position(
            myTestDtSeries)
        assert positionDay == DEFAULT_POSITION_DAY

    def test_find_day_position_for_finding_day_large_than_12(self, my_datetimeParser):
        myTestDtSeries = pd.read_csv(
            f"{TEST_DATA_DIR}/timestamps_findDayPosition_2.csv", header=None)[0]
        positionDay = my_datetimeParser._find_day_position(
            myTestDtSeries)  # TODO
        my_expected_day_position_2 = 2
        assert positionDay == my_expected_day_position_2

    def test_find_day_position_when_month_name_exist(self, my_datetimeParser):
        myTestDtSeries = pd.read_csv(
            f"{TEST_DATA_DIR}/timestamps_monthName.csv", header=None)[0]
        positionDay = my_datetimeParser._find_day_position(
            myTestDtSeries)
        assert positionDay == 2

    def test_removeTimeZone_for_timestamps_with_time_zones(self, my_datetimeParser, my_test_case_for_removing_time_zone_from_timestamps_with_time_zones):
        myDatetimeParts, myFormatCodeList, expectedFormatCodeList = my_test_case_for_removing_time_zone_from_timestamps_with_time_zones
        newFormatCodeList = my_datetimeParser._check_and_remove_time_zone(
            myDatetimeParts, myFormatCodeList)
        assert newFormatCodeList == expectedFormatCodeList

    def test_removeTimeZone_for_timestamps_without_time_zones(self, my_datetimeParser, my_test_case_for_removing_time_zone_from_timestamps_without_time_zones):
        myDatetimeParts, myFormatCodeList, expectedFormatCodeList = my_test_case_for_removing_time_zone_from_timestamps_without_time_zones
        newFormatCodeList = my_datetimeParser._check_and_remove_time_zone(
            myDatetimeParts, myFormatCodeList)
        assert newFormatCodeList == expectedFormatCodeList

    def test_checkTimeZone_for_timestamps_with_unrecognisable_time_zones(self, my_datetimeParser, my_test_case_for_finding_unrecognisable_time_zone):
        """
        Test for the method, _check_and_remove_time_zone, in DatetimeParser. 
        If a datetime part that doesn't follow the pattern of timezone or timezone_name defined in DatetimeParser.bricks, 
        but looks like a time zone name
        _check_and_remove_time_zone should be able to detect that and flag that time zone exists.
        """
        myDatetimeParts, myFormatCodeList = my_test_case_for_finding_unrecognisable_time_zone
        my_datetimeParser._check_and_remove_time_zone(
            myDatetimeParts, myFormatCodeList)
        assert my_datetimeParser.containsTimeZone == True

    def test_checkTimeZone_for_timestamps_without_time_zones(self, my_datetimeParser, my_test_case_ampm_parsing, my_non_unix_timestamp_flag):
        dtSeries, my_dtObjects = my_test_case_ampm_parsing
        dtObjects = my_datetimeParser.parse(dtSeries, my_non_unix_timestamp_flag)
        assert not my_datetimeParser.containsTimeZone

    def test_parse_for_time_zone_handling(self, my_datetimeParser, my_test_case_time_zone_parsing, my_non_unix_timestamp_flag):
        dtSeries, expected_output = my_test_case_time_zone_parsing
        dtObjects = my_datetimeParser.parse(dtSeries, my_non_unix_timestamp_flag)
        assert expected_output.equals(dtObjects.astype(str))

    def test_parse_for_timestamps_with_unrecognisable_time_parts(self, my_datetimeParser, my_test_dtSeries_with_unrecognisable_time_parts, my_non_unix_timestamp_flag):
        with pytest.raises(EtlError):
            my_datetimeParser.parse(
                my_test_dtSeries_with_unrecognisable_time_parts, my_non_unix_timestamp_flag)

    def test_correct_format_code_for_AMPM_with_seconds(self, my_datetimeParser, my_test_case_for_correcting_format_code_with_AMPM_and_seconds):
        """
        Test for the method, _correct_format_code_for_AMPM, in DatetimeParser.
        The method should be able replace %H:%M:%S with %I:%M:%S if %H:%M:%S and %p are parts of the datetime format.
        """
        my_format_code_list, correct_format_code_list = my_test_case_for_correcting_format_code_with_AMPM_and_seconds
        newFormatCodeList = my_datetimeParser._correct_format_code_for_AMPM(
            my_format_code_list)
        assert newFormatCodeList == my_format_code_list

    def test_correct_format_code_for_AMPM(self, my_datetimeParser, my_test_case_for_correcting_format_code_with_AMPM):
        """
        Test for the method, _correct_format_code_for_AMPM, in DatetimeParser.
        The method should be able replace %H:%M with %I:%M if %H:%M and %p are parts of the datetime format.
        """
        my_format_code_list, correct_format_code_list = my_test_case_for_correcting_format_code_with_AMPM
        newFormatCodeList = my_datetimeParser._correct_format_code_for_AMPM(
            my_format_code_list)
        assert newFormatCodeList == my_format_code_list

    def test_correct_format_code_for_AMPM_but_no_time(self, my_datetimeParser, my_format_code_with_AMPM_but_no_time):
        """
        Test for the method, _correct_format_code_for_AMPM, in DatetimeParser.
        The method should raise error if %p is part of the datetime format
        but neither %H:%M:%S nor %H:%M can't be found.
        """
        my_format_code_list = my_format_code_with_AMPM_but_no_time
        with pytest.raises(EtlError):
            my_datetimeParser._correct_format_code_for_AMPM(
                my_format_code_list)

    @pytest.mark.parametrize("myTestMilliseconds", [".1", ".11", ".111", ".1111", ".11111", ".111111"])
    def test_parse_timestamp_with_milliseconds(self, my_datetimeParser, myTestMilliseconds, my_non_unix_timestamp_flag):
        myTestTimestamp = "2022-05-15 05:05:01" + myTestMilliseconds
        myTestDtSeries = pd.Series([myTestTimestamp for i in range(10)])
        my_datetimeParser.parse(myTestDtSeries, my_non_unix_timestamp_flag)

        assert my_datetimeParser.dtFinalFormat == '%Y-%m-%d %H:%M:%S.%f'

    @pytest.mark.parametrize("myTestMilliseconds", [".1 PM", ".11 PM", ".111 PM", ".1111 PM", ".11111 PM", ".111111 PM"])
    def test_parse_timestamp_with_milliseconds_AMPM(self, my_datetimeParser, myTestMilliseconds, my_non_unix_timestamp_flag):
        myTestTimestamp = "2022-05-15 05:05:01" + myTestMilliseconds
        myTestDtSeries = pd.Series([myTestTimestamp for i in range(10)])
        my_datetimeParser.parse(myTestDtSeries, my_non_unix_timestamp_flag)

        assert my_datetimeParser.dtFinalFormat == '%Y-%m-%d %I:%M:%S.%f %p'

    def test_parse_unix_timestamps(self, my_datetimeParser, my_test_case_parse_unix_timestamps, my_unix_timestamp_flag):
        testDtSeries, expectedDtObjects = my_test_case_parse_unix_timestamps
        dtObjects = my_datetimeParser.parse(testDtSeries, my_unix_timestamp_flag)
        assert dtObjects.equals(expectedDtObjects)


class TestTransformColumnsToLongDataframes:

    def test_transform_columns_to_long_dataframes(self):
        myTestWideDataframe = pd.DataFrame({
            'timepretty': pd.to_datetime(['2023-05-19 15:08', '2023-05-19 15:09', '2023-05-19 15:10']),
            'Cooling Tower Fan Frequency': [0, 0, 1],
            'Cooling Tower Fan Power': [0, None, 3]
        })
        myTestFilesWithNanColumn, myTestFileName = (set(), '')
        expectedDfDictOutput = {'Cooling Tower Fan Frequency':
                                pd.DataFrame({'timepretty': [Timestamp('2023-05-19 15:08:00'), Timestamp('2023-05-19 15:09:00'), Timestamp('2023-05-19 15:10:00')],
                                              'observation': ['Cooling Tower Fan Frequency', 'Cooling Tower Fan Frequency', 'Cooling Tower Fan Frequency'],
                                              'datapoint': [0, 0, 1]}),
                                'Cooling Tower Fan Power':
                                    pd.DataFrame({'timepretty': [Timestamp('2023-05-19 15:08:00'), Timestamp('2023-05-19 15:10:00')],
                                                  'observation': ['Cooling Tower Fan Power', 'Cooling Tower Fan Power'],
                                                  'datapoint': [0.0, 3.0]})}

        dfDict, newFilesWithNanColumn = transform_columns_to_long_dataframes(
            myTestWideDataframe, myTestFilesWithNanColumn, myTestFileName, 'timepretty')

        assert dfDict.keys() == expectedDfDictOutput.keys()

        # Compare DataFrames for each key
        for key in dfDict.keys():
            df1 = dfDict[key]
            df2 = expectedDfDictOutput[key]
            assert df1.equals(df2)


class TestGetPointSummary:

    @pytest.mark.parametrize("my_get_point_summary_test_case", ['my_summary_statistics_table_test_case1', 'my_summary_statistics_table_test_case2', 'my_summary_statistics_table_test_case3'])
    def test_get_point_summary(self, my_get_point_summary_test_case, request):
        myTestPoint, myTestDf, expectedPointSummary = request.getfixturevalue(
            my_get_point_summary_test_case)
        assert get_point_summary(
            myTestPoint, myTestDf).equals(expectedPointSummary)

class TestGetStatisticalSummary:
    def test_get_statistical_summary(self, my_summary_statistics_table_test_case1, my_summary_statistics_table_test_case2, my_summary_statistics_table_test_case3):
        myTestPoint1, myTestDf1, expectedPointSummary = my_summary_statistics_table_test_case1
        myTestPoint2, myTestDf2, expectedPointSummary = my_summary_statistics_table_test_case2
        myTestPoint3, myTestDf3, expectedPointSummary = my_summary_statistics_table_test_case3
        expectedStatisticalSummaryTable = pd.DataFrame({'count': {'Test data point1': 2.0,
                                                                  'Test data point2': 3,
                                                                  'Test data point3': 0.0},
                                                        'mean': {'Test data point1': 1.0,
                                                                 'Test data point2': '',
                                                                 'Test data point3': ''},
                                                        'std': {'Test data point1': 1.414,
                                                                'Test data point2': '',
                                                                'Test data point3': ''},
                                                        'min': {'Test data point1': 0.0,
                                                                'Test data point2': '',
                                                                'Test data point3': ''},
                                                        '25%': {'Test data point1': 0.5,
                                                                'Test data point2': '',
                                                                'Test data point3': ''},
                                                        '50%': {'Test data point1': 1.0,
                                                                'Test data point2': '',
                                                                'Test data point3': ''},
                                                        '75%': {'Test data point1': 1.5,
                                                                'Test data point2': '',
                                                                'Test data point3': ''},
                                                        'max': {'Test data point1': 2.0,
                                                                'Test data point2': '',
                                                                'Test data point3': ''}}, dtype="object")

        assert get_statistical_summary(
            {myTestPoint1: myTestDf1, myTestPoint2: myTestDf2, myTestPoint3: myTestDf3}).equals(expectedStatisticalSummaryTable)


class TestMergeLongDataframesClass:

    @pytest.fixture(scope='class')
    def my_df_list(self):
        df = pd.DataFrame(np.array([['01/01/2023 00:00', 'a', 7], ['01/01/2023 00:08', 'a', 8], ['01/01/2023 00:16', 'a', 9]]),
                          columns=['t', 'd', 'v'])
        df1 = pd.DataFrame(np.array([['01/01/2023 00:00', 'b', 9], ['01/01/2023 00:08', 'b', 8], ['01/01/2023 00:16', 'b', 9]]),
                           columns=['t', 'd', 'v'])
        return [df, df1, df]

    @pytest.fixture(scope='class')
    def my_invalid_df_list(self):
        df = pd.DataFrame(np.array([['a', 7], ['a', 8], ['a', 9]]),
                          columns=['t', 'd'])
        df1 = pd.DataFrame(np.array([['b', 9], ['b', 8], ['b', 9]]),
                           columns=['t', 'd'])
        return [df, df1, df]

    @pytest.fixture(scope='class')
    def my_freq(self):
        return 5

    def test_merge_long_dataframes(self, my_df_list, my_freq):
        """Test the type of the wide dataframe merged from a list of long dataframes."""
        tmpMergedDf = merge_long_dataframes(my_df_list, my_freq)
        assert type(tmpMergedDf) == pd.DataFrame

    def test_merge_invalid_long_dataframes(self, my_invalid_df_list, my_freq):
        """Test the invalid long dataframe in input dfList"""
        with pytest.raises(ValueError):
            tmpMergedDf = merge_long_dataframes(my_invalid_df_list, my_freq)


class TestMergeWideDataframesClass:

    @pytest.fixture(scope='class')
    def my_df_list(self):
        df = pd.DataFrame(np.array([['01/01/2023 00:00', 1.5, 7], ['01/01/2023 00:05', 2.4, 8], ['01/01/2023 00:10', 23.2, 9]]),
                          columns=['Timestamp', 'col1', 'col2'])
        df1 = pd.DataFrame(np.array([['01/01/2023 00:00', 0.6, 9], ['01/01/2023 00:05', 5.5, 8], ['01/01/2023 00:10', 56.2, 9]]),
                           columns=['Timestamp', 'col3', 'col4'])
        return [df, df1]

    @pytest.fixture(scope='class')
    def my_missing_timestamp_df_list(self):
        df = pd.DataFrame(np.array([['01/01/2023 00:00', 1.5, 7], ['01/01/2023 00:05', 2.4, 8], ['01/01/2023 00:10', 23.2, 9]]),
                          columns=['time', 'col1', 'col2'])
        df1 = pd.DataFrame(np.array([['01/01/2023 00:00', 0.6, 9], ['01/01/2023 00:05', 5.5, 8], ['01/01/2023 00:10', 56.2, 9]]),
                           columns=['time', 'col3', 'col4'])
        return [df, df1]

    def test_merge_wide_dataframes(self, my_df_list):
        """Test the type of the wide dataframe merged from a list of wide dataframes."""
        tmpMergedDf = merge_wide_dataframes(my_df_list)
        assert type(tmpMergedDf) == pd.DataFrame

    def test_merge_missing_timestamp_wide_dataframes(self, my_missing_timestamp_df_list):
        """Test the missing timestamp column in input dfList"""
        with pytest.raises(ValueError):
            tmpMergedDf = merge_wide_dataframes(my_missing_timestamp_df_list)


class TestSaveFileToPortalClass:
    # TODO: call jobId and api from conftest.py we created it
    @pytest.fixture(scope="class")
    def my_api(self):
        return None

    @pytest.fixture(scope="class")
    def my_filePath(self):
        return ''

    @pytest.fixture(scope="class")
    def my_jobId(self):
        return ''

    @pytest.fixture(scope="class")
    def my_nodeName(self):
        return ''

    @pytest.fixture(scope='class')
    def my_removeFile(self):
        return False

    def test_save_missing_file_to_portal(self, my_api, my_filePath, my_jobId, my_nodeName, my_removeFile):
        """Test saving missing file to portal"""
        with pytest.raises(EtlError):
            url2s3 = save_file_to_portal(
                my_api, my_filePath, my_jobId, my_nodeName, my_removeFile)


class TestGetBuildingDataClass:

    @pytest.fixture(scope='class')
    def my_bCode(self):
        return 'datatest'

    @pytest.fixture(scope='class')
    def my_pCode(self):
        return 'datatest-PLANT-231'

    @pytest.fixture(scope='class')
    def my_prod_api(self):
        api = create_api('production')
        return api

    def test_get_building_data(self, my_bCode, my_pCode, my_prod_api):
        buildingData = get_building_data(my_bCode, my_pCode, my_prod_api)
        assert 'plantEquipment' in buildingData.keys()

    def test_get_building_data_invalid_pCode(self, my_bCode, my_prod_api):
        with pytest.raises(ValueError, match='buildingData not exist in jobData.'):
            buildingData = get_building_data(my_bCode, "testInvalid", my_prod_api)

    def test_get_building_data_invalid_bCode(self, my_pCode, my_prod_api):
        with pytest.raises(ValueError, match='buildingData not exist in jobData.'):
            buildingData = get_building_data("testInvalid", my_pCode, my_prod_api)


class TestGetEquipmentQuantitiesClass:

    @pytest.fixture(scope='class')
    def my_equip_data(self):
        with open(f'{TEST_DATA_DIR}/job463_building_data.json', 'r+') as f:
            buildingData = json.load(f)
        equipData = buildingData['plantEquipment']
        return equipData

    @pytest.fixture(scope='class')
    def my_equip_data_air_cooled(self):
        with open(f'{TEST_DATA_DIR}/job463_building_data.json', 'r+') as f:
            buildingData = json.load(f)
        equipData = buildingData['plantEquipment']
        equipData.pop(CDWP_TYPE)
        equipData.pop(CT_TYPE)
        equipData.pop(HEADER_TYPE)
        return equipData


    def test_get_equipment_quantities_for_water_cooled_plant(self, my_equip_data):
        equipQtyDict = get_equipment_quantities(my_equip_data)
        assert all(equip in equipQtyDict for equip in EQUIP_TYPE_LIST)
        assert equipQtyDict[HEADER_TYPE] > 0
        assert equipQtyDict[CDWP_TYPE] > 0
        assert equipQtyDict[CT_TYPE] > 0

    def test_get_equipment_quantities_for_air_cooled_plant(self, my_equip_data_air_cooled):
        equipQtyDict = get_equipment_quantities(my_equip_data_air_cooled)
        
        assert all(equip in equipQtyDict for equip in EQUIP_TYPE_LIST)
        assert equipQtyDict[HEADER_TYPE] == 0
        assert equipQtyDict[CDWP_TYPE] == 0
        assert equipQtyDict[CT_TYPE] == 0


class TestGetActiveAndHiddenEquipmentsClass:

    @pytest.fixture(scope='class')
    def my_building_data(self):
        with open(f'{TEST_DATA_DIR}/job463_building_data.json', 'r+') as f:
            buildingData = json.load(f)
        return buildingData

    @pytest.fixture(scope='class')
    def my_building_data_no_hidden(self):
        with open(f'{TEST_DATA_DIR}/job463_building_data.json', 'r+') as f:
            buildingData = json.load(f)
        buildingData['plantGroups'] = [g for g in buildingData['plantGroups'] if g['groupCategory'] != 'hidden']
        return buildingData

    def test_get_active_and_hidden_equipments(self, my_building_data):
        activeEquipDict, hiddenEquipList = get_active_and_hidden_equipments(my_building_data)
        assert activeEquipDict[CH_TYPE] == [1, 2, 4]
        assert hiddenEquipList == ['cooling-tower-2', 'condenser-water-pump-2', 'chilled-water-pump-1', 'chiller-3']

    def test_get_active_and_hidden_equipments_no_hidden(self, my_building_data_no_hidden):
        activeEquipDict, hiddenEquipList = get_active_and_hidden_equipments(my_building_data_no_hidden)
        assert activeEquipDict[CH_TYPE] == [1, 2, 3, 4]
        assert hiddenEquipList == []


class TestGetEquipmentMetadataClass:

    @pytest.fixture(scope='class')
    def my_equip_data(self):
        with open(f'{TEST_DATA_DIR}/job463_building_data.json', 'r+') as f:
            buildingData = json.load(f)
        equipData = buildingData['plantEquipment']
        return equipData

    @pytest.fixture(scope='class')
    def my_equip_data_air_cooled(self):
        with open(f'{TEST_DATA_DIR}/job463_building_data.json', 'r+') as f:
            buildingData = json.load(f)
        equipData = buildingData['plantEquipment']
        equipData.pop(CDWP_TYPE)
        equipData.pop(CT_TYPE)
        equipData.pop(HEADER_TYPE)
        return equipData


    def test_get_equipment_metadata_for_water_cooled_plant(self, my_equip_data):
        equipDict = get_equipment_metadata(my_equip_data)
        assert all(equip in equipDict for equip in EQUIP_TYPE_LIST)
        for num in equipDict[CH_TYPE].keys():
            assert 'cooling-capacity' in equipDict[CH_TYPE][num]

    def test_get_equipment_metadata_for_air_cooled_plant(self, my_equip_data_air_cooled):
        equipDict = get_equipment_metadata(my_equip_data_air_cooled)
        
        assert all(equip in equipDict for equip in EQUIP_TYPE_LIST)
        for num in equipDict[CH_TYPE].keys():
            assert 'cooling-capacity' in equipDict[CH_TYPE][num]
        assert equipDict[HEADER_TYPE] == {}
        assert equipDict[CDWP_TYPE] == {}
        assert equipDict[CT_TYPE] == {}


class TestGetHeadersClass:

    @pytest.fixture(scope='class')
    def my_building_data(self):
        with open(f'{TEST_DATA_DIR}/job463_building_data.json', 'r+') as f:
            buildingData = json.load(f)
        return buildingData

    @pytest.fixture(scope='class')
    def my_building_data_no_headers(self):
        with open(f'{TEST_DATA_DIR}/job463_building_data.json', 'r+') as f:
            buildingData = json.load(f)
        buildingData['plantEquipment'].pop(HEADER_TYPE)
        buildingData['plantGroups'] = None
        return buildingData

    @pytest.fixture(scope='class')
    def my_building_data_multi_headers(self):
        with open(f'{TEST_DATA_DIR}/job463_building_data_multi_headers.json', 'r+') as f:
            buildingData = json.load(f)
        return buildingData

    @pytest.fixture(scope='class')
    def my_building_data_invalid(self):
        with open(f'{TEST_DATA_DIR}/job463_building_data_multi_headers.json', 'r+') as f:
            buildingData = json.load(f)
        buildingData['plantEquipment'][HEADER_TYPE] = buildingData['plantEquipment'][HEADER_TYPE][:1]
        return buildingData

    def test_get_headers_invalid(self, my_building_data_invalid):
        with pytest.raises(ValueError, match='please check your plant configuration.'):
            headerDict = get_headers(my_building_data_invalid)

    def test_get_headers(self, my_building_data):
        headerDict = get_headers(my_building_data)
        assert 'singleheader' in headerDict.keys()

    def test_get_headers_no_header(self, my_building_data_no_headers):
        headerDict = get_headers(my_building_data_no_headers)
        assert headerDict == {}

    def test_get_headers_multi_headers(self, my_building_data_multi_headers):
        headerDict = get_headers(my_building_data_multi_headers)
        assert len(headerDict.keys()) > 1



class TestGetRenamedAndUnnamedColumns:

    @pytest.fixture(scope='class')
    def my_header_df(self):
        headerDf = pd.read_csv(f'{TEST_DATA_DIR}/job463_header.csv')
        headerDf.fillna("", inplace=True)
        return headerDf

    def test_get_renamed_and_unnamed_columns(self, my_header_df):
        renamed_cols, unnamed_cols = get_renamed_and_unnamed_columns(my_header_df)
        assert "Common Condenser Water Leaving Temp" in renamed_cols
        assert "CT-L29-B-GEN CT-LTSP-COMMON Trend - Present Value () (deg C)" in unnamed_cols
        assert len(my_header_df) == len(renamed_cols) + len(unnamed_cols) + 1 # rename+uname+Timestamp


class TestGetDailyBaseline:
    
    @pytest.fixture(scope='class')
    def my_time_interval(self):
        return 15

    @pytest.fixture(scope='class')
    def my_ch_num(self):
        return 4

    @pytest.fixture(scope='class')
    def my_ct_num(self):
        return 2

    @pytest.fixture(scope='class')
    def my_transformed_df(self):
        df = pd.read_csv(f'{TEST_DATA_DIR}/job463_transformation.csv')
        return df

    @pytest.fixture(scope='class')
    def sample_raw_df(self):
        raw_df = pd.read_csv(f'{TEST_DATA_DIR}/job463_raw_baseline.csv')
        raw_df['Timestamp'] = pd.to_datetime(raw_df['Timestamp'], format='%Y-%m-%d %H:%M:%S')
        return raw_df

    @pytest.fixture(scope='class')
    def sample_daily_df(self):
        daily_df = pd.read_csv(f'{TEST_DATA_DIR}/job463_daily_baseline.csv')
        daily_df['date'] = pd.to_datetime(daily_df['date'], format='%Y-%m-%d').dt.date
        return daily_df


    def test_get_daily_baseline(self, my_time_interval, my_ch_num, my_ct_num, my_transformed_df, sample_raw_df, sample_daily_df):
        raw_df, daily_df = get_daily_baseline(my_time_interval, my_ch_num, my_ch_num, my_ch_num, my_ct_num, my_transformed_df)
        assert_frame_equal(raw_df, sample_raw_df)
        assert_frame_equal(daily_df, sample_daily_df)


class TestGetHistoricalBaseData:

    @pytest.fixture(scope='class')
    def my_ch_num(self):
        return 4

    @pytest.fixture(scope='class')
    def my_ct_num(self):
        return 2

    @pytest.fixture(scope='class')
    def my_transformed_df(self):
        df = pd.read_csv(f'{TEST_DATA_DIR}/job463_transformation.csv')
        return df

    @pytest.fixture(scope='class')
    def my_min_load_thres_list(self):
        return [0.1, 0.1, 0, 0]

    @pytest.fixture(scope='class')
    def my_invalid_min_load_thres_list(self):
        return [0.1, 0, 0]

    @pytest.fixture(scope='class')
    def sample_historical_df(self):
        df = pd.read_csv(f'{TEST_DATA_DIR}/job463_historical_data.csv')
        return df

    def test_invalid_get_historical_base_data(self, my_ch_num, my_ct_num, my_transformed_df, my_invalid_min_load_thres_list):
        with pytest.raises(ValueError):
            historicalDf = get_historical_base_data(my_ch_num, my_ch_num, my_ch_num, my_ct_num, my_ct_num, my_transformed_df, my_invalid_min_load_thres_list)

    def test_get_historical_base_data(self, my_ch_num, my_ct_num, my_transformed_df, my_min_load_thres_list, sample_historical_df):
        historicalDf = get_historical_base_data(my_ch_num, my_ch_num, my_ch_num, my_ct_num, my_ct_num, my_transformed_df, my_min_load_thres_list)
        assert_frame_equal(historicalDf, sample_historical_df)



class TestParseTimestampColumn:

    @pytest.fixture(scope='class')
    def my_time_series1(self):
        timeSeries = pd.Series([
            '2022-03-11 00:00:00',
            '2022-03-11 00:05:00',
            '2022-03-11 00:10:00',
        ])
        return timeSeries

    @pytest.fixture(scope='class')
    def my_time_series2(self):
        timeSeries = pd.Series([
            '11/03/2022 00:00',
            '11/03/2022 00:05',
            '11/03/2022 00:10',
        ])
        return timeSeries

    @pytest.fixture(scope='class')
    def my_time_series3(self):
        timeSeries = pd.Series([
            '11/03/22 00:00',
            '11/03/22 00:05',
            '11/03/22 00:10',
        ])
        return timeSeries

    @pytest.fixture(scope='class')
    def my_invalid_time_series(self):
        timeSeries = pd.Series([
            '11/23/22 00:00',
            '11/23/22 00:05',
            '11/23/22 00:10',
        ])
        return timeSeries


    def test_parse_timestamp_column_format1(self, my_time_series1):
        parsed_time_series1 = parse_timestamp_column(my_time_series1)
        assert is_datetime(parsed_time_series1)

    def test_parse_timestamp_column_format2(self, my_time_series2):
        parsed_time_series2 = parse_timestamp_column(my_time_series2)
        assert is_datetime(parsed_time_series2)

    def test_parse_timestamp_column_format3(self, my_time_series3):
        parsed_time_series3 = parse_timestamp_column(my_time_series3)
        assert is_datetime(parsed_time_series3)

    def test_parse_timestamp_column_invalid(self, my_invalid_time_series):
        with pytest.raises(ValueError, match='does not fit existing formats.'):
            parse_timestamp_column(my_invalid_time_series)



class TestFindStageOneChs:

    @pytest.fixture(scope='class')
    def my_cap_list(self):
        return [1000,1500,1000]

    @pytest.fixture(scope='class')
    def my_cap_list_with_none(self):
        return [np.nan,1500,None]

    def test_find_stage_one_chs(self, my_cap_list):
        stage1Ch = find_stage_one_chs(my_cap_list)
        assert stage1Ch == 1

    def test_find_stage_one_chs_with_none(self, my_cap_list_with_none):
        stage1Ch = find_stage_one_chs(my_cap_list_with_none)
        assert stage1Ch == 2



class TestGetSystemDataDrops:

    @pytest.fixture(scope='class')
    def my_stage_one_ch_list(self):
        return [1]

    @pytest.fixture(scope='class')
    def my_load_data(self):
        loadData = np.array([
            [0, 1000,  500, 0, 0,    0, 1000],
            [0, 1000,    0, 0, 0,    0, 1000],
            [0,    0, 1000, 0, 0,    0, 1000]
        ])
        return loadData

    @pytest.fixture(scope='class')
    def my_interval(self):
        return 5

    def test_get_system_data_drops(self, my_stage_one_ch_list, my_load_data, my_interval):
        dropsFlagData = get_system_data_drops(my_stage_one_ch_list, my_load_data, my_interval)
        np.testing.assert_array_equal(dropsFlagData , np.array([ 1, np.nan, np.nan,1,np.nan, 1, np.nan]))


class TestGetWeightedCOP:

    @pytest.fixture(scope='class')
    def my_timestamp(seldf):
        return np.array(pd.to_datetime(['2023-05-19 15:08', '2023-05-19 15:09', '2023-05-20 15:10']))

    @pytest.fixture(scope='class')
    def my_actual_COP(seldf):
        return np.array([6.5, 5.9, 8.8])

    @pytest.fixture(scope='class')
    def my_expected_COP(seldf):
        return np.array([5.5, 7.1, 8.2])

    @pytest.fixture(scope='class')
    def my_kWr(seldf):
        return np.array([597.3, 889.6, 743.1])

    @pytest.fixture(scope='class')
    def my_invalid_timestamp(seldf):
        return np.array(['2023-05-19 15:08', '2023-05-19 15:09', '2023-05-20 15:10'])

    @pytest.fixture(scope='class')
    def my_invalid_actual_COP(seldf):
        return np.array(['6.5', '5.9', '8.8'])

    @pytest.fixture(scope='class')
    def my_invalid_kWr(seldf):
        return np.array(['597', '889', '743'])

    def test_get_weighted_COP(self, my_timestamp, my_actual_COP, my_expected_COP, my_kWr):
        date, weighted_actual_cop, weighted_expected_cop = get_weighted_COP(my_timestamp, my_actual_COP, my_expected_COP, my_kWr)
        np.testing.assert_array_equal(date.astype(str), np.array(['2023-05-19', '2023-05-20']))
        np.testing.assert_array_equal(weighted_actual_cop, np.array([6.141, 8.8]))
        np.testing.assert_array_equal(weighted_expected_cop, np.array([6.457, 8.2]))

    def test_invalid_timestamp_get_weighted_COP(self, my_invalid_timestamp, my_actual_COP, my_expected_COP, my_kWr):
        with pytest.raises(ValueError, match='Data type for timestamp must be datetime-like.'):
            get_weighted_COP(my_invalid_timestamp, my_actual_COP, my_expected_COP, my_kWr)

    def test_invalid_COP_get_weighted_COP(self, my_timestamp, my_invalid_actual_COP, my_expected_COP, my_kWr):
        with pytest.raises(ValueError, match='Data type for actual_cop must be numerical.'):
            get_weighted_COP(my_timestamp, my_invalid_actual_COP, my_expected_COP, my_kWr)

    def test_invalid_kWr_get_weighted_COP(self, my_timestamp, my_actual_COP, my_expected_COP, my_invalid_kWr):
        with pytest.raises(ValueError, match='Data type for kwr must be numerical.'):
            get_weighted_COP(my_timestamp, my_actual_COP, my_expected_COP, my_invalid_kWr)



class TestGetPostImpCdw3dUrls:

    @pytest.fixture(scope='class')
    def my_prod_api(self):
        return create_api('production')

    @pytest.fixture(scope='class')
    def my_cdwFigureDict(self):

        my_cdwFigureDict = {
            'header_1': {
                'stage_0010': {
                    'url': {
                        'metric': 'https://exergenics-public.s3.ap-southeast-2.amazonaws.com/2023/11/27/3a09bf9202834b92b8889a418d043373__ex.json',
                        'imperial': 'https://exergenics-public.s3.ap-southeast-2.amazonaws.com/2023/11/27/86184628424049b9b0bd2500e3e50e11__ex.json',
                        'mixed': 'https://exergenics-public.s3.ap-southeast-2.amazonaws.com/2023/11/27/5cb2f376f5324245a5d65fb501dd7de8__ex.json'
                    },
                    'identical_stages': ['stage_1000']
                },
                'stage_1010': {
                    'url': {
                        'metric': 'https://exergenics-public.s3.ap-southeast-2.amazonaws.com/2023/11/27/fd5e6061791c47af8274a6d6a4413a3d__ex.json',
                        'imperial': 'https://exergenics-public.s3.ap-southeast-2.amazonaws.com/2023/11/27/152459b1d6d14dfaa3f4bcf2b2b86075__ex.json',
                        'mixed': 'https://exergenics-public.s3.ap-southeast-2.amazonaws.com/2023/11/27/13b87b2c78cf4fe686ecc8867779e015__ex.json'
                        },
                    'identical_stages': []
                }
            }
        }
        return my_cdwFigureDict

    @pytest.fixture(scope='class')
    def my_invalid_mv_transformed_df(self):
        df = pd.read_csv(f'{TEST_DATA_DIR}/job463_transformation.csv')
        return df

    @pytest.fixture(scope='class')
    def my_mv_transformed_df(self):
        df = pd.read_csv(f'{TEST_DATA_DIR}/job463_transformation_with_chiller_stage.csv')
        return df

    def test_invalid_get_post_imp_cdw_3d_urls(self, my_prod_api, my_cdwFigureDict, my_invalid_mv_transformed_df):
        with pytest.raises(ValueError):
            post_imp_cdw_3d_df = get_post_imp_cdw_3d_urls(my_prod_api, my_cdwFigureDict, my_invalid_mv_transformed_df)

    # def test_get_post_imp_cdw_3d_urls(self, my_prod_api, my_cdwFigureDict, my_mv_transformed_df):
    #     post_imp_cdw_3d_df = get_post_imp_cdw_3d_urls(my_prod_api, my_cdwFigureDict, my_mv_transformed_df)
    #     assert len(post_imp_cdw_3d_df) == 6

class TestEnglishConverterClass:

    @pytest.mark.parametrize("content, target, expected", [
    ("optimisation", 'us', "optimization"),
    ("optimisation", 'uk', "optimisation"),
    ("optimization", 'us', "optimization"),
    ("optimization", 'uk', "optimisation"),
    ])
    def test_english_converter(self, content, target, expected):
        assert english_converter(content, target) == expected



    @pytest.mark.parametrize("content, target, expected", [
    ("optimization", 'au', "optimisation"),
    (123, 'uk', "123"),
    ])
    def test_english_converter_invalid_target(self, content, target, expected):
        with pytest.raises(ValueError):
            expected = english_converter(content, target)

class TestFigCOPToKWTon:

    @pytest.fixture(scope='class')
    def my_scatter_fig(self):
        fig = go.Figure(data=[
            go.Scatter3d(x=[1, 2, 3], y=[4, 5, 6], z=[7, 8, 9], mode='markers', hovertemplate="<br>".join([
                "Lift (°C): %{x:0.2f}",
                "Load: %{y:.00%}",
                "COP: %{z:0.2f}"
            ])),
        ])
        return fig
        
    @pytest.fixture(scope='class')
    def my_surface_fig(self):
        fig = go.Figure(data=[
            go.Surface(x=[1, 2, 3], y=[4, 5, 6], z=[[7, 8, 9], [7, 8, 9], [7, 8, 9]], hovertemplate="<br>".join([
                "Lift (°C): %{x:0.2f}",
                "Load: %{y:.00%}",
                "COP: %{z:0.2f}"
            ]))
        ])
        return fig

    def test_fig_COP_to_kW_ton_scatter(self, my_scatter_fig):

        fig = fig_COP_to_kW_ton(my_scatter_fig)
        
        # Check if the z-axis values are converted to KW/Ton
        for trace in fig.data:
            np.testing.assert_almost_equal(trace.z, np.true_divide(3.517, np.clip([7, 8, 9], 1, None)), decimal=3)

        # Check if the hovertemplate is updated
        for trace in fig.data:
             assert "KW/Ton" in trace.hovertemplate

        # Check if the layout is updated
        assert fig.layout.scene.zaxis.title.text == "KW/Ton"
        assert fig.layout.scene.zaxis.tick0 == 0.1
        assert fig.layout.scene.zaxis.dtick == 0.2
        assert fig.layout.scene.zaxis.range == (0, 1.2)

    def test_fig_COP_to_kW_ton_surface(self, my_surface_fig):

        fig = fig_COP_to_kW_ton(my_surface_fig)
        
        # Check if the z-axis values are converted to KW/Ton
        for trace in fig.data:
            np.testing.assert_almost_equal(trace.z, np.true_divide(3.517, np.clip([[7, 8, 9], [7, 8, 9], [7, 8, 9]], 1, None)), decimal=3)

        # Check if the hovertemplate is updated
        for trace in fig.data:
             assert "KW/Ton" in trace.hovertemplate

        # Check if the layout is updated
        assert fig.layout.scene.zaxis.title.text == "KW/Ton"
        assert fig.layout.scene.zaxis.tick0 == 0.1
        assert fig.layout.scene.zaxis.dtick == 0.2
        assert fig.layout.scene.zaxis.range == (0, 1.2)

    
class TestFigFahrenheitToCelsius:

    @pytest.fixture(scope='class')
    def my_fig(self):
        fig = go.Figure(data=[
            go.Scatter3d(x=[1, 2, 3], y=[4, 5, 6], z=[7, 8, 9], mode='markers', name='Optimised', hovertemplate="<br>".join([
                "Lift (°C): %{x:0.2f}",
                "Load: %{y:.00%}",
                "COP: %{z:0.2f}"
            ])),
            go.Surface(x=[1, 2, 3], y=[4, 5, 6], z=[[7, 8, 9], [7, 8, 9], [7, 8, 9]], name='Model', hovertemplate="<br>".join([
                "Lift (°C): %{x:0.2f}",
                "Load: %{y:.00%}",
                "COP: %{z:0.2f}"
            ]))
        ])
        fig.update_layout(scene=dict(
                xaxis=dict(range=[30,0])))
        return fig


    def test_fig_fahrenheit_to_celsius(self, my_fig):

        fig = fig_fahrenheit_to_celsius(my_fig)
        
        # Check if the x-axis values are converted to Celsius
        for trace in fig.data:
            np.testing.assert_almost_equal(trace.x, np.array([j * F_TO_C_RANGE for j in [1, 2, 3]]), decimal=3)

        # Check if the hovertemplate/trace name are updated
        for trace in fig.data:
             assert "Lift (°C)" not in trace.hovertemplate
             assert "Lift (°F)" in trace.hovertemplate
             assert "Optimised" not in trace.name

        # Check if the layout is updated
        assert fig.layout.scene.xaxis.title.text == "Lift (°F)"
        assert fig.layout.scene.xaxis.nticks == 6
        assert fig.layout.scene.xaxis.range == (54, 0)


class TestGetPostImpSim3dUrls:

    @pytest.fixture(scope='class')
    def my_prod_api(self):
        return create_api('production')

    @pytest.fixture(scope='class')
    def my_sim3dFigureDict(self):

        sim3dFigureDict = {
            1: {
                'traceNumberList': ['1', '2', '3', '4'],
                'jsonUrl': 'https://exergenics-public.s3.ap-southeast-2.amazonaws.com/2023/11/30/749a9afa1fc64ec781b2944b1330f95a__/tmp/job820_3d_curve_ch1.json'
            }
        }
        return sim3dFigureDict

    @pytest.fixture(scope='class')
    def my_mv_transformed_df(self):
        df = pd.read_csv(f'{TEST_DATA_DIR}/job463_transformation_with_chiller_stage.csv')
        return df

    # def test_get_post_imp_sim_3d_urls(self, my_prod_api, my_sim3dFigureDict, my_mv_transformed_df):
    #     post_imp_sim_3d_df = get_post_imp_sim_3d_urls(my_prod_api, my_sim3dFigureDict, my_mv_transformed_df)
    #     assert len(post_imp_sim_3d_df) == 3


class TestMapDataSelection:

    @pytest.fixture(scope='class')
    def my_selection_df_v2(self):
        selection_df = pd.DataFrame({
            'point': ['point1', 'point2', 'point3'],
            'selected': ['Y', 'N', 'Y']
        })
        return selection_df
        
    @pytest.fixture(scope='class')
    def my_selection_df_v1(self):
        selection_df = pd.DataFrame({
            'point': ['point1', 'point2', 'point3'],
            'selected-rows': [True, False, True]
        })
        return selection_df
      
class TestSkipDataSelection:

    @pytest.fixture(scope='class')
    def my_manifest(self):
        manifest = [
            {'point': 'point1'},
            {'point': 'point2'},
            {'point': 'point3'}
        ]
        return manifest

    @pytest.fixture(scope='class')
    def expected_selected(self):
        return ['point1', 'point3']

    def test_map_data_selection_v1(self, my_selection_df_v1, my_manifest, expected_selected):
        selected_manifest = map_data_selection(my_selection_df_v1, my_manifest, False)
        selected_counts = len([entry['selected'] for entry in selected_manifest if 'selected' in entry.keys()])
        assert selected_counts == len(expected_selected)

    def test_map_data_selection_v2(self, my_selection_df_v2, my_manifest, expected_selected):
        selected_manifest = map_data_selection(my_selection_df_v2, my_manifest)
        selected_counts = len([entry['selected'] for entry in selected_manifest if 'selected' in entry.keys()])
        assert selected_counts == len(expected_selected)



class TestMapHeaderMappingV1:

    @pytest.fixture(scope='class')
    def my_mappings_v1_df(self):
        v1_df = pd.DataFrame({
            'dt-client-headers': ['header1', 'header2', 'header3'],
            'dt-new-headers': ['new_header1', 'new_header2', 'header3']
        })
        return v1_df

    @pytest.fixture(scope='class')
    def expected_v2_dict(self):
        v2_dict = {'header1': 'new_header1', 'header2': 'new_header2'}
        return v2_dict


    def test_map_header_mapping_v1(self, my_mappings_v1_df, expected_v2_dict):

        v2_dict = map_header_mapping_v1(my_mappings_v1_df)
        assert v2_dict == expected_v2_dict

class TestSkipDataSelection:

    @pytest.fixture(scope='class')
    def my_manifest(self):
        manifest = [
            {'point': 'point1', 'interval': '5'},
            {'point': 'point2', 'interval': '10'},
            {'point': 'point3', 'interval': '5'},
            {'point': 'point4', 'interval': '15'}
        ]
        return manifest

    def test_get_selection_and_interval(self, my_manifest):
        manifest, timeInterval = get_selection_and_interval(my_manifest)
        selectedCounts = len([row for row in manifest if 'selected' in row.keys() and row['selected']=='Y'])
        assert selectedCounts == len(manifest)
        assert timeInterval == 5

class TestGetDefaultHistoricalFinal:

    @pytest.fixture(scope='class')
    def my_historicalBaseDataDf(self):
        df = pd.read_csv(f'{TEST_DATA_DIR}/job463_historical_data.csv')
        return df

    @pytest.fixture(scope='class')
    def smaple_historical_final_df(self):
        df = pd.read_csv(f'{TEST_DATA_DIR}/job463_historical_final_data.csv')
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df

    def test_get_default_historical_final(self, my_historicalBaseDataDf, smaple_historical_final_df):
        historicalFinalDf = get_default_historical_final(my_historicalBaseDataDf)
        assert 'ErrorDay' in historicalFinalDf.columns
        assert 'StageUp' in historicalFinalDf.columns
        assert_frame_equal(historicalFinalDf, smaple_historical_final_df)