"""
This module provides functionality to interact with Google Sheets API. It includes functions to refresh and retrieve access tokens using OAuth2 credentials, and to fetch data from a specified Google Sheets spreadsheet, optionally converting it to a pandas DataFrame.

Functions:
    refresh_access_token(refresh_token): Refreshes the Google OAuth2 access token using a provided refresh token.
    get_access_token(): Retrieves a new access token using the stored refresh token.
    get_sheet_data(main_spreadsheet_id, sub_sheet_name, to_pandas_df=True): Retrieves data from a specified Google Sheets spreadsheet and converts it to a pandas DataFrame if required.

Examples:
    # Refresh access token
    new_token = refresh_access_token('your_refresh_token_here')

    # Get new access token
    access_token = get_access_token()

    # Fetch data from a Google Sheet and convert to DataFrame
    data_frame = get_sheet_data('spreadsheet_id', 'sheet_name')
"""

import pandas as pd
import logging
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.discovery import Resource

from bullpenfi.auth import authenticator

# Configure the root logger to display logs of INFO level and above
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # Add StreamHandler to output to stdout
    ],
)

logger = logging.getLogger(__name__)


class GoogleSheetService:
    """
    A class to interact with Google Sheets API.

    This class provides functionality to refresh and retrieve access tokens using OAuth2 credentials,
    and to fetch data from a specified Google Sheets spreadsheet, optionally converting it to a pandas DataFrame.
    """

    def __init__(
        self, api_key, refresh_token, client_id, client_secret, spreadsheet_id
    ):
        """
        Initialize the GoogleSheetService.

        Args:
            refresh_token (str): The Google Cloud refresh token.
            client_id (str): The Google Cloud client ID.
            client_secret (str): The Google Cloud client secret.
            spreadsheet_id (str): The ID of the Google Sheets spreadsheet.
        """
        authenticator.authenticate(api_key)
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.spreadsheet_id = spreadsheet_id
        self.header_cache = {}
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    def refresh_access_token(self):
        """
        Refreshes the Google OAuth2 access token using the stored refresh token.

        Returns:
            str: The new access token.
        """
        creds = Credentials(
            None,
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=self.scopes,
        )
        creds.refresh(Request())
        return creds.token

    def get_access_token(self):
        """
        Retrieves a new access token using the stored refresh token.

        Returns:
            str: A new access token.
        """
        return self.refresh_access_token()

    def get_sheet_data(self, sub_sheet_name="accounts_sheet", to_pandas_df=True):
        """
        Retrieves data from a specified Google Sheets spreadsheet and sheet.

        Args:
            sub_sheet_name (str): The name of the sheet within the spreadsheet.
            to_pandas_df (bool): If True, converts the retrieved data to a pandas DataFrame.

        Returns:
            DataFrame or list: A pandas DataFrame containing the sheet data if to_pandas_df is True,
                               otherwise a list of lists representing the data.
        """
        logger.info(
            "Fetching data from spreadsheet ID: %s, sheet name: %s",
            self.spreadsheet_id,
            sub_sheet_name,
        )
        access_token = self.get_access_token()
        creds = Credentials(access_token)
        service: Resource = build("sheets", "v4", credentials=creds)

        try:
            result = (
                service.spreadsheets()  # pylint: disable=no-member
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=f"{sub_sheet_name}!A1:Z")
                .execute()
            )
        except HttpError as error:
            logger.error("An error occurred: %s", error)
            raise

        values = result.get("values", [])

        if not values:
            logger.info("No data found in sheet: %s.", sub_sheet_name)
            return pd.DataFrame()

        header = values[0]
        data = [
            (
                row[: len(header)]
                if len(row) > len(header)
                else row + [""] * (len(header) - len(row))
            )
            for row in values[1:]
        ]

        if to_pandas_df:
            return pd.DataFrame(data, columns=header)
        else:
            return data

    def append_row_to_sheet(self, sub_sheet_name, row_data):
        """
        Appends a new row of data to a specified Google Sheets spreadsheet and sheet.

        Args:
            sub_sheet_name (str): The name of the sheet within the spreadsheet.
            row_data (dict): A dictionary where keys are column headers and values are the data to be added.

        Returns:
            dict: The response from the Google Sheet API after appending the data.
        """
        access_token = self.get_access_token()
        creds = Credentials(access_token)
        service = build("sheets", "v4", credentials=creds)

        if sub_sheet_name not in self.header_cache:
            result = (
                service.spreadsheets()  # pylint: disable=no-member
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=f"{sub_sheet_name}!A1:Z1")
                .execute()
            )
            self.header_cache[sub_sheet_name] = result.get("values", [[]])[0]

        headers = self.header_cache[sub_sheet_name]
        row_values = [""] * len(headers)
        for i, header in enumerate(headers):
            if header in row_data:
                row_values[i] = row_data[header]

        body = {"values": [row_values]}
        response = (
            service.spreadsheets()  # pylint: disable=no-member
            .values()
            .append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sub_sheet_name}!A1:Z",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )

        return response

    def batch_append_rows(self, sub_sheet_name, rows_data):
        """
        Appends multiple rows of data to a specified Google Sheets spreadsheet and sheet.

        Args:
            sub_sheet_name (str): The name of the sheet within the spreadsheet.
            rows_data (list): A list of dictionaries where keys are column headers and values are the data to be added.

        Returns:
            dict: The response from the Google Sheet API after appending the data.
        """
        access_token = self.get_access_token()
        creds = Credentials(access_token)
        service = build("sheets", "v4", credentials=creds)

        if sub_sheet_name not in self.header_cache:
            result = (
                service.spreadsheets()  # pylint: disable=no-member
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=f"{sub_sheet_name}!A1:Z1")
                .execute()
            )
            self.header_cache[sub_sheet_name] = result.get("values", [[]])[0]

        headers = self.header_cache[sub_sheet_name]
        all_row_values = []

        for row_data in rows_data:
            row_values = [""] * len(headers)
            for i, header in enumerate(headers):
                if header in row_data:
                    row_values[i] = row_data[header]
            all_row_values.append(row_values)

        body = {"values": all_row_values}
        response = (
            service.spreadsheets()  # pylint: disable=no-member
            .values()
            .append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sub_sheet_name}!A1:Z",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )

        return response


# Example usage:
# sheet_service = GoogleSheetService(
#     GOOGLE_CLOUD_REFRESH_TOKEN,
#     GOOGLE_CLOUD_CLIENT_ID,
#     GOOGLE_CLOUD_CLIENT_SECRET,
#     GOOGLE_SHEETS_SPREADSHEET_ID_BULLPEN_TG_BRIEF_ACCOUNTS
# )
# data = sheet_service.get_sheet_data("accounts_sheet")
