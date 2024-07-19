import os
import zipfile
import sqlalchemy
try:
    from ..src.logger import ETLLogger as Logger
except:
    from logger import ETLLogger as Logger
import pandas as pd
import numpy as np
from pytz import timezone
from datetime import datetime
from typing import Union, Dict, Callable, Literal
from exergenics import exergenics
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from Levenshtein import distance as levenshtein_distance
import regex as re
import dateparser
from collections import Counter
from typing import Tuple, List
from functools import reduce
from sklearn.metrics import r2_score
import json
import uuid
from urllib.request import urlopen
import plotly.graph_objects as go
from eng import Target, TextFixer

from dotenv import load_dotenv
load_dotenv()


EXTENSIONS = ['csv', 'xlsx']
# The length threshold of a string where we consider the string as a point name
LENGTH_THRESHOLD = 10
# The maximum distance between two timestamp column headers that are considered similar
TIMESTAMP_HEADER_DISTANCE = 4
LOG_HEADER = ['timepretty', 'observation', 'datapoint']
TIME, NAME, VALUE = LOG_HEADER
N_COLUMN_LONG_DATA = 3  # The number of columns in a long-format data table
DEFAULT_POSITION_DAY = 0  # The default position of the day of month in timestamps
SUMMARY_COLUMNS = ['count', 'mean', 'std',
                   'min', '25%', '50%', '75%', 'max']
EMPTY_COLUMN_NAME_PREFIX = "Unnamed"  # Prefix of auto generated column name when column name is not found

CH_TYPE = 'chiller'
CHWP_TYPE = 'chilled-water-pump'
CDWP_TYPE = 'condenser-water-pump'
CT_TYPE = 'cooling-tower'
HEADER_TYPE = 'header'
EQUIP_TYPE_LIST = [CH_TYPE, CHWP_TYPE, CDWP_TYPE, CT_TYPE, HEADER_TYPE] # names for all equipment types from portal


TIMESTAMP = 'Timestamp'
DBT = 'Dry Bulb Temperature'
WBT = 'Wet Bulb Temperature'
LCHWT = 'Common Chilled Water Leaving Temp'
DBT_OPEN_WEAHTER = 'Dry Bulb Temperature (from openWeather)'
WBT_OPEN_WEAHTER = 'Wet Bulb Temperature (from openWeather)'
HUMID_OPEN_WEAHTER = 'Weather Air Humidity % (from openWeather)'
SYSTEM_LOAD = 'System Cooling Load'

POST_IMP_SCATTER_COLOR = 'green'
TON_TO_KWR = 3.51685
F_TO_C_RANGE = 1.8

logger = Logger(loggerName='Exergenics-ETL',
                component='python_package', subComponent='exergenics_etl')


class EtlError(Exception):
    """Exception raised for errors in ETL function."""

    def __init__(self, message="", *args):
        self.message = message
        super().__init__(self.message, *args)


def hello(name: str) -> None:
    """Says hello to someone.

    Args:
        name (str): The name of the person to greet.

    Returns:
        None
    """

    print(f"Hello {name}!")

    return


def create_api(environment: str, component_name: str = "") -> exergenics.ExergenicsApi:
    """Creates an authenticated Exergenics API object. Environment variables, EXERGENICS_API_USERNAME
    and EXERGENICS_API_PASSWORD, are required.

    Args:
        environment (str): The environment where the API will be used. Must be either 'staging' or 'production'.
        component_name (str, optional): The name of the component that will be using the API.

    Raises:
        ValueError: If the input environment is not ‘staging’ or ‘production’.
        RuntimeError: If the username or password for API authentication is not found in environment variables.

    Returns:
        exergenics.ExergenicsApi: An authenticated Exergenics API object.
    """

    # Validate input environment
    try:
        assert (environment == 'staging') or (environment == 'production')
    except AssertionError:
        raise ValueError(
            f"Invalid input argument: environment = {environment}")

    # Get credentials from environment variables
    api_username = os.getenv('EXERGENICS_API_USERNAME')
    api_password = os.getenv('EXERGENICS_API_PASSWORD')
    try:
        assert api_username is not None, "EXERGENICS_API_USERNAME not found in environment variables!"
        assert api_password is not None, "EXERGENICS_API_PASSWORD not found in environment variables!"
    except AssertionError as e:
        raise RuntimeError(e)

    if environment == "staging":
        production = False
    elif environment == 'production':
        production = True

    api = exergenics.ExergenicsApi(
        username=api_username, password=api_password, useProductionApi=production)
    if component_name:
        api.setComponentName(component_name)

    if not api.authenticate():
        exit(0)

    return api


def create_sql_engine(databaseName: str, host: str, user: str, password: str) -> sqlalchemy.engine.base.Engine:
    """Formats a URL using the provided credentials
    and creates a connectable MySQL database engine object based on the URL.

    Args:
        databaseName (str): The name of the MySQL database to connect to.
        host (str): The hostname of the MySQL server.
        user (str): The MySQL user to authenticate as.
        password (str): The password for the MySQL user.

    Raises:
        RuntimeError: If the password is missing

    Returns:
        sqlalchemy.engine.base.Engine: A connectable MySQL engine object.
    """

    try:
        url = f"mysql+pymysql://{user}:{quote_plus(password)}@{host}:3306/{databaseName}"
    except TypeError:
        raise TypeError(
            f"Input password is not a string: password = {password}")
    engine = create_engine(url)

    return engine


def get_time_now(timestampFormat="%Y_%m_%d_%H%M") -> str:
    """Returns the current date and time in Melbourne the format 'YYYY_MM_DD_HHMM'.

    Returns:
        str: A string representing the current date and time in Melbourne.
    """
    now = datetime.now().astimezone(tz=timezone('Australia/Melbourne'))
    dt_string = now.strftime(timestampFormat)
    return dt_string



def structure_slack_message(bCode: str = "", jobId: Union[int, str] = "", message: str = "") -> str:
    """Creates a formatted Slack message string.

    Args:
        bCode (str, optional): The building code associated with the job. Defaults to "".
        jobId (Union[int, str], optional): The job ID. Defaults to "".
        message (str, optional): The message to be sent to a Slack channel. Defaults to "".

    Returns:
        str: A formatted Slack message.
    """

    return f'Time: {get_time_now()}\nBcode: {bCode}\nJob: {jobId}\n{message}'


def create_tmp_folder(tmpFolderName: str = "temp") -> None:
    """Creates a temporary folder with the given name if it does not already exist.

    Args:
        tmpFolderName (str, optional): The name of the temporary folder to create. Defaults to "temp".

    Raises:
        Exception: If the temporary folder was not successfully created.
    """

    if not os.path.exists(tmpFolderName):
        os.makedirs(tmpFolderName)

    try:
        assert os.path.exists(tmpFolderName)
    except AssertionError as e:
        raise Exception(
            f"temp folder doesn't not existing after attempting to make the directory: {e}")

    return


def generate_CSV_name(pointName: str) -> str:
    """Generates a CSV name for the trend log of a given data point name.

    Args:
        pointName (str): The name of a data point

    Returns:
        str: The CSV name for the data point
    """

    # Follow logic from portal-php code to rename file names
    pointName = pointName.replace(" ", "_").replace(
        "/", "-").replace("~", "-").replace("&", "and").replace("%", "-")
    return f'{pointName}.csv'


def strftime_for_NaT(timestamp: Union[pd.Timestamp, pd._libs.tslibs.nattype.NaTType], log_time_format: str = "%d/%m/%Y %H:%M") -> str:
    """Formats a pandas Timestamp object as a string in the specified format.
    Returns an empty string if the type of the timestamp is pandas.NaT.

    Args:
        timestamp (Union[pd.Timestamp, pd._libs.tslibs.nattype.NaTType]: A pandas Timestamp object to format.
        log_time_format (str, optional): the format of the output timestamp string. Defaults to "%d/%m/%Y %H:%M".

    Returns:
        str: A formatted string representing the provided timestamp or an empty string if the timestamp is pandas.NaT.
    """

    if timestamp is pd.NaT:
        return ""
    else:
        try:
            return timestamp.strftime(log_time_format)
        except AttributeError as e:
            raise AttributeError(
                f'Cannot convert this timestamp to its equivalent string: timestamp = {timestamp}, {e}')


def generate_one_manifest_row(pointName: str, dfLog: pd.DataFrame) -> Dict:
    """Generates manifest data for a data point from its trend log.

    Args:
        pointName (str): The name of the data point.
        dfLog (pd.DataFrame): A pandas DataFrame containing the trend log for the data point.

    Returns:
        Dict: A dictionary of manifest data for the data point.
    """

    # Get start/end time for the trend log of the point
    startTime = dfLog[TIME].min()
    endTime = dfLog[TIME].max()

    # Generate manifest fields for the data point
    fileField = generate_CSV_name(pointName)
    rowsField = len(dfLog)
    intervalField = calculate_time_interval(dfLog[TIME])
    fromField, toField, dataFromField, dataToField = [
        strftime_for_NaT(t) for t in [startTime, endTime, startTime, endTime]]

    # Format manifest fields into a dictionary
    metadataDict = {"point": pointName,
                    "file": fileField,
                    "rows": rowsField,
                    "from": fromField,
                    "to": toField,
                    "dataFrom": dataFromField,
                    "dataTo": dataToField,
                    "interval": intervalField}

    return metadataDict


def generate_output_file_path(module: str, extension: str, bCode: str = "", pCode: str = "", category: str = "", jobId: Union[int, str] = "", path: str = "") -> str:
    """Generates a local file path for an output file.

    Args:
        module (str): The name of the module generating the output file, such as, transformation or preheader.
        extension (str): The file extension of the output file.
        bCode (str, optional): The building code associated with the file. Defaults to "".
        pCode (str, optional): The plant code associated with the file. Defaults to "".
        category (str, optional): The category of the output file, such as, zipfile or manifest. Defaults to "".
        jobId (Union[int, str], optional): The job ID associated with the output file. Defaults to "".
        path (str, optional): The directory path where the output file should be saved. Defaults to "".

    Returns:
        str: The file path for the output file.
    """

    # Format individual parts of the output file path string
    timeNow = get_time_now()
    if category:
        category = "_" + category
    if bCode:
        bCode = "_" + bCode
    if pCode:
        pCode = "_" + pCode
    if jobId:
        jobId = "_job" + str(jobId)

    outputFilePath = f"{timeNow}{bCode}{pCode}{jobId}_{module}{category}.{extension}"

    # Append the file path to the end of the directory path if the directory path is provided
    if path:
        if path.endswith('/'):
            outputFilePath = f"{path}{outputFilePath}"
        else:
            outputFilePath = f"{path}/{outputFilePath}"

    return outputFilePath


def get_file_name_list(zf: zipfile.ZipFile) -> list:
    """Open manual zipfile and return a list of unique data files

    Args:
        zf (zipfile.ZipFile): ZipFile object containing CSVs.

    Returns:
        list: A list of file names in the zipfile object input. 
    """

    logger = Logger()

    filesIncluded = [j for extension in EXTENSIONS for j in zf.namelist()
                     if j.endswith(extension) and
                     not j.startswith('__MACOSX') and
                     not ('/~' in j)]

    filesExcluded = list(set(zf.namelist()) - set(filesIncluded))

    logger.info(
        f'Reading {len(filesIncluded)} data files from manual zipfile: {filesIncluded}\n')
    if filesExcluded:
        logger.info(
            f'{len(filesExcluded)} data files in manual zipfile NOT included: {filesExcluded}\n')

    return filesIncluded


