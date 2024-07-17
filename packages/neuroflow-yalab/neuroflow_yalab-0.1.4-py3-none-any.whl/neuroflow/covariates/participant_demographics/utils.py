from pathlib import Path
from typing import Union

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# define scopes
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# Sheet name
SHEET_NAME = "CRF YA"

# Worksheet name
WORKSHEET_NAME = "גיליון1"

# Columns to keep from the CRF
CRF_COLUMNS_TO_KEEP = {
    "Questionnaire": "subject_id",
    "Sex": "sex",
    "Date of Birth": "dob",
    "Height (cm)": "height",
    "Weight (kg)": "weight",
    "Study": "study",
    "Group": "group",
    "Condition": "condition",
}

# Transformations of the CRF columns
CRF_TRANSFORMATIONS = {
    "sex": lambda x: x.upper()[0],
    "dob": pd.to_datetime,
    "height": pd.to_numeric,
    "weight": pd.to_numeric,
    # make strings lowercase
    "study": lambda x: x.lower(),
    "group": lambda x: x.lower(),
    "condition": lambda x: x.lower(),
}


def load_or_request_credentials(
    credentials_path: Union[str, Path]
) -> ServiceAccountCredentials:
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_path, SCOPES
        )
    except FileNotFoundError as err:
        raise FileNotFoundError(
            f"Credentials file not found at {credentials_path}"
        ) from err
    return credentials


def get_worksheet(
    credentials: ServiceAccountCredentials,
    sheet_name: str = SHEET_NAME,
    worksheet_name: str = WORKSHEET_NAME,
) -> pd.DataFrame:
    """
    Get a worksheet from a Google Sheet

    Parameters
    ----------
    credentials : ServiceAccountCredentials
        The credentials to access the Google Sheet
    sheet_name : str
        The name of the Google Sheet
    worksheet_name : str
        The name of the worksheet in the Google Sheet

    Returns
    -------
    pd.DataFrame
        The worksheet as a DataFrame
    """
    gc = gspread.authorize(credentials)
    sheet = gc.open(sheet_name)
    worksheet = sheet.worksheet(worksheet_name)
    return pd.DataFrame(worksheet.get_all_records())