class SkipRowsMachine:
    """
    A class to provide automated header rows skipping for Pandas Dataframe.
    Skip non-data rows on top of data files in the format of CSV or Excel.
    """

    def __init__(self, nRowsVerify: int = 10):
        """Constructs all the necessary attributes for the SkipRowsMachine object.

        Args:
            nRowsVerify (int, optional): Numbers of rows to verify in each CSV. Defaults to 10.
        """
        self.logger = Logger()
        self.skiprows = None
        self.nRowsVerify = nRowsVerify

    def validate_headers(self, headers: pd.Series):
        """This function validates the value of skiprows by checking the types of header.
        A header should not be a column header that is automatically generated by Pandas.
        It should be a non-nan string only, ideally with a length greater than 5,
        and not a string of numbers.

        Args:
            df0 (pd.DataFrame): Pandas DataFrame for header validation.

        Raises:
            EtlError: If invalid column headers are found.
        """

        # Validate each header
        for v in headers:

            try:
                # Check header is a string but not a string of numbers
                pd.to_numeric(v)

                # Raise and log error
                errorMessage = f"Test Failed: Can do to_numeric on header: {v} of type {type(v)}; \
                    the header can't be numbers, a string of numbers, an empty string, None, np.nan or boolean."
                self.logger.error(errorMessage)
                userMessage = "Column names cannot be numbers, empty strings or True/False."
                raise EtlError(userMessage)

            except ValueError as e:
                pass

            try:
                assert not v.startswith(EMPTY_COLUMN_NAME_PREFIX)
            except AssertionError as e:
                self.logger.error(e)
                raise EtlError(e)

            try:
                assert len(v) > 5, f'Expected the length of header to be ideally greater than 5 \
                    but the actual length of header "{v}" was {len(v)}'
            except AssertionError as e:
                self.logger.warn(e)

        return
    
    def _auto_skiprows(self, fileName: str, zf: zipfile.ZipFile, readFileFunc: Callable) -> Tuple[pd.DataFrame, int, int]:

        """
        Automatically determines the number of rows to skip in a CSV or XLSX file to locate the header row.

        Args:
            fileName (str): The name of the file within the zip file to be read.
            zf (zipfile.ZipFile): The ZipFile object containing the file.
            readFileFunc (Callable): A function to read the file.

        Returns:
            Tuple[pd.DataFrame, int, int]: A tuple containing the pandas DataFrame (`df`), the number of rows to skip (`skiprows`),
            and the row ID of the header (`headerRowID`).

        Raises:
            EtlError: If reading file failed after trying from 1 to 10 as the skiprows value.

        """

        # Try reading the file with different numbers of rows to skip
        skiprowsTrials = range(10)

        for skiprowsTrial in skiprowsTrials:
            try:
                # Try reading the CSV file with the current number of rows to skip
                df = readFileFunc(zf.open(fileName),
                                 skiprows=skiprowsTrial, header=None, nrows=skiprowsTrial+12)
                skiprows = skiprowsTrial

                # Find the row ID of header and compute the number of rows to skip
                col1 = df[df.columns[1]]
                headerRowID = col1.dropna().index[0]  # The row number of the first non-na value
                skiprows = skiprowsTrial + headerRowID

                self.logger.info(
                    f'Found skiprows value = {skiprowsTrial}')

                return df, skiprows, headerRowID

            except:
                continue

        errorMessage = f"Table in the data file should start at the first 10 rows."
        self.logger.error(errorMessage)
        raise EtlError(errorMessage)

    def read(self, fileName: str, zf: zipfile.ZipFile = None) -> pd.DataFrame:
        """Read a data file from a zipped folder while skipping non-data rows on top of the file.
        If a skiprows value exists, try reading the file with the existing skiprows value.
        If it failed, find the skiprows value again and read the file.

        Args:
            fileName (str): File name of the file to apply skip rows.
            zf (zipfile.ZipFile): Zipped folder where the file is.

        Returns:
            pd.DataFrame: Pandas DataFrame of the input CSV file with skipped rows.  
        """

        try:
            # Get the filename extension of the current data file
            extension = [
                extension for extension in EXTENSIONS if fileName.endswith(extension)][0]
            
            # Get the pandas method for openning data file
            if extension == 'csv':
                readFileFunc = pd.read_csv
            elif extension == 'xlsx':
                readFileFunc = pd.read_excel
            
            if self.skiprows is None:
                
                # Find skiprows value
                df, self.skiprows, headerRowID = self._auto_skiprows(fileName, zf, readFileFunc)
                df.dropna(axis='columns', how='all', inplace=True)

                # Validate header after skipping text rows
                self.validate_headers(df.iloc[headerRowID])

                # Finally, open data file with skiprows value and headers as dataframe columns
                df = readFileFunc(zf.open(fileName),
                                        skiprows=self.skiprows)
                df.drop(columns=[col for col in df.columns if col.startswith(EMPTY_COLUMN_NAME_PREFIX) and df[col].isna().all()], inplace=True)
                

            else:
                try:
                    # Try reading data file with the previously found skiprows value
                    df = readFileFunc(zf.open(fileName),
                                        skiprows=self.skiprows)
                    df.dropna(axis='columns', how='all', inplace=True)
                    self.validate_headers(df.columns)
                    df.drop(columns=[col for col in df.columns if col.startswith(EMPTY_COLUMN_NAME_PREFIX) and df[col].isna().all()], inplace=True)
                    
                except:
                    msg = f'The current file ({fileName}) probably has a different skiprows value. Rerun auto skiprows.'
                    self.logger.warn(msg)

                    # If failed, reset and find skiprows value again
                    self.skiprows = None
                    df, self.skiprows, headerRowID = self._auto_skiprows(fileName, zf, readFileFunc)
                    df.dropna(axis='columns', how='all', inplace=True)

                    # Validate that headers are strings
                    self.validate_headers(df.iloc[headerRowID])

                    # Finally, open data file with skiprows value and headers as dataframe columns
                    df = readFileFunc(zf.open(fileName),
                                            skiprows=self.skiprows)
                    df.drop(columns=[col for col in df.columns if col.startswith(EMPTY_COLUMN_NAME_PREFIX) and df[col].isna().all()], inplace=True)
        
        except Exception as e:
            self.logger.error(e)
            raise EtlError('Error in opening data file.')

        return df


def convertable_to_float(string: str) -> bool:
    """Checks if a given string can be converted to a float.

    Args:
        string (str): The input string to be checked.

    Returns:
        bool: True if the string can be converted to a float, False otherwise.
    """
    try:
        result = float(string)
        return True
    except ValueError:
        return False
    

class InputValidation:
    """A class to provide automated validation for CSV files.
    """

    def __init__(self, validTimestampHeaders: list, genericColumnHeaders: list):
        """Constructs all the necessary attributes for the InputValidation object.

        Args:
            validTimestampHeaders (list): A list of valid format for timestamp column. 
            genericColumnHeaders (list): A list of generic column header names. 
        """
        self.validTimestampHeaders = validTimestampHeaders
        self.genericColumnHeaders = genericColumnHeaders

    def _validate_timestamp_column_header(self, df: pd.DataFrame) -> bool:
        """Assuming the first column is always timestamps,
        validate auto skiprows by checking if the first header is a valid header for timestamps.

        Raises:
            EtlError: Cannot find exact match for the timestamp column header.

        Returns:
            bool: True if timestamp is in a correct format. 
        """

        logger = Logger()

        timestampHeader = df.columns[0]

        try:
            assert timestampHeader.lower() in self.validTimestampHeaders
        except AssertionError as e:
            logger.warn(
                f"Cannot find exact match for this timestamp column header: {timestampHeader}.")

            try:
                # Check if the timestamp column header of the current df is similar to any valid timestamp headers
                assert min([levenshtein_distance(timestampHeader.lower(), validTimestampHeader)
                            for validTimestampHeader in self.validTimestampHeaders]) <= TIMESTAMP_HEADER_DISTANCE
            except AssertionError:
                logger.error(
                    f"Cannot find similar match for this timestamp column header: {timestampHeader}.")
                userMessage = "Cannot find timestamp column."
                raise EtlError(userMessage)

        logger.info(
            'Verifying timestamp column header ... Timestamp header is VALID!')
        return True

    def _check_for_wide_format(self, df: pd.DataFrame, timestampColumnNames: List[str]) -> bool:
        """Method check whether input dataframe is in a wide format.

        Args:
            df (pd.DataFrame): Pandas DataFrame to apply format checking on. 
            timestampColumnNames (List[str]): Column names of all timestamp columns in the dataframe.

        Raises:
            EtlError: If the input dataframe is in a long format. 
            The exception is raised with three arguments: the error message, 
            the names and the values column IDs of the long dataframe.

        Returns:
            bool: True if input is in a wide format.
        """

        # Find timestamp column id(s)
        timestampColumnIds = [list(df.columns).index(n) for n in timestampColumnNames]

        # If there are only 3 columns in this data file
        if df.shape[1] == N_COLUMN_LONG_DATA:

            # Not a long dataframe if there is less than one column after ignoring timestamp columns
            if (N_COLUMN_LONG_DATA - len(timestampColumnNames) <= 1):
                return True

            # Loop through all columns except timestamps to find the names column
            for namesColumnId in range(N_COLUMN_LONG_DATA):

                # Ignore timestamp columns
                if df.columns[namesColumnId] in timestampColumnNames:
                    continue
                
                valuesColumnId = list(set(range(N_COLUMN_LONG_DATA)) - set(timestampColumnIds) - {namesColumnId})[0]

                # If none of the values in the current column can be converted to float
                nameColumnName = df.columns[namesColumnId]
                nameColumn = df[nameColumnName]
                if not any(nameColumn.apply(convertable_to_float)):

                    # If the average length of the strings in the current column is longer than 10
                    if nameColumn.apply(lambda x: len(x)).mean() > LENGTH_THRESHOLD:
                        
                        # Raise error when a long format dataset is detected
                        errorMessage = 'The table in this file is in a long format. ' \
                            + f'This column (column name = \"{nameColumnName}\") is detected to be a variable name column. '
                        logger.error(errorMessage)
                        raise EtlError(errorMessage, namesColumnId, valuesColumnId)

        return True

    def check_input_dataframe(self, df: pd.DataFrame, timestampColumnNames: List[str]) -> bool:
        """Validate the format of a dataframe read from a data file.

        Args:
            df (pd.DataFrame): Pandas DataFrame to validate timestamp and 
            wide format. 

        Raises:
            EtlError: If any validation failed.
            Exception: For unknown errors.

        Returns:
            bool: True if all validations are passed.
        """

        logger = Logger()

        try:
            self._validate_timestamp_column_header(df)
            self._check_for_wide_format(df, timestampColumnNames)
        except EtlError as e:
            raise EtlError(e)
        except Exception as e:
            msg = f'Unknown error: {e}'
            logger.error(msg)
            raise e

        return True

    def check_for_generic_header(self, pointName: str, dfSameName: pd.DataFrame, dfNew: pd.DataFrame) -> bool:
        """Check if the point name of a dataframe is from a generic header
        by comparing the time intervals (i.e. the modes of timestamp gaps)
        of the dataframes before and after concatenation.
        If two dataframes of the same point have the same time interval,
        the concatenation of the two should have the same time interval
        as before. Concatenating two dataframes of two points with the same header
        will result in a drop in time interval.

        Args:
            pointName (str): Point name to verify whether it is a generic header.
            dfSameName (pd.DataFrame): Pandas Dataframe in a long format containing values that have the same 
                column header in the original data file as dfNew.
            dfNew (pd.DataFrame): Pandas Dataframe in a long format containing values that have the same 
                column header in the original data file as dfSameName.

        Raises:
            EtlError: If the point name is considered generic.

        Returns:
            bool: False if the point name is not considered generic.
        """

        logger = Logger()

        try:
            # Check if this is a generic column header we have seen before
            assert pointName.lower(
            ) not in self.genericColumnHeaders, f'Generic column name found: "{pointName}".'

            # Check if this could be a generic column header we haven't seen before
            if len(pointName) <= LENGTH_THRESHOLD:

                msg = f'This point name has a length less than 10, which is possibly not a valid point name: "{pointName}"'
                logger.warn(msg)

                # If values are recorded in a similar behaviour in terms of time interval
                oldTimeInterval = calculate_time_interval(dfSameName[TIME])
                newTimeInterval = calculate_time_interval(dfNew[TIME])
                if oldTimeInterval == newTimeInterval:

                    # Concatenate the two dataframes with the same point name
                    dfConcat = pd.concat([dfSameName, dfNew],
                                        axis=0, ignore_index=True)
                    dfConcat.drop_duplicates(inplace=True, ignore_index=True)

                    # Check for a drop in time interval
                    timeIntervalAfterConcat = calculate_time_interval(
                        dfConcat[TIME])
                    if timeIntervalAfterConcat < oldTimeInterval:
                        msg = f'It\'s likely that there are two different points sharing the same column header: "{pointName}".'
                        logger.error(
                            f"{msg} because the time interval dropped after concatenating two dataframes.")
                        raise EtlError(msg)
            
            return False

        except (AssertionError, EtlError) as e:
            raise EtlError(str(e))


def calculate_time_interval(dtSeries: pd.Series) -> str:
    """Calculate the time interval of a datetime series.

    Args:
        dtSeries (pandas.Series): A pandas series of datetime objects.

    Returns:
        str: A string representing the time interval in minutes, or an empty string
            when there are less than 2 valid datetime objects.
    """

    # Cannot calculate time interval when there are less than 2 non-NA datetimes; return empty string
    if (~dtSeries.isna()).sum() < 2:
        return ''

    else:
        dtSeriesSorted = dtSeries.sort_values(
            ascending=True, ignore_index=True)
        return str(int(dtSeriesSorted.diff().mode()[0].total_seconds()/60))


def find_timestamp_columns(df:pd.DataFrame) -> Tuple[List[str], bool]:
    """
    Finds the columns in a pandas DataFrame that represent timestamps
    (including unix timestamps).

    The function iterates over the values in the first row of the DataFrame and attempts to
    convert each value to a timestamp using the `pd.to_datetime` function. Any value that can
    be successfully converted to a timestamp is considered a timestamp column.

    Args:
        df (pd.DataFrame): The DataFrame to search for the timestamp column.

    Returns:
        List[str]: A list of column names representing the detected timestamp columns.
        bool: True if the timestamp columns are unix timestamps; False, otherwise.
    
    Raises:
        EtlError: If no timestamp column is found in the DataFrame.
    """

    logger = Logger()

    isUnixTimestamp = False

    firstRowInStrings = df.iloc[0].astype(str)
    timestampColumnNames = []
    for index, possibleTimestamp in firstRowInStrings.items():
        try:
            # FIXME: AEST and AEDT tz names raise error in pandas 2.0, fix them after error removed in pandas
            possibleTimestamp = possibleTimestamp.replace("AEST", "AET").replace("AEDT", "AET")
            # Raise exception if possibleTimestamp is not in any timestamp format
            # or is a string of numbers (unix timestamps)
            pd.to_datetime(possibleTimestamp)

            # Store the column name if to_datetime passes
            timestampColumnNames.append(index)
            logger.info(f'This is a timestamp column. Column name = "{index}". Tested value = {possibleTimestamp}')
        except:
            logger.info(f'This is not a timestamp column. Column name = "{index}". Tested value = {possibleTimestamp}')

    if timestampColumnNames:
        return timestampColumnNames, isUnixTimestamp

    else:
        
        # Find unix timestamp column
        isUnixTimestamp = True

        firstRow = df.iloc[0]
        for index, possibleTimestamp in firstRow.items():
            try:
                # Raise exception if possibleTimestamp is not within the eligible range
                # of unix timestamps or cannot be converted to a datetime object
                assert (float(possibleTimestamp) >= 315532800) and (float(possibleTimestamp) <= 2524608000)
                pd.to_datetime(possibleTimestamp, unit='s')

                # Store the column name if checks are passed
                timestampColumnNames.append(index)
                logger.info(f'This is a timestamp column. Column name = "{index}". Tested value = {possibleTimestamp}')

            except:
                logger.info(f'This is not a timestamp column. Column name = "{index}". Tested value = {possibleTimestamp}')

        if timestampColumnNames:
            return timestampColumnNames, isUnixTimestamp
        else:
            errorMessage = "Cannot find any timestamp column."
            logger.error(errorMessage)
            raise EtlError(errorMessage)


class DatetimeParser():
    """A class to parse a Panda Series of timestamp strings. 
    """

    # Define class attributes

    # Regex bricks
    bricks = re.compile(r"""
                (?(DEFINE)
                    (?P<year_def>[12]\d{3}) # 1 or 2 then followed by 3 digits
                    # (?P<year_short_def>\d{2})  
                    (?P<month_def>January|February|March|April|May|June|
                    July|August|September|October|November|December)
                    (?P<month_short_def>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)
                    (?P<month_dec_def>(0?[1-9]|1[012]))  # 01, 1, 12 but not 13
                    (?P<day_def>(?:0[1-9]|[1-9]|[12][0-9]|3[01]))
                    (?P<weekday_def>(?:Mon|Tue|Wednes|Thurs|Fri|Satur|Sun)day)
                    (?P<weekday_short_def>Mon|Tue|Wed|Thu|Fri|Sat|Sun)
                    (?P<hms_def>T?\d{1,2}:\d{2}:\d{2}) # 03:20:10 or 3:20:10
                    (?P<hmsf_def>T?\d{1,2}:\d{2}:\d{2}.\d{1,6})
                    (?P<hm_def>T?\d{1,2}:\d{2})  # T13:20 or 13:20
                    (?P<delim_def>([-/, ]+|(?<=\d|^)T))
                    (?P<ampm_def>am|pm|AM|PM)
                    (?P<timezone_def>[+-]\d{4}) # +HHMM or -HHMM
                    # TODO: complie time zone format +HH:MM and -HH:MM, e.g. -08:00
                    (?P<timezone_name_def>ACDT|ACST|ACT|ADT|AEDT|AEST|AFT|AKDT|AKST|
                    ALMT|AMST|AMT|ANAST|ANAT|AQTT|ART|AST|AT|AWDT|AWST|AZOST|AZOT|AZT|
                    AoE|BNT|BOT|BRST|BRT|BST|BTT|CAT|CCT|CDT|CEST|CET|CHADT|CHAST|CHOT|
                    CHOST|CHST|CHUT|CIDST|CIST|CKT|CLST|CLT|COT|CST|CT|CVT|CWST|CXT|DAVT|
                    DDUT|DFT|EASST|EAST|EAT|ECT|EDT|EEST|EET|EGST|EGT|EST|ET|FET|FJST|
                    FJT|FKST|FKT|FNT|GALT|GAMT|GET|GFT|GILT|GMT|GST|GYT|HDT|HAEC|HST|HKT|
                    HMT|HOVT|HST|ICT|IDT|IOT|IRDT|IRKST|IRKT|IRST|IST|JST|KALT|KGT|KOST|
                    KRAT|KST|KUYT|LHST|LHST|LINT|MAGST|MAGT|MART|MAWT|MDT|MEST|MET|MHT|
                    MIST|MIT|MMT|MSK|MST|MUT|MVT|MYT|NCT|NDT|NFT|NOVT|NPT|NST|NT|NUT|
                    NZDT|NZST|OMSST|OMST|ORAT|PDT|PET|PETST|PETT|PGT|PHOT|PHT|PKT|PMDT|
                    PMST|PONT|PST|PT|PWT|PYST|PYT|RET|ROTT|SAKT|SAMT|SAST|SBT|SCT|SDT|SGT|
                    SLST|SRET|SRT|SST|SYOT|TAHT|TFT|TJT|TKT|TLT|TMT|TRT|TOT|TVT|ULAST|ULAT|
                    UTC|UYST|UYT|UZT|VET|VLAST|VLAT|VOST|VUT|WAKT|WARST|WAST|WAT|WEST|WET|
                    WFT|WGST|WGT|WIB|WIT|WITA|WST|WT|YAKST|YAKT|YAPT|YEKST|YEKT
                    )
                )

                (?P<hmsf>^(?&hmsf_def)$)|(?P<hms>^(?&hms_def)$)|(?P<hm>^(?&hm_def)$)|(?P<year>^(?&year_def)$)|(?P<month>^(?&month_def)$)|
                (?P<month_short>^(?&month_short_def)$)|(?P<month_dec>^(?&month_dec_def)$)|(?P<day>^(?&day_def)$)|
                (?P<weekday>^(?&weekday_def)$)|(?P<weekday_short>^(?&weekday_short_def)$)|(?P<delim>^(?&delim_def)$)|
                (?P<ampm>^(?&ampm_def)$)|(?P<timezone>^(?&timezone_def)$)|(?P<timezone_name>^(?&timezone_name_def)$)
                #|(?P<year_short>^(?&year_short_def)$)|(?P<ms>^(?&ms_def)$)
                """, re.VERBOSE)
        
    # Delimiters used in timestamps
    delim = re.compile(r'([-/, ]+|(?<=\d)T)')

    # Format codes
    formats = {'year': '%Y', 'year_short': '%y', 'month': '%B', 'month_dec': '%m', 'day': '%d', 'weekday': '%A',
                    'hms': '%H:%M:%S', 'hmsf': '%H:%M:%S.%f',
                    'hms_12': '%I:%M:%S', 'hmsf_12': '%I:%M:%S.%f',
                    'hm_12': '%I:%M',
                    'weekday_short': '%a', 'month_short': '%b', 'hm': '%H:%M', 'delim': '',
                    'ampm': '%p', 'timezone': '%z', 'timezone_name': '%Z'}

    def __init__(self, nTests=100):
        """Constructs all the necessary attributes for the DatetimeParser object.

        Args:
            nTests (int, optional): The number of timestamp strings used to find the year position. Defaults to 100.
        """
        self.logger = Logger()
        self.positionYear = None
        self.positionDay = None
        self.isShortYear = False  # Whether 2-digit year is used
        self.nTests = nTests
        self.containsTimeZone = False
        self.dtFinalFormat = None
    
    def _reset_instance_attributes(self):
        self.positionYear = None
        self.positionDay = None
        self.isShortYear = False
        self.containsTimeZone = False
        self.dtFinalFormat = None

    def _find_short_year_position(self, dtSeries: pd.Series) -> None:
        """ 
        Find the position of year with or without century 
        based on a series of timestamps. 

        Args:
            dtSeries (pd.Series): Pandas Series containing timestamp strings.

        Returns:
            None
        """

        # SELECT self.nTests timestamps from dtSeries as test cases
        if len(dtSeries) > self.nTests:
            dtTests = dtSeries.sample(n=self.nTests, replace=False)
        else:
            dtTests = dtSeries.copy(deep=True)

        # PARSE the selected timestamps with a magic datetime parser
        dtObjectsTests = dtTests.apply(lambda x: dateparser.parse(str(x)))

        # CONCATENATE the output datetime objects and the original datetime strings into a DataFrame
        dtDf = pd.DataFrame(
            {'Dt Strings': dtTests.astype(str), 'Dt Objects': dtObjectsTests})

        # CREATE a list, positionsShortYears to store positions of short years
        positionsYears = []

        # FOR each datetime object
        for idx in dtDf.index:
            # FIXME: catch None and return errors
            if dtDf.loc[idx]["Dt Objects"] is None:
                self.logger.warn(
                    f"Returned object for {dtDf.loc[idx]['Dt Strings']} is {dtDf.loc[idx]['Dt Objects']}.")
                continue

            # GET its year
            year = str(dtDf.loc[idx]["Dt Objects"].year)

            # SET the last two digits of year as shortYear
            shortYear = str(year)[-2:]

            # SPLIT the corresponding datetime string into chunks of strings by delimiters into a list
            dtString = dtDf.loc[idx]['Dt Strings']
            dateParts = self.delim.split(dtString)

            # GET the positions of year in dateParts
            positions = [i for i, x in enumerate(dateParts) if x == year]

            # If year is not found
            if not positions:

                # GET the position of shortYear in dateParts
                positions = [i for i, x in enumerate(
                    dateParts) if x == shortYear]

                if not positions:
                    errorMessage = f"Can't find year position in the current timestamp = {dtString}, neither 4-digit year or 2-digit year."
                    self.logger.warn(errorMessage)

                else:
                    self.isShortYear = True

            # STORE the position to list positionsShortYears
            positionsYears += positions

        # TODO: Check the number of year positions found

        # GET the most common position of short year
        if positionsYears:
            countPositionsYears = Counter(positionsYears)
            self.positionYear = sorted(countPositionsYears.items(),
                                       key=lambda item: item[1], reverse=True)[0][0]
        else:
            errorMessage = f"Cannot find the position of year in timestamps."
            self.logger.error(errorMessage)
            raise EtlError(errorMessage)

        return

    def _find_month_wording(self, datestring: str) -> list:
        """Find any month name or abbreviation in date string 
        and return them as a list of names.

        Args:
            datestring (str): Input datetime string to identify month wording.

        Returns:
            list: Identified list of month wording (could be empty).
        """
        month_names = r"January|February|March|April|May|June|July|August|September|October|November|December"
        month_abbrs = r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"

        pattern = rf"\b(?:{month_names}|{month_abbrs})\b"
        matches = re.findall(pattern, datestring, re.IGNORECASE)

        return matches


    def _find_day_position(self, dtSeries: pd.Series) -> int:
        """Find 50 timestamps with day > 12 as test cases and
        find the position of day.

        Args:
            dtSeries (pd.Series): Panda Series containing timestamp strings

        Returns:
            int: Position of Day in timestamp
        """
        # CREATE a list, positionsShortYears to store positions of day
        positionsDays = []

        # FIXME: when we can't day >= 12, get the max value of; make it fail if max <= 12!!
        nRuns = 0  # Count the times running the while loop
        maxRuns = len(dtSeries)

        while len(positionsDays) < 50 and nRuns < 200:
            nRuns += 1

            # SELECT 1 timestamp from dtSeries as test case randomly
            dtTest = dtSeries.sample().values[0]

            # PARSE the selected timestamp with a magic datetime parser
            # dtObjectTest = parser.parse(dtTest)
            dtObjectTest = dateparser.parse(str(dtTest))

            day = dtObjectTest.day

            # Don't use timestamps with day <= 12 and no month wording found
            if day <= 12 and not self._find_month_wording(dtTest):
                continue
            else:
                day = str(day)

            # SPLIT the corresponding datetime string into chunks of strings by delimiters into a list
            dateParts = self.delim.split(str(dtTest))

            # GET the position of day in the list
            positions = [i for i, x in enumerate(dateParts) if x == day]

            # STORE the position to list positionsDays
            positionsDays += positions

        # GET the most common position of year
        if positionsDays:
            countPositionsDays = Counter(positionsDays)
            self.positionDay = sorted(countPositionsDays.items(),
                                      key=lambda item: item[1], reverse=True)[0][0]
        else:
            self.logger.warn(
                f"Not enough timestamps to tell where the position of day is. Setting it to DEFAULT_POSITION_DAY = {DEFAULT_POSITION_DAY}")
            self.positionDay = DEFAULT_POSITION_DAY

        return self.positionDay

    def _correct_format_code_for_AMPM(self, formatCodeList) -> list:
        """
        Correct and replace format code %H with %I if AM/PM is in timestamps.
        """

        if self.formats['ampm'] in formatCodeList:
            # REPLACE %H with %I if %p in format
            try:
                formatCodeList[formatCodeList.index(
                    self.formats['hms'])] = self.formats['hms_12']
            except ValueError:
                try:
                    formatCodeList[formatCodeList.index(
                        self.formats['hm'])] = self.formats['hm_12']
                except ValueError:
                    try:
                        formatCodeList[formatCodeList.index(
                            self.formats['hmsf'])] = self.formats['hmsf_12']
                    except ValueError:
                        errorMessage = 'AM/PM in timestamp but cannot find time!'
                        self.logger.error(errorMessage)
                        userMessage = 'Cannot find time in timestamps.'
                        raise EtlError(userMessage)

        return formatCodeList

    def _guess_one_format(self, datestring: str) -> str:
        """ Guess and return the timestamp format for a timestamp string. 

        Args:
            datestring (str): Input datetime string to identify format.

        Returns:
            str: Identified format of the input datestring.
        """

        # Break timestamp string into parts
        parts = self.delim.split(str(datestring))

        out = []

        # Iterate over the parts and try to match them to a known date brick
        for index, part in enumerate(parts):

            # IF index is equal to positionYear THEN
            if index == self.positionYear:

                # IF short year is in the datestring
                if self.isShortYear:

                    # APPEND the format code of short year to out
                    out.append(self.formats['year_short'])

                # IF long year is in the datestring THEN
                else:

                    # APPEND the format code of long year to out
                    out.append(self.formats['year'])

            # ELSE IF index is equal to positionDay THEN
            elif index == self.positionDay:

                # APPEND the format code of day to out
                out.append(self.formats['day'])

            else:

                # ELSE search for regex brick for the current timestamp part

                # Use the bricks regex to search for a brick in the part
                try:
                    brick = dict(
                        filter(lambda x: x[1] is not None, self.bricks.match(part).groupdict().items()))

                    # Get the key for the first brick found in the part; FIXME: GET all the matching bricks instead, e.g. %m & %d
                    key = next(iter(brick))

                    item = part if key == 'delim' else self.formats[key]

                    # Append the format code for the current timestamp part to output
                    out.append(item)

                except AttributeError:
                    errorMessage = f"Can't find a time part regex brick that matches with {part}"
                    self.logger.error(errorMessage)
                    raise EtlError('Cannot recognise date parts.')

        out = self._correct_format_code_for_AMPM(out)

        # Check and filter out time zone from datetime format code
        out = self._check_and_remove_time_zone(parts, out)

        return "".join(out).strip()

    def _find_final_format(self, dtSeries: pd.Series) -> str:
        """Get the format for the whole timestamp series. 

        Args:
            dtSeries (pd.Series): Pandas Series containing timestamp strings.

        Raises:
            EtlError: Unable to find datetime format.

        Returns:
            str: Most common time format as a string.
        """

        # FIND the most common format
        # FIND the positions of year and day
        try:
            self._find_short_year_position(dtSeries)
            self._find_day_position(dtSeries)

            # SELECT self.nTests timestamps randomly as tests to find the format
            dtTests = dtSeries.sample(n=self.nTests, replace=True)
            dtFormats = dtTests.apply(lambda x: self._guess_one_format(x))

            countPossibleFormats = Counter(dtFormats)

            # SAVE the most common format
            self.dtFinalFormat = sorted(countPossibleFormats.items(),
                                        key=lambda item: item[1], reverse=True)[0][0]
            self.logger.info(
                f'Datetime format found: {self.dtFinalFormat}')
            
        except EtlError as e:
            self.logger.error(e)
            raise EtlError(f'Unable to find datetime format. {str(e)}')
        except Exception as e:
            self.logger.error(e)
            raise e

        # RETURN the most common format as a string
        return self.dtFinalFormat

    def _check_and_remove_time_zone(self, dateParts: list, out: str) -> str:
        """Check if time zones exist in timestamps. 

        Args:
            dateParts (list): List of date parts.
            out (str): Datetime format code. 

        Returns:
            str: Datetime format code without time zones.
        """

        # Try removing format code for time zones
        try:
            out.remove(self.formats['timezone'])
            self.containsTimeZone = True

        except ValueError:
            try:
                out.remove(self.formats['timezone_name'])
                self.containsTimeZone = True

            except:

                # Try another way to check if time zones exist
                if (len(dateParts[-1]) >= 3 and dateParts[-1].isalpha()):
                    self.containsTimeZone = True
                    self.logger.warn(
                        f'Possible time zone exists but not aligned with the format of %Z or %z: {dateParts}. The containsTimeZone flag set as True')

        return out

    def parse(self, dtSeries: pd.Series, isUnixTimestamp: bool) -> pd.Series:
        """Parse input datetime string.

        Args:
            dtSeries (pd.Series): Pandas Seires of Datetime string to apply parsing.
            isUnixTimestamp (bool): True if the timestamps in the input series are unix timestamps.

        Raises:
            EtlError: Failed datetime parsing.
            Exception: For unknown errors.

        Returns:
            pd.Series: Panda Series of parsed datetime objects.
        """

        self.logger.info(
            f'Showing the first and the last 2 of the timestamps BEFORE parsing: \n{pd.concat([dtSeries.head(2), dtSeries.tail(2)])}')

        # PARSE unix timestamps automatically without finding timestamp format
        if isUnixTimestamp:
            try:
                # Convert unix timestamps need numeric type
                if dtSeries.dtype == "O":
                    dtSeries = dtSeries.astype(int)
                dtObjects = pd.to_datetime(dtSeries, unit='s')
            except Exception as e:
                errorMessage = f'Parsing unix timestamps failed: {e}'
                self.logger.error(errorMessage)
                raise EtlError(f'Parsing timestamps failed.')
            else:
                self.logger.info(f'Showing the first and the last 2 of the timestamps AFTER parsing: \n{pd.concat([dtObjects.head(2), dtObjects.tail(2)])}')
                return dtObjects
            
        # FIND the timestamp format
        if self.dtFinalFormat is None:
            self._find_final_format(dtSeries)
        else:
            self.logger.info(
                f'Datetime format has been found before: {self.dtFinalFormat}')

        # PARSE the whole timestamp series using the format found by self._find_final_format()
        try:
            # Try exact match to test the algo
            dtObjects = pd.to_datetime(
                dtSeries, format=self.dtFinalFormat, exact=(not self.containsTimeZone))

        except Exception as e:
            self.logger.warn(f'Parsing failed: {e}')
            try:
                self.logger.warn('Redo finding format ...')

                # Reset variables
                self._reset_instance_attributes()

                # Retry finding datetime format
                self._find_final_format(dtSeries)
                dtObjects = pd.to_datetime(
                    dtSeries, format=self.dtFinalFormat, exact=(not self.containsTimeZone))
                self.logger.info('Second Parsing done')
            except EtlError as e:
                errorMessage = f'Second parsing failed: {e}'
                self.logger.error(errorMessage)
                raise EtlError(f'Parsing timestamps failed. {str(e)}')
            except Exception as e:
                self.logger.error(e)
                raise e

        # TODO: Check that the numbers of NaN in dtSeries and dtObjects are the same

        if self.containsTimeZone:
            self.logger.warn('Timestamps contain time zones!')

        # RETURN a pd.Series of datetime objects
        self.logger.info(
            f'Showing the first and the last 2 of the timestamps AFTER parsing: \n{pd.concat([dtObjects.head(2), dtObjects.tail(2)])}')

        return dtObjects


def transform_columns_to_long_dataframes(wideDf: pd.DataFrame, filesWithNanColumn: set, fileName: str, timestampColumnName: str) -> Tuple[dict, set]:
    """Transform each column in the input dataframe to a new dataframe in long format.

    Args:
        wideDf (pd.DataFrame): Pandas Dataframe of a dataset with wide format.
        filesWithNanColumn (set): Set of files with NaN column.
        fileName (str): Absolute file path of dataset to be processed.
        timestampColumnName (str): Column name of timestamp column.

    Raises:
        EtlError: If duplicate column headers are found in a single data file and for unknown errors.

    Returns:
        Tuple[dict, set]: Dictionary of the new dataframe(s) and a set of files with NaN column.
    """
    
    logger = Logger()

    try:
        dfDictFile = {}

        # Loop through all columns (point values) except the timestamp column
        for point in wideDf.columns:
            if point == timestampColumnName:
                continue

            # Get all non-na values for selected column as temp dataframe
            tempDf = wideDf[wideDf[point].notna()][[TIME, point]].rename(
                columns={point: VALUE})

            # Log the file name if the whole column is NaN
            if not wideDf[point].notna().any():
                filesWithNanColumn.add(fileName)

            # Rename and reorder to fit raw data format
            tempDf[NAME] = point  # point for every row
            tempDf = tempDf[LOG_HEADER]  # Reorder the columns

            tempDf.sort_values(TIME, inplace=True, ignore_index=True)

            assert point not in dfDictFile.keys(), f'Duplicate column header in a single data file.'
            dfDictFile[point] = tempDf

    except AssertionError as e:
        logger.error(e)
        raise EtlError(str(e))

    except Exception as e:
        logger.error(e)
        raise EtlError('Failed to preprocess columns.')

    return dfDictFile, filesWithNanColumn


def get_point_summary(point: str, df: pd.DataFrame) -> pd.DataFrame:
    """Generate summary statistics of a point based on its trend log.

    Args:
        point (str): Point name of the data.
        df (pd.DataFrame): Trend log of the point.

    Returns:
        pd.DataFrame: Summary statistics of the given trend log.
    """

    logger = Logger()

    try:

        # Reformat and transform data
        dfNew = df.rename(columns={'datapoint': point})
        dfNew[point] = pd.to_numeric(dfNew[point], errors='coerce')

        # Calculate statistics
        df_summary = dfNew[[point]].describe()
        # df_summary.loc['count'] = df[point].gt(0).sum()
        df_summary = df_summary.transpose().round(3)

        # Drop columns that are not in SUMMARY_COLUMNS
        df_summary = df_summary[df_summary.columns.intersection(
            SUMMARY_COLUMNS)]

        # Replace pd.NaN with empty string
        df_summary.fillna(value="", inplace=True)

    except Exception as e:
        df_summary = pd.DataFrame(
            data={j: "" for j in SUMMARY_COLUMNS}, index=[point])
        msg = f"Exception occurred: {e}. Added empty strings as summary statistics instead."
        logger.warn(msg)

    return df_summary


def get_statistical_summary(dfDict: dict) -> pd.DataFrame:
    """Generate a summary statistics table for the dataframe(s) in the input dictionary.

    Args:
        dfDict (dict): Dictionary of dataframe(s).

    Raises:
        Exception: For unknown errors.

    Returns:
        pd.DataFrame: A summary statistics table.
    """

    logger = Logger()

    try:
        summaryList = []
        for point, df in dfDict.items():
            pointSummary = get_point_summary(point, df)
            summaryList.append(pointSummary)

        statSummaryDf = pd.concat(summaryList)

        # Replace pd.NaN with empty string
        statSummaryDf.fillna(value="", inplace=True)

    except Exception as e:
        msg = f'Unknown error: {e}'
        logger.error(msg)
        raise Exception(msg)

    return statSummaryDf


def merge_long_dataframes(dfList: list, freq: int) -> pd.DataFrame:
    """Merge a list of long dataframes to wide format after rounding timestamp for a given time interval

    Args:
        dfList (list): A list of pandas DataFrames containing the trend log. (length upto 100)
        freq (int): Value of given time interval.

    Returns:
        pd.DataFrame: A wide format pandas DataFrame.
    """
    # Error out if one of dataframe in the list is not a valid long format
    for tmpDf in dfList:
        if len(tmpDf.columns) != 3:
            raise ValueError(
                f'Invalid header length of {len(tmpDf)} in input dataframe')

    # Concat all dataframes in list and rename columns
    df = pd.concat(dfList, ignore_index=True, copy=False)
    df.columns = [TIMESTAMP, 'Description', 'Value']

    # Round timestamp for given time interval
    df[TIMESTAMP] = pd.to_datetime(
        df[TIMESTAMP], format='%d/%m/%Y %H:%M')
    df[TIMESTAMP] = df[TIMESTAMP].dt.round(f'{freq}min')

    # Get time difference before/after every row
    interval = int(freq)
    timeDiff1 = (df[TIMESTAMP] - df[TIMESTAMP].shift(1)).dt.seconds/60 # row_n - row_n-1
    timeDiff1[df['Description'] != df['Description'].shift(1)] = np.nan
    timeDiff2 = (df[TIMESTAMP].shift(-1) - df[TIMESTAMP]).dt.seconds/60 # row_n+1 - row_n
    timeDiff2[df['Description'].shift(-1) != df['Description']] = np.nan

    # Identify gap type 1: two identical rounded timestamp after gap
    # Identify gap type 2: two identical rounded timestamp before gap
    timeGap1 = (timeDiff1 == 2*interval) & (timeDiff2 == 0)
    timeGap2 = (timeDiff1 == 0 )& (timeDiff2 == 2*interval)

    # move timestamp before/after one interval
    df.loc[timeGap1,TIMESTAMP] = df[timeGap1][TIMESTAMP] - pd.Timedelta(minutes=interval)
    df.loc[timeGap2,TIMESTAMP] = df[timeGap2][TIMESTAMP] + pd.Timedelta(minutes=interval)

    # Sort data by timestamp and ignore non-numeric data
    df.sort_values(TIMESTAMP, inplace=True)
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

    # Make log data into wide format (pivot table)
    df = pd.pivot_table(df, index=TIMESTAMP,
                        columns='Description', values='Value')
    df.reset_index(inplace=True)

    return df


def merge_wide_dataframes(dfList: list) -> pd.DataFrame:
    """Merge a list of wide dataframes to a big final merged dataframe
    Args:
        dfList (list): A list of wide dataframes needed to be merged.

    Returns:
        pd.DataFrame: A wide format pandas DataFrame.
    """
    # Error out if Timestamp is not in header of any dataframe in the list
    for tmpDf in dfList:
        if TIMESTAMP not in tmpDf.columns:
            raise ValueError(
                f'Could not find Timestamp columns in dataframe, first column named as {tmpDf.columns[0]}')

    # Iterate merge process
    df = reduce(lambda df1, df2: pd.merge(
        df1, df2, on=TIMESTAMP, how='outer'), dfList)

    # Sort columns alphabetically and sort rows by timestamp
    df = df[[TIMESTAMP]+sorted(df.columns[1:])]
    df.sort_values(TIMESTAMP, ignore_index=True, inplace=True)

    return df


def save_file_to_portal(api: exergenics.ExergenicsApi, filePath: str, jobId: Union[int, str],  nodeName: str, removeFile: bool = True) -> str:
    """Upload a local file to s3 and save it to jobData in Exergenics portal.

    Args:
        api (exergenics.ExergenicsApi): Exergenics Api object
        filePath (str): A local path for file needed to be uploaded
        jobId (int): The Id of selected job
        nodeName (str): The name of node in jobData
        removeFile (bool, optional): Remove local file after uploading or not. Defaults to True.

    Raises:
        EtlError: If no file exist in input file path.
    Returns:
        str: url for file uploaded
    """

    logger = Logger()

    # Error out if no file exist in input file path
    if not os.path.isfile(filePath):

        logger.error(f'No file existing in local path: {filePath}.')
        raise EtlError(f'No file existing in local path.')

    url2s3 = api.sendToBucket(filePath)
    if removeFile is True:
        os.remove(filePath)
    api.setJobData(jobId, nodeName, url2s3)
    return url2s3


def get_building_data(bCode: str, pCode: str, api: exergenics.ExergenicsApi) -> dict:
    """Get building data for selected building and plant from Exergenics portal

    Args:
        bCode (str): The building code associated to building data.
        pCode (str): The plant code associated to building data.
        api (exergenics.ExergenicsApi): Exergenics Api object.

    Raises:
        ValueError: If failed to get building data.
        ValueError: If no building data found.

    Returns:
        dict: A dictionary of building data.
    """

    logger = Logger()

    try:
        buildingData = None
        if api.getBuildings(bCode):
            while api.moreResults():
                building = api.nextResult()
                for plantData in building['buildingPlants']:
                    if plantData['plantCode'] == pCode:
                        buildingData = plantData
    except Exception as e:
        raise ValueError(
            f"Fail to get buildingData from jobData for {str(e)}.")

    # Validate result
    if buildingData is None:
        message = "buildingData not exist in jobData."
        logger.error(message)
        raise ValueError(message)

    return buildingData

def get_equipment_quantities(equipData: dict) -> dict:
    """Get equipment quantities dictionary of equip data

    Args:
        equipData (dict): The equipment data associated with equipments

    Returns:
        dict: A dictionary of all equipment types and their quantities
    """

    logger = Logger()
    
    try:
        equipQtyDict = {}
        for equipType in EQUIP_TYPE_LIST:

            # Get number of each equipment type, assign 0 if failed to find
            if equipType in equipData.keys():
                tmpEquipNum = len(equipData[equipType])
            else:
                tmpEquipNum = 0
                
            equipQtyDict[equipType] = tmpEquipNum

    except Exception as e:
        logger.error(f'Failed to get quantity dict from building data: {e}')
        raise ValueError(e)
    
    return equipQtyDict


def get_hidden_equip(buildingData: dict) -> list:
    """Get all hidden equipment names for building data from Exergenics portal

    Args:
        buildingData (dict): The building data associated with hidden equipments

    Returns:
        list: A list of hidden equipment names
    """

    logger = Logger()

    try:
        hiddenEquipList = []
        for group in buildingData['plantGroups']:
            if group['groupCategory'] == 'hidden':
                for equip in group['attachedEquipment']:
                    equipName = equip.split('.')[-1]
                    hiddenEquipList.append(equipName)
    except Exception as e:
        logger.error(e)
        hiddenEquipList = []

    logger.info(f'Get hidden equip list: {hiddenEquipList}')

    return hiddenEquipList


def get_active_and_hidden_equipments(buildingData: dict) -> Tuple[dict, dict]:
    """Get active equipment dictionary and hidden equipment list from building data.

    Args:
        buildingData (dict): The building data associated with active and hidden equipments

    Returns:
        dict: A dictionary of active equipments and a list of hidden equipments
    """

    logger = Logger()
    
    try:
        # Get all hidden equipments
        hiddenEquipList = get_hidden_equip(buildingData)
        equipData = buildingData['plantEquipment']

        # Getactive equip dict
        activeEquipDict = {}
        for equipType in EQUIP_TYPE_LIST:
            tmpActiveList = []
            if equipType in equipData.keys():
                for tmpEquipData in equipData[equipType]:
                    equipCode = tmpEquipData['equipmentCode'].split(
                        '.')[-1]
                    if equipCode not in hiddenEquipList:
                        tmpActiveList.append(int(equipCode.split('-')[-1]))
            activeEquipDict[equipType] = tmpActiveList

    except Exception as e:
        logger.error(f'Failed to get hidden and active equipments from building data: {e}')
        raise ValueError(e)

    return activeEquipDict, hiddenEquipList


def get_equipment_metadata(equipData: dict) -> dict:
    """Get a dictionary with all equipments and their metadata

    Args:
        equipData (dict): The equipment data associated with equipments

    Returns:
        dict: A dictionary of all equipments and their metadata
    """

    logger = Logger()
    
    try:
        equipDict = {}
        for equipType in EQUIP_TYPE_LIST:
            logger.info(f'Get {equipType} attributes from buildingData.')
            equipDict[equipType] = {}
            if equipType in equipData.keys():
                for tmpEquipData in equipData[equipType]:
                    equipCode = tmpEquipData['equipmentCode'].split(
                        '.')[-1]
                    num = int(equipCode.split('-')[-1])
                    equipDict[equipType][num] = {v['field']: v['value'] for v in tmpEquipData['equipmentVariables']}
                    
    except Exception as e:
        logger.error(f'Failed to get plant dict from equip data: {e}')
        raise ValueError(e)

    return equipDict


def get_headers(buildingData: dict) -> dict:
    """Get a dictionary of header id and its associated chillers and cooling tower numbers from building data

    Args:
        buildingData (dict): The building data associated with headers

    Raises:
        ValueError: Header number in equipment is not the same as header group number
        ValueError: Failed to get header data

    Returns:
        dict: A dictionary of header id and its associated chillers and cooling tower numbers
    """

    logger = Logger()
    
    try:
        equipData = buildingData['plantEquipment']
        if HEADER_TYPE in equipData.keys():
            headerEquipNum = len(equipData[HEADER_TYPE])
        else:
            headerEquipNum = 0

        try:
            headerGroupNum = len([g for g in buildingData['plantGroups'] if g['groupCategory'] == 'plant-header' and g['attachedEquipment'] != []])
        except:
            headerGroupNum = 0

        # Check number of header equips/groups are the same
        defaultHeaderCase = headerEquipNum == 1 and headerGroupNum == 0
        if not defaultHeaderCase and headerEquipNum != headerGroupNum:
            msg = f'Number of headers ({headerEquipNum}) does not match number of header groups ({headerGroupNum}), please check your plant configuration.'
            logger.error(msg)
            raise ValueError(msg)
        else:
            headerNum = headerEquipNum


        if headerNum == 0:
            headerDict = {}
            logger.warn('Assign empty header data.')
        elif headerNum == 1:
            if 'cooling-tower' in equipData.keys():
                headerDict = {'singleheader': {'chiller': [j for j in range(
                    1, len(equipData[CH_TYPE])+1)], 'cooling-tower': [j for j in range(1, len(equipData[CT_TYPE])+1)]}}
                logger.info('Get single header data for all chs and cts.')
            else:
                headerDict = {'singleheader': {'chiller': [j for j in range(
                    1, len(equipData[CH_TYPE])+1)], 'cooling-tower': []}}
                logger.info('Get single header data for all chs.')
        else:
            headerDict = {}
            for j in buildingData['plantGroups']:
                if j['groupCategory'] == 'plant-header':
                    headerDict[j['groupId']] = [
                        k.split('.')[-1] for k in j['attachedEquipment']]

            for key, value in headerDict.items():
                tmpHeaderDict = {'chiller': [], 'cooling-tower': []}
                for equip in value:
                    equipName = '-'.join(equip.split('-')[:-1])
                    equipNum = int(equip.split('-')[-1])
                    if equipName in tmpHeaderDict.keys():
                        tmpHeaderDict[equipName].append(equipNum)
                    else:
                        tmpHeaderDict[equipName] = [equipNum]
                headerDict[key] = tmpHeaderDict
            logger.info('Get multiple headers data')
                    
    except Exception as e:
        logger.error(f'Failed to get header dict from building data: {e}')
        raise ValueError(e)

    return headerDict


def get_renamed_and_unnamed_columns(headerDf: pd.DataFrame) -> Tuple[list, list]:
    """Get renamed and unnamed columns from header dataframe of merged dataset

    Args:
        headerDf (pd.DataFrame): a header dataframe of merged dataset

    Raises:
        ValueError: failed to find new header column in header dataframe
        ValueError: failed to find client header column in header dataframe
        ValueError: failed to get renamed and unnamed columns

    Returns:
        _type_: A tuple of a list of renamed columns and a list of unnamed columns
    """

    logger = Logger()

    try:

        if 'dt-new-headers' not in headerDf.columns:
            msg = 'Missing new header column in header dataframe.'
            logger.error(msg)
            raise ValueError(msg)
        elif 'dt-client-headers' not in headerDf.columns:
            msg = 'Missing client header column in header dataframe.'
            logger.error(msg)
            raise ValueError(msg)

        renamed_cols = [j for j in headerDf['dt-new-headers'] if j and TIMESTAMP not in j]
        unnamed_cols = [raw for new, raw in zip(headerDf['dt-new-headers'], headerDf['dt-client-headers']) if not new and TIMESTAMP not in raw]
                    
    except Exception as e:
        logger.error(f'Failed to get renamed and unnamed columns from merged header data: {e}')
        raise ValueError(e)

    return renamed_cols, unnamed_cols



def get_daily_baseline(timeInterval: int, chNum: int, chwpNum:int, cdwpNum:int, ctNum:int, transformedDf: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Get daily baseline report (date, kWrh, kWeh and base temp columns) from transformed dataset

    Args:
        timeInterval (int): An integer of time interval in transformed dataset
        chNum (int): An integer of chiller number
        chwpNum (int): An integer of chilled water pump number
        cdwpNum (int): An integer of condenser water pump number
        ctNum (int): An integer of cooling tower number
        transformedDf (pd.DataFrame): A dataframe of transformed columns 

    Raises:
        ValueError: failed to get daily baseline report

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple of dataframe of raw dataframe for basedline and daily dataframe for baseline
    """

    logger = Logger()
    
    try:

        if transformedDf[TIMESTAMP].dtype == 'O':
            transformedDf[TIMESTAMP] = parse_timestamp_column(transformedDf[TIMESTAMP])
            logger.warn('Convert timestamp column type from object to datetime.')


        # Get point needed in equipment base from transformed data
        cols = [TIMESTAMP, DBT, WBT, LCHWT, DBT_OPEN_WEAHTER,HUMID_OPEN_WEAHTER, SYSTEM_LOAD]
        for i in range(1, chNum+1):
            cols += [f'Chiller {i} Power kWe', f'Chiller {i} Load kWr', f'Chiller {i} Load Proportion']
        for i in range(1, chwpNum+1):
            cols += [f'Chilled Water Pump {i} Power kWe', ]
        for i in range(1, cdwpNum+1):
            cols += [f'Condenser Water Pump {i} Power kWe']
        for i in range(1, ctNum+1):
            cols += [f'Cooling Tower {i} Fan VFD Power kWe']
        data = transformedDf[[j for j in cols if j in transformedDf.columns]]
        logger.info('Get all columns needed from transform data')

        # Generate raw baseline data fo DBT/WBT/LCHWT - keep copying for old jobs
        df = data[[TIMESTAMP]].copy()
        for col in [DBT, WBT, LCHWT]:
            if col in data.keys():
                df[col] = data[col]
            else:
                df[col] = np.nan
                data[col] = np.nan

        # Calculate wet bulb temp from openWeather
        if DBT_OPEN_WEAHTER in data.columns and HUMID_OPEN_WEAHTER in data.columns:
            dry, humid = data[DBT_OPEN_WEAHTER], data[HUMID_OPEN_WEAHTER]
            data[WBT_OPEN_WEAHTER] = dry * np.arctan((0.151977 * (humid + 8.313659)**(1/2))) + np.arctan(dry + humid) - np.arctan(
                humid - 1.676331) + 0.00391838 * (humid)**(3/2) * np.arctan(0.023101 * humid) - 4.686035
            logger.info('Calculate wet bulb temp from openWeather.')

        # Map open weather data for dry/wet bulb temp
        weatherCols = [[DBT, DBT_OPEN_WEAHTER], [WBT, WBT_OPEN_WEAHTER]]
        for col1, col2 in weatherCols:
            try:
                dff = data[data[col1].notna() & data[col2].notna()]
                col_r2 = r2_score(dff[col1], dff[col2])
                logger.info(f'Weather columns: {col1}, r2: {col_r2}')
                if col_r2 > 0.75:
                    df.loc[data[col1].isna() & data[col2].notna(), col1] = data[col2]
                    logger.info(f'Map missing {col1} data by {col2} data based on r2={col_r2}')
            except Exception as e:
                logger.warn(f'Missing weather data: {str(e)}')
                pass

        df['Day Flag'] = np.nan
        df['Excluded Row Flag'] = np.nan
        logger.info('Generate raw baseline data for Dry/Wet Bulb Temp')

        # Generate raw baseline data for kWr, kWe
        raw_columns = []
        system_kwrs = []
        for i in range(1, chNum+1):
            kwr_col = f'Chiller {i} Load kWr'
            kwe_col = f'Chiller {i} Power kWe'
            loadp_col = f'Chiller {i} Load Proportion'
            raw_columns += [kwr_col, kwe_col, loadp_col]
            df[kwr_col] = data.get(kwr_col)
            df[kwe_col] = data.get(kwe_col)
            df[loadp_col] = data.get(loadp_col)

            # clear minor load if no kwe and load p < 5%
            df.loc[(df[loadp_col] < 0.05) & (df[kwe_col] == 0), kwr_col] = 0
            df.loc[(df[kwe_col] > 0) & ~(df[kwr_col] > 0), 'Excluded Row Flag'] = 'kWr'
            df.loc[(df[kwr_col] > 0) & ~(df[kwe_col] > 0), 'Excluded Row Flag'] = 'kWe'
            system_kwrs.append(kwr_col)

        # Skip clear minor load for all chiller kWrs are missing.
        if data[system_kwrs].sum().sum() == 0 and data[SYSTEM_LOAD].sum() > 0:
            df['kWr'] = data[SYSTEM_LOAD]
            logger.warn(f'Skip clear minor load for all chiller kWrs are missing.')
        else:
            df['kWr'] = df[system_kwrs].sum(axis=1)

        df['kWrh'] = df['kWr']*timeInterval/60
        df['kWe'] = data[[j for j in data.columns if 'kWe' in j]].sum(axis=1).clip(0).values
        df['kWeh'] = df['kWe']*timeInterval/60
        logger.info('Generate raw baseline data for kWr and kWe')

        # TODO: Tag row error for kWr/kWe/Weather, but don't exclude for now
        df.loc[~(df[DBT] > 0) & ~(df[WBT] > 0), 'Excluded Row Flag'] = 'Weather'
        raw_df = df.copy()

        # df.loc[df['Excluded Row Flag'] == 'kWr', 'kWeh'] = 0
        # df.loc[df['Excluded Row Flag'] == 'kWe', 'kWrh'] = 0
        # df.loc[df['Excluded Row Flag'] == 'Weather', 'kWeh'] = 0
        # df.loc[df['Excluded Row Flag'] == 'Weather', 'kWrh'] = 0
        # logger.info('Excluded row for invalid kWr/kWe.')

        # Get Dry/Wet Bulb CDD for all possible base temp (if available)
        for i in range(21):
            df[f'DCDD-{i}'] = (df[DBT] - i).clip(0) * timeInterval/(24*60)
            df[f'WCDD-{i}'] = (df[WBT] - i).clip(0) * timeInterval/(24*60)
        logger.info('Get Dry/Wet Bulb CDD for all possible base temp')

        # Get weighted DBT/WBT/LCHWT
        df['Weighted_DBT'] = df[DBT] * df['kWrh']
        df['Weighted_WBT'] = df[WBT] * df['kWrh']
        df['Weighted_LCHWT'] = df[LCHWT] * df['kWrh']

        # Get sum of daily data in from raw baseline df
        df['date'] = df[TIMESTAMP].dt.date
        raw_columns += [DBT, WBT, LCHWT, 'CDD', 'kWr', 'kWe', 'Day Flag']
        df.drop(
            columns=[j for j in df.columns if j in raw_columns], inplace=True)
        daily_df = df.groupby(df['date']).sum(numeric_only=True).reset_index()
        for col in ['Weighted_DBT', 'Weighted_WBT', 'Weighted_LCHWT']:
            daily_df[col] = daily_df[col] / daily_df['kWrh']
        daily_df['2D'] = 0
        daily_df['System_DB_lift'] = daily_df['Weighted_DBT'] - \
            daily_df['Weighted_LCHWT']
        daily_df['System_WB_lift'] = daily_df['Weighted_WBT'] - \
            daily_df['Weighted_LCHWT']
        logger.info('Get sum of daily data in from raw baseline df')

        return raw_df, daily_df

    except Exception as e:
        logger.error(f'Failed to get daily baseline data: {e}')
        raise ValueError(e)


def get_historical_base_data(chNum: int, chwpNum:int, cdwpNum:int, ctNum:int, headerNum:int, transformedDf: pd.DataFrame, minLoadThresList: list) -> pd.DataFrame:
    """Get all columns needed from historical and calculate kWe value for each equip type to be a new dataframe.

    Args:
        chNum (int): An integer of chiller number
        chwpNum (int): An integer of chilled water pump number
        cdwpNum (int): An integer of condenser water pump number
        ctNum (int): An integer of cooling tower number
        headerNum (int): An integer of header number
        transformedDf (pd.DataFrame): A dataframe of transformed columns 
        minLoadThresList (list): A list of minimum load threshold

    Raises:
        ValueError: Number of min load threshold does not match number of chiller
        ValueError: Failed to get historical data

    Returns:
        pd.DataFrame: A dataframe of historical data
    """
    logger = Logger()
    try:
        if chNum != len(minLoadThresList):
            msg = f'Number of min load threshold does not match number of chiller!'
            logger.error(msg)
            raise ValueError(msg)


        chRange = list(range(1, chNum+1))
        chwpRange = list(range(1, chwpNum+1))
        cdwpRange = list(range(1, cdwpNum+1))
        ctRange = list(range(1, ctNum+1))
        headerRange = list(range(1, headerNum+1))
        allRangeList = [chRange, chwpRange, cdwpRange, ctRange, headerRange]

        # List all columns needed in historical data
        commonColList = [
            TIMESTAMP, SYSTEM_LOAD,
            'Total Primary Side Flow',
            'Secondary Side Flow',
            'Decoupler Flow',
            LCHWT, WBT, DBT
        ]
        chillerCols = [
            'Chiller {} Load Proportion',
            'Chiller {} Load kWr',
            'Chiller {} Power kWe',
            'Chiller {} Lift',
            'Chiller {} COP',
            'Chiller {} Chilled Water Entering Temp',
            'Chiller {} Chilled Water Leaving Temp',
            'Chiller {} Condenser Water Entering Temp',
            'Chiller {} Condenser Water Leaving Temp',
            'Chiller {} Chilled Water Flow Rate L/s',
            'Chiller {} Condenser Water Flow Rate L/s',
            'Chiller {} Evaporator Pressure Drop kPa',
            'Chiller {} Condenser Pressure Drop kPa'
        ]
        chilledPumpCols = ['Chilled Water Pump {} Power kWe']
        condenserPumpCols = ['Condenser Water Pump {} Power kWe']
        coolingTowerCols = ['Cooling Tower {} Fan VFD Power kWe']
        headerCols = ['Header {} Aggregate Fan Speed Proportion',
                      'Header {} Approach']
        allColList = [chillerCols, chilledPumpCols,
                      condenserPumpCols, coolingTowerCols, headerCols]

        cols = commonColList
        for rangeList, colList in zip(allRangeList, allColList):
            cols += [k.format(j) for j in rangeList for k in colList]
        hisCols = [j for j in cols if j in transformedDf.columns]

        # Get data for the columns list
        historicalDf = transformedDf[hisCols]
        chs = [
            'Chiller {} Load Proportion',
            'Chiller {} Load kWr',
            'Chiller {} Power kWe'
        ]

        if historicalDf[[chs[1].format(j) for j in chRange]].sum().sum() > 0:
            # Clear minor loads
            for i in chRange:
                threshold = minLoadThresList[i-1]
                if threshold and float(threshold) > 0:
                    loadp = chs[0].format(i)
                    condition = historicalDf[loadp] < float(threshold)
                    ch_cols = [j.format(i) for j in chs]
                    historicalDf.loc[condition, ch_cols] = 0
            historicalDf[SYSTEM_LOAD] = historicalDf[[
                chs[1].format(j) for j in chRange]].sum(axis=1)
        else:
            logger.warn(
                f'Skip clear minor load for all chiller kWrs are missing.')

        # Sum kWe points for each equip type
        equips = ['chilled water pump', 'condenser water pump', 'cooling tower', 'chiller']
        equips_col = {}
        for item in equips:
            cols = [j for j in historicalDf.columns if (
                'kwe' in j.lower()) and item in j.lower() and 'old' not in j.lower() and 'calculated' not in j]
            historicalDf[f'{item}_HistoricalEnergyKWe'] = historicalDf[cols].sum(axis=1)
            equips_col[item] = cols
        historicalDf[f'pump_HistoricalEnergyKWe'] = historicalDf[['chilled water pump_HistoricalEnergyKWe',
                                                                  'condenser water pump_HistoricalEnergyKWe']].sum(axis=1)
        historicalDf['HistoricalEnergyKWe (before ADR)'] = historicalDf[['chiller_HistoricalEnergyKWe',
                                                                        'pump_HistoricalEnergyKWe', 'cooling tower_HistoricalEnergyKWe']].sum(axis=1)
        historicalDf['HistoricalEnergyKWe'] = historicalDf['HistoricalEnergyKWe (before ADR)']
        historicalDf['System Cooling Load (before ADR)'] = historicalDf[SYSTEM_LOAD]
        historicalDf['Historical COP'] = historicalDf[
            'System Cooling Load (before ADR)'] / historicalDf['HistoricalEnergyKWe']
    except Exception as e:
        logger.error(f'Failed to get historical baseline data: {e}')
        raise ValueError(e)
    return historicalDf


def parse_timestamp_column(timeSeries: pd.Series) -> pd.Series:
    """Parse timestamp column using pd.to_datetime method with known time formats. Error out if none of existing format fitted.

    Args:
        timeSeries (pd.Series): A datetime series data.

    Raises:
        ValueError: None of existing format fitted.

    Returns:
        pd.Series: A parsed datetime series data.x
    """
    logger = Logger()
    
    time_format_list = [
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%y %H:%M", 
    ]
    parsedTimeSeries = None
    for timeFormat in time_format_list:
        try:
            parsedTimeSeries = pd.to_datetime(timeSeries, format=timeFormat)
        except:
            continue
        else:
            logger.info(f'Format parsed: {timeFormat} ({timeSeries[0]})')
            return parsedTimeSeries

    if not parsedTimeSeries:
        msg = f'[{timeSeries[0]}] does not fit existing formats.'
        logger.error(msg)
        raise ValueError(msg)
        

def find_stage_one_chs(capList: list) -> int:
    """Find chiller number with smallest capacity, return first one if multiple ones found.

    Args:
        capList (list): A list of all chillers capacity

    Returns:
        int: A chiller number that gets smallest capacity
    """
    
    capList = [np.nan if v is None else v for v in capList]
    
    return int(np.nanargmin(capList) + 1)

def get_historical_stages(stage1ChList: list, loadData: np.array) -> np.array:
    """Get stage values for 0 (no chiller on), 1 (single stage 1 chiller on), 2+ (multiple or other chillers on)     

    Args:
        stage1ChList (list): A list of all chillers in stage one.
        loadData (np.array): A numpy array of load kwr data for all chillers (assume chiller from 1 to n)

    Returns:
        np.array: A numpy array of stage 0, 1, 2
    """
    chRange = np.arange(1, len(loadData)+1)
    loadDf = pd.DataFrame(loadData.T, columns=chRange)
    stage2ChList = [j for j in chRange if j not in stage1ChList]
    conditions = [
        (loadDf.sum(axis=1)<=0),
        ((loadDf[stage1ChList]>0).sum(axis=1) == 1)&(loadDf[stage2ChList].sum(axis=1) <=0),
        ((loadDf[stage1ChList]>0).sum(axis=1) > 1)|(loadDf[stage2ChList].sum(axis=1) > 0),
    ]
    choices = [0, 1, 2]
    stageData = np.select(conditions, choices, default=np.nan)
    stageData

    return stageData


def get_system_data_drops(stage1ChList: list, loadData: np.array, interval: int) -> np.array:
    """Get a numpy array of invalid starts/stops flag data 

    Args:
        stage1ChList (list): A list of all chillers in stage one.
        loadData (np.array): A numpy array of load kwr data for all chillers (order of chiller 1 to n)
        interval (int): An integer of time step for each row in loadData

    Returns:
        np.array: A numpy array of invalid starts/stops flag data (np.nan or 1)
    """
    TREND_PERIOD = 30

    # Get stage data
    stageData = get_historical_stages(stage1ChList, loadData)
    df = pd.DataFrame(stageData, columns=['stage'])

    # Get invalid starts/stops data
    trendRowNum = TREND_PERIOD // interval
    system_off = df['stage'] == 0
    stage_above_one = (df['stage'].shift(1) > 1)|(df['stage'].shift(-1) > 1)
    short_gaps = df['stage'].groupby((df['stage'] != df['stage'].shift(1)).cumsum()).transform('size')<=trendRowNum
    df.loc[system_off & stage_above_one & short_gaps, 'outputs'] = 1
    return df['outputs'].values


def get_weighted_COP(timestamp: np.array, actual_cop: np.array, expected_cop: np.array, kwr: np.array) -> Tuple[np.array, np.array, np.array]:
    """Get numpy array of weighted COPs from actual/expected COP and kWr data, with grouping timestamp to date.

    Args:
        timestamp (np.array): A numpy array of timestamp in transformation file
        actual_cop (np.array):  A numpy array of actual COP data for a single chiller
        expected_cop (np.array): A numpy array of expected COP data for a single chiller
        kwr (np.array): A numpy array of load kwr data for a single chiller

    Raises:
        ValueError: If data type of the input actual_cop is not float or integer.
        ValueError: If data type of the input expected_cop is not float or integer.
        ValueError: If data type of the input kwr is not float or integer.
        ValueError: If data type of the input timestamp is not datetime.

    Returns:
        Tuple[np.array, np.array, np.array]: 3 numpy arrays of date, weighted actual/expected COP in a daily basis.
    """
    
    # Check data type for numpy array of all input variables
    if not np.issubdtype(actual_cop.dtype, np.floating) and not np.issubdtype(actual_cop.dtype, np.integer):
        raise ValueError('Data type for actual_cop must be numerical.')
    if not np.issubdtype(expected_cop.dtype, np.floating) and not np.issubdtype(expected_cop.dtype, np.integer):
        raise ValueError('Data type for expected_cop must be numerical.')
    if not np.issubdtype(kwr.dtype, np.floating) and not np.issubdtype(kwr.dtype, np.integer):
        raise ValueError('Data type for kwr must be numerical.')
    if not np.issubdtype(timestamp.dtype, np.datetime64):
        raise ValueError('Data type for timestamp must be datetime-like.')

    # Get weighted actual/expected COP
    df = pd.DataFrame(zip(timestamp, actual_cop, expected_cop, kwr), columns=['timestamp', 'actual_cop', 'expected_cop', 'kwr'])
    df['date'] = df['timestamp'].dt.date
    df['weighted_actual_cop'] = df['actual_cop'] * df['kwr']
    df['weighted_expected_cop'] = df['expected_cop'] * df['kwr']

    # Get daily average weighted COPs
    daily_df = df.groupby(df['date']).sum(numeric_only=True)
    daily_df['weighted_actual_cop'] = daily_df['weighted_actual_cop'] / daily_df['kwr']
    daily_df['weighted_expected_cop'] = daily_df['weighted_expected_cop'] / daily_df['kwr']

    # Format results into numpy array
    date = np.array(daily_df.index)
    weighted_actual_cop = np.array(daily_df['weighted_actual_cop'].round(3))
    weighted_expected_cop = np.array(daily_df['weighted_expected_cop'].round(3))

    return date, weighted_actual_cop, weighted_expected_cop

def kw2ton(kw):
    tons = kw / TON_TO_KWR
    return tons

def celsius2fahrenheit(celsius, delta=False):
    if delta:
        fahrenheit = celsius * F_TO_C_RANGE
    else:
        fahrenheit = (celsius * F_TO_C_RANGE) + 32
    return fahrenheit

def get_stage_identifier(stageName):
    return str([int(j) for j in list(stageName.split('_')[-1])])

def add_scatter_to_figure(figureUrl, templateName, xData, yData, zData, scatterColor):
    data = json.load(urlopen(figureUrl))
    fig = go.Figure(data)
    templateTrace = [j for j in fig.data if j['name'] == templateName][0]
    hoverTemplate = templateTrace['hovertemplate']
    markerSize = templateTrace['marker']['size']
    fig.add_trace(go.Scatter3d(name='Post-implementation', x=xData, y=yData, z=zData, mode='markers', marker={'color':scatterColor, 'size':markerSize}, hovertemplate=hoverTemplate))
    return fig

def save_fig_to_s3(api, fig):
    config = dict({'scrollZoom': False, 'displaylogo': False,
                  'modeBarButtonsToRemove': ['resetCameraLastSave3d']})

    html_name  = "{}.html".format(uuid.uuid4().hex)
    fig.write_html(html_name, config=config)
    url2s3 = api.sendToBucket(html_name, 'text/html')
    os.remove(html_name)
    return url2s3


def get_post_imp_cdw_3d_urls(api: exergenics.ExergenicsApi, cdwFigureDict: dict, df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate and retrieve URLs for 3D scatter plots representing cooling tower performance metrics after implementation.

    Parameters:
    - api (exergenics.ExergenicsApi): An instance of the Exergenics API for communication.
    - cdwFigureDict (dict): A dictionary containing information about the cooling tower figures.
    - df (pd.DataFrame): Input DataFrame containing chiller stage data.

    Returns:
    pd.DataFrame: DataFrame with information about the generated figure URLs, including header number,
    stage identifier, category (metric, mixed, imperial), and the corresponding URL.
    """
    logger = Logger()
    
    # Get Chiller Stage column from mv_transformation, error out if not exist
    if 'Chiller Stage' not in df.columns:
        raise ValueError(f'Stage identifier column [Chiller Stage] not in mv_transformation data, please rerun latest mv_transformed module.')

    xCol = 'System Cooling Load'
    yCol = 'Wet Bulb Temperature'
    newCdwFigureData = []
    for header in cdwFigureDict:
        headerNum = header.split('_')[-1]
        zCol = f'Header {headerNum} Approach'
        for stage in cdwFigureDict[header]:

            # Get list of stage identifier and its identical stages (if exist)
            stageIdentifier = get_stage_identifier(stage)
            stageIdsList = [stageIdentifier]
            if len(cdwFigureDict[header][stage]['identical_stages']) > 0:
                stageIdsList += [get_stage_identifier(j) for j in cdwFigureDict[header][stage]['identical_stages']]
            
            # Filter mv period data by stage identifiers and send warning log if chosen stage not exist in mv period
            stageDf = df[df['Chiller Stage'].isin(stageIdsList)][[xCol, yCol, zCol]]
            if len(stageDf) == 0:
                logger.warn(f'Stage: {stageIdsList} does not exist in MV period.')
            else:
                # Generate and save metric chart
                metricFig = add_scatter_to_figure(
                    figureUrl=cdwFigureDict[header][stage]['url']['metric'], templateName='Historical', 
                    xData=stageDf[xCol], yData=stageDf[yCol], zData=stageDf[zCol], scatterColor=POST_IMP_SCATTER_COLOR
                )
                metircUrl = save_fig_to_s3(api, metricFig)
                newCdwFigureData.append([headerNum, stageIdentifier, 'metric', metircUrl])

                # Generate and save mixed chart
                mixedFig = add_scatter_to_figure(
                    figureUrl=cdwFigureDict[header][stage]['url']['mixed'], templateName='Historical', 
                    xData=kw2ton(stageDf[xCol]), yData=stageDf[yCol], zData=stageDf[zCol], scatterColor=POST_IMP_SCATTER_COLOR
                )
                mixedUrl = save_fig_to_s3(api, mixedFig)
                newCdwFigureData.append([headerNum, stageIdentifier, 'mixed', mixedUrl])

                # Generate and save imperial chart
                imperialFig = add_scatter_to_figure(
                    figureUrl=cdwFigureDict[header][stage]['url']['imperial'], templateName='Historical', 
                    xData=kw2ton(stageDf[xCol]), yData=celsius2fahrenheit(stageDf[yCol]), zData=celsius2fahrenheit(stageDf[zCol], delta=True), scatterColor=POST_IMP_SCATTER_COLOR
                )
                imperialUrl = save_fig_to_s3(api, imperialFig)
                newCdwFigureData.append([headerNum, stageIdentifier, 'imperial', imperialUrl])
    outputDf = pd.DataFrame(newCdwFigureData, columns=['headerNum', 'stageIdentifier', 'category', 'url'])
    logger.info('Get table of urls for all headers')
    
    return outputDf


def english_converter(content: str, target: Literal["uk","us"]) -> str:
    """
    Convert English content from one dialect to another (UK or US).

    Parameters:
    - content (str): The English content to be converted.
    - target (Literal["uk", "us"]): The target English dialect for conversion. 
      It can be either "uk" for British English or "us" for American English.

    Returns:
    str: The converted English content based on the specified target dialect.
    """
    if not isinstance(content, str):
        raise ValueError(f'Only convert string content, {type(content)} is not allowed!')
    fixer = TextFixer(content=content, target=Target(target))
    result = fixer.apply()
    return result

def fig_COP_to_kW_ton(fig):
    """
    Convert the z-axis values (COP) of a 3D scatter plot figure to KW/Ton.

    Parameters:
    - fig: Plotly Figure: The input 3D scatter plot figure.

    Returns:
    None: The function modifies the input figure in-place.

    Note:
    The function updates the z-axis values in each trace of the figure to represent KW/Ton.
    It also modifies the hovertemplate to reflect the change and updates the layout accordingly.
    """
    # Update z-axis(COP) to KW/Ton
    for trace in fig.data:
        trace.z = np.array(trace.z, dtype=float)
        trace.z = np.true_divide(TON_TO_KWR, np.clip(trace.z, 1, None))

        trace.hovertemplate = trace.hovertemplate.replace('COP', 'KW/Ton')

    fig.update_layout(scene=dict(
        zaxis=dict(tick0=0.1, dtick=0.2,range=[0, 1.2]),
        zaxis_title="KW/Ton"))
    return fig


def fig_fahrenheit_to_celsius(fig):    
    """
    Convert the x-axis values (Lift) of a 3D scatter plot figure from Fahrenheit to Celsius.

    Parameters:
    - fig: Plotly Figure: The input 3D scatter plot figure.

    Returns:
    Plotly Figure: The modified 3D scatter plot figure with x-axis values converted to Celsius.

    Note:
    The function updates the x-axis values in each trace of the figure to represent Celsius.
    It also modifies the hovertemplate and trace name to reflect the change and updates the layout accordingly.
    """
    # Update x-axis(Lift) to Fahrenheit
    for trace in fig.data:
        trace.x = [j*F_TO_C_RANGE for j in trace.x]
        trace.hovertemplate = trace.hovertemplate.replace(
            'Lift (°C)', 'Lift (°F)')

        # Using american english for imperial chart
        trace.name = english_converter(trace.name, 'us')
    fig.update_layout(scene=dict(
        xaxis=dict(nticks=6, range=[int(j*F_TO_C_RANGE) for j in fig.layout.scene.xaxis.range]),
        xaxis_title="Lift (°F)"))
    return fig


def get_post_imp_sim_3d_urls(api: exergenics.ExergenicsApi, sim3dFigureDict: dict, df: pd.DataFrame) -> pd.DataFrame:

    """
    Generate and retrieve URLs for 3D scatter plots representing chiller simulation data after recommendations implementation.

    Parameters:
    - api: An instance of the Exergenics API for communication.
    - sim3dFigureDict: A dictionary containing information about the simulation figures.
    - df: Input DataFrame containing post-implementation data.

    Returns:
    pd.DataFrame: DataFrame with information about the generated figure URLs, including chiller number,
    category (metric, mixed, imperial), and the corresponding URL.
    """
    logger = Logger()

    newSim3dFigureData = []
    for chillerNum in sim3dFigureDict:
        traceNumberList = sim3dFigureDict[chillerNum]['traceNumberList']
        jsonUrl = sim3dFigureDict[chillerNum]['jsonUrl']

        simData = []
        for i in traceNumberList:
            xCol = f'Chiller {i} Lift'
            yCol = f'Chiller {i} Load Proportion'
            zCol = f'Chiller {i} COP'
            tmpDf = df[(df[xCol] > 0) & (df[yCol] > 0) & (df[zCol] > 0) & (df[zCol]<100)][[xCol, yCol, zCol]].copy()
            tmpDf.columns = ['x', 'y', 'z']
            simData.append(tmpDf)
        simData = pd.concat(simData)
        logger.info(f'Get post implementation data for ch{chillerNum}, with identical chs list of {traceNumberList}')
        
        # Generate and save metric chart
        fig = add_scatter_to_figure(jsonUrl, "Pre-Optimisation", simData['x'], simData['y'], simData['z'], POST_IMP_SCATTER_COLOR)
        metircUrl = save_fig_to_s3(api, fig)
        newSim3dFigureData.append([chillerNum, 'metric', metircUrl])

        # Generate and save mixed chart
        fig_COP_to_kW_ton(fig)
        mixedUrl = save_fig_to_s3(api, fig)
        newSim3dFigureData.append([chillerNum, 'mixed', mixedUrl])

        # Generate and save imperial chart
        fig_fahrenheit_to_celsius(fig)
        imperialUrl = save_fig_to_s3(api, fig)
        newSim3dFigureData.append([chillerNum, 'imperial', imperialUrl])
    outputDf = pd.DataFrame(newSim3dFigureData, columns=['chillerNum', 'category', 'url'])
    logger.info('Get table of urls for all chillers')
    
    return outputDf

def map_data_selection(selectionDf: pd.DataFrame, manifest: list, isV2: bool =True) -> list:
    """
    Map data selection information to the manifest.

    Parameters:
    - selectionDf (pd.DataFrame): DataFrame containing data selection information.
    - manifest (list): List of dictionaries representing the manifest.
    - isV2 (bool, optional): Flag indicating whether the data selection is in V2 format. Defaults to True.

    Returns:
    list: Modified manifest with 'selected' key indicating the selected points.

    Note:
    The function updates the 'selected' key in the manifest based on the data selection information.
    It also ensures that openWeather points are forcibly selected.
    """
    try:
        logger = Logger()
        # get selected points from selection dataframe
        if isV2:
            selectedList = list(selectionDf[selectionDf['selected'] == 'Y']['point'].values)
        else:
            selectedList = list(selectionDf[selectionDf['selected-rows']==True]['point'].values)

        # force selecting openWeather points
        if 'temp (from openWeather)' not in selectedList:
            selectedList.append('temp (from openWeather)')
        if 'humidity (from openWeather)' not in selectedList:
            selectedList.append('humidity (from openWeather)')
        
        # paste selection to manifest
        for idx, row in enumerate(manifest):
            if row['point'] in selectedList:
                manifest[idx]['selected'] = 'Y'

    except Exception as e:
        logger.error(f'Failed to map data selection for {e}')
        raise EtlError('Failed to map data selection from baseline to mv/rw job.')

    return manifest

def set_data_selection_outputs(jobId: Union[int, str], environment: str, jobType: str, api: exergenics.ExergenicsApi = None) -> bool:
    """
    Set data selection outputs for a given job.

    Parameters:
    - jobId (Union[int, str]): Identifier of the job.
    - environment (str): Environment information.
    - jobType (str): Type of the job, e.g., 'mv' or 'rw'.
    - api (exergenics.ExergenicsApi, optional): An instance of the Exergenics API.
      If not provided, a new API instance will be created using the specified environment.

    Returns:
    bool: True if the operation is successful, False otherwise.

    Note:
    The function copies data selection information from the baseline job to the specified job type.
    It saves the selected manifest to the job and copies the time interval information.
    The jobType parameter is used to customize the output paths based on the specific job type.
    """
    try:
        logger = Logger()
        if not api:
            api = create_api(environment)
        
        # Copy data selection
        manifestUrl = api.getJobData(jobId, f'{jobType}_pre_header_ready.outputs.point_manifest')
        manifest = json.loads(urlopen(manifestUrl).read())

        selectionV2Url = api.getJobData(jobId, 'data_selection_ready.outputs.point_manifest')
        if selectionV2Url:
            selectionDf = pd.read_json(selectionV2Url)
            manifest = map_data_selection(selectionDf, manifest, isV2=True)
            logger.info(f'Copied v2 data selection')
        else:
            selectionV1Url = api.getJobData(jobId, 'selection')
            if selectionV1Url:
                selectionDf = pd.read_csv(selectionV1Url)
                manifest = map_data_selection(selectionDf, manifest, isV2=False)
                logger.warn(f'Copied v1 data selection')
            else:
                raise ValueError(f'Missing data selection in baseline job')

        # Save selected manifest to mv/rw job
        pathName = f'job{jobId}_{jobType}_data_selection_manifest.json'
        with open(pathName, 'w') as f:
            json.dump(manifest, f)
        url2s3 = api.sendToBucket(pathName)
        os.remove(pathName)
        api.setJobData(jobId, f'{jobType}_data_selection_ready.outputs.point_manifest', url2s3)

        # Copy time interval
        timeInterval = api.getJobData(jobId, 'data_selection_ready.outputs.time_interval')
        if timeInterval:
            api.setJobData(jobId, f'{jobType}_data_selection_ready.outputs.time_interval', timeInterval)
        else:
            raise ValueError(f'Missing time interval in baseline job')
        logger.info('Copy time interval.')

        status = True
    except Exception as e:
        logger.error(e)
        status = False
    return status

def map_header_mapping_v1(v1Df: pd.DataFrame) -> dict:
    """
    Map V1 header mappings to V2 format.

    Parameters:
    - v1Df (pd.DataFrame): DataFrame containing V1 header mappings.

    Returns:
    dict: Dictionary representing the V2 header mappings.

    Note:
    The function filters out mappings where 'dt-client-headers' and 'dt-new-headers' are not equal.
    It converts the V1 DataFrame format to V2 dictionary format.
    """
    try:
        logger = Logger()
            
        # get v1 header mappings
        v1Df = v1Df[(v1Df['dt-client-headers'] != v1Df['dt-new-headers']) & (v1Df['dt-new-headers'] != 'Timestamp')]

        # Convert v1 format (df) to v2 format (dict) 
        v2Dict = pd.Series(v1Df['dt-new-headers'].values,index=v1Df['dt-client-headers']).to_dict()

    except Exception as e:
        logger.error(f'Failed to map header mapping v1 for {e}')
        raise EtlError('Failed to map header mapping v1 from baseline to mv/rw job.')

    return v2Dict

def set_header_mapping_outputs(jobId: Union[int, str], environment: str, jobType: str, api: exergenics.ExergenicsApi = None) -> bool:
    """
    Set header mapping outputs for a given job.

    Parameters:
    - jobId (Union[int, str]): Identifier of the job.
    - environment (str): Environment information.
    - jobType (str): Type of the job, e.g., 'mv' or 'rw'.
    - api (exergenics.ExergenicsApi, optional): An instance of the Exergenics API.
      If not provided, a new API instance will be created using the specified environment.

    Returns:
    bool: True if the operation is successful, False otherwise.

    Note:
    The function copies header mapping information from the baseline job to the specified job type.
    It saves the V2 header mapping result to the job and copies unit conversion information.
    The jobType parameter is used to customize the output paths based on the specific job type.
    """
    try:
        logger = Logger()
        if not api:
            api = create_api(environment)
        
        # Copy header mapping
        mappingUrl = api.getJobData(jobId, 'header_ready.outputs.mapping')
        if mappingUrl:
            api.setJobData(jobId, f'{jobType}_header_ready.outputs.mapping', mappingUrl)
            logger.info(f'Copied v2 header mapping')
        else:
            v1Url = api.getJobData(jobId, 'headermapping')
            if v1Url:
                v1Df = pd.read_csv(v1Url, usecols=['dt-client-headers', 'dt-new-headers'])
                v2Dict = map_header_mapping_v1(v1Df)
                
                # Save v2 result to jobData
                pathName = f'job{jobId}_{jobType}_header_mapping.json'
                with open(pathName, 'w') as f:
                    json.dump(v2Dict, f)
                url2s3 = api.sendToBucket(pathName)
                os.remove(pathName)
                api.setJobData(jobId, f'{jobType}_header_ready.outputs.mapping', url2s3)
                logger.warn(f'Copied v1 header mapping')
            else:
                raise ValueError(f'Missing header mapping in baseline job')

        # Copy unit conversion
        unitConvUrl = api.getJobData(jobId, 'header_ready.outputs.unit_conversion')
        if unitConvUrl:
            api.setJobData(jobId, f'{jobType}_header_ready.outputs.unit_conversion', unitConvUrl)
            logger.info('Copy unit conversion.')

        status = True
    except Exception as e:
        logger.error(e)
        status = False
    return status
  
def get_selection_and_interval(manifest: list) -> Tuple[list, int]:
    """
    Updates the 'selected' field in each point of the manifest to 'Y' and
    calculates the most common interval from the 'interval' field.

    Parameters:
    - manifest (List[dict]): A list of dictionaries representing data points.
      Each dictionary should have 'selected' and 'interval' fields.

    Returns:
    - Tuple[List[dict], int]: A tuple containing the updated manifest and
      the most common interval from the 'interval' field.
    """
    intervalList = []
    for idx, point in enumerate(manifest):
        manifest[idx]['selected'] = 'Y'
        interval = manifest[idx]['interval']
        if interval.isdigit() and int(interval)>0:
            intervalList.append(int(interval))
    timeInterval = max(set(intervalList), key=intervalList.count)
    return manifest, timeInterval

def skip_data_selection(jobId: Union[int, str], environment: str, api: exergenics.ExergenicsApi = None) -> bool:
    """
    Skip data selection process for a job if the number of points in the manifest is less than 200.

    Parameters:
    - jobId (Union[int, str]): The identifier of the job.
    - environment (str): The environment in which the job is running.
    - api (exergenics.ExergenicsApi, optional): An instance of the Exergenics API.
      If not provided, a new API instance will be created using the specified environment.

    Returns:
    - bool: True if data selection should be skipped; False otherwise.

    Raises:
    - Exception: If an error occurs during the process, an exception is caught and printed,
      and the function returns False.
    """
    try:
        skipFlag = False

        if not api:
            api = create_api(environment)
        manifestUrl = api.getJobData(jobId, 'pre_header_ready.outputs.point_manifest')
        if manifestUrl:
            manifest = json.loads(urlopen(manifestUrl).read())
            if len(manifest) < 200:
                manifest, timeInterval = get_selection_and_interval(manifest)
                pathName = f'/tmp/{environment}/{jobId}/data_selection_manifest.json'
                os.makedirs(os.path.dirname(pathName), exist_ok=True)
                with open(pathName, 'w') as f:
                    json.dump(manifest, f)

                save_file_to_portal(api, pathName, jobId,  'data_selection_ready.outputs.point_manifest')
                api.setJobData(jobId, 'data_selection_ready.outputs.time_interval', timeInterval)
                skipFlag = True
    except Exception as e:
        print(e)
        skipFlag = False

    return skipFlag

def set_stage_change(df):

    # Get all kWr columns
    kWrCols = [j for j in df.columns if 'kWr' in j and 'Old' not in j]

    # Get all stage up rows (number of chillers on in the next time step is greater than number of chillers on in the previous time step)
    stageUp = ((df[kWrCols] > 0).sum(axis=1) -
               (df[kWrCols] > 0).sum(axis=1).shift(1) > 0)

    # Get all already-on rows (number of chillers on in the previous timestep is > 0)
    moreThanOneChiller = ((df[kWrCols] > 0).sum(axis=1).shift(1) > 0)

    # Set stage up column value = 1 if system already on and stage up
    df.loc[moreThanOneChiller & stageUp, 'Stage Up'] = 1
    return df

def set_stablisation_delay(df, sysLoad, stablisationDelay):
    
    df[sysLoad] = df[sysLoad].fillna(0)
    stageUpWindow = []
    for j in df[df['Stage Up'] == 1].index:
        stageUpWindow += [k for k in range(j, j+stablisationDelay)]
    df.loc[stageUpWindow, sysLoad] = np.nan
    df[sysLoad] = df[sysLoad].interpolate()
    return df

def get_default_historical_final(historicalBaseDataDf: pd.DataFrame) -> pd.DataFrame:

    """
    Enhances the provided historical base data DataFrame by adding additional columns and modifications of stabilisation delay and moving average.

    Parameters:
    - historicalBaseDataDf (pd.DataFrame): The input DataFrame containing historical base data.

    Returns:
    pd.DataFrame: A modified DataFrame with additional columns for error days, stage changes, stabilisation delay, moving average, and cleaned column names.
    """
    logger = Logger()

    DEFAULT_STABALISATION_DELAY = 1
    DEFAULT_MOVING_AVERAGE = 3
    df = historicalBaseDataDf.copy()

    # Add empty Error Day column in historical data
    df['Error Day'] = np.nan
    logger.info('Add empty Error Day column.')

    t, SYSTEM_LOAD = ['Timestamp', 'System Cooling Load']
    df[t] = pd.to_datetime(
        df[t], infer_datetime_format=True)
    fillZeroList = [j for j in df.columns if 'Historical' not in j and 'ADR' not in j and j != 'Error Day']
    df[fillZeroList] = df[fillZeroList].replace(np.nan, 0)
    logger.info('Fill in zeroes to columns.')

    df = set_stage_change(df)
    logger.info('Set Stage Up column.')

    df['year'] = df[t].dt.year
    df['month'] = df[t].dt.month
    df['Day Of Week'] = df[t].dt.day_name()
    df['Time'] = df[t].dt.time
    df[SYSTEM_LOAD + '(before stabilisation delay)'] = df[SYSTEM_LOAD]
    logger.info('Get system cooling load before stablisation delay.')

    df.index = df.index.astype(int)
    df = set_stablisation_delay(
        df, SYSTEM_LOAD, DEFAULT_STABALISATION_DELAY)
    logger.info('Set stablisation delay.')
    oldSysLoad = SYSTEM_LOAD + '(before moving average)'
    df[oldSysLoad] = df[SYSTEM_LOAD]

    df[SYSTEM_LOAD] = df[SYSTEM_LOAD].replace(0, np.nan).rolling(
        window=int(DEFAULT_MOVING_AVERAGE), center=True, min_periods=1).mean().replace(np.nan, 0)
    df.loc[df[oldSysLoad] == 0, SYSTEM_LOAD] = 0
    df.loc[df[oldSysLoad] == df[oldSysLoad].max(),
            SYSTEM_LOAD] = df[oldSysLoad].max()
    logger.info('Set moving average.')

    df['Timestamp'] = pd.to_datetime(
        df['Timestamp'], infer_datetime_format=True)
    df.drop(columns=['year', 'month', 'Day Of Week', 'Time'], inplace=True)
    df.columns = df.columns.str.replace(' ', '')
    logger.info('Remove whitespaces in column headers.')

    return df

def clear_seasonal_cleaned_data(api: exergenics.ExergenicsApi, jobId: Union[int, str]) -> list:

    """
    Clears seasonal cleaned historical data associated with a specific job.

    Parameters:
    - api (ExergenicsApi): The Exergenics API instance for data manipulation.
    - jobId (Union[int, str]): The identifier for the specific job.

    Returns:
    List[str]: A list of seasons for which the seasonal cleaned historical data was successfully removed.
    """

    # get all seasons from portal
    seasonOptions = []
    if api.getTreeData('t_seasons'):
        while api.moreResults():
            rootNode = api.nextResult()
            season = rootNode['ontology'].lower()
            seasonOptions.append(season)

    # get full jobData
    api.getJob(jobId)
    job = api.nextResult()
    jobData = job['jobData']

    # remove seasonal cleaned historical data if exist
    removedSeason = []
    for season in seasonOptions:
        historicalSeasonalUrl = jobData.get(f'baselining_ready.outputs.historical_season_{season}_csv_url')
        if historicalSeasonalUrl:
            api.setJobData(
            jobId, f'baselining_ready.outputs.historical_season_{season}_csv_url', '')
            removedSeason.append(season)
    return removedSeason