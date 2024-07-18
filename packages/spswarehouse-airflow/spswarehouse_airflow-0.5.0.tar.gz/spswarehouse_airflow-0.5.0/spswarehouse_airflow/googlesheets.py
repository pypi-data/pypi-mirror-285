import gspread
import os
import pickle

from airflow.providers.google.common.hooks.base_google import GoogleBaseHook

# from .credentials import google_config

# from oauth2client.service_account import ServiceAccountCredentials

default_google_conn_id = 'google_cloud_default'

# def get_google_service_account_email():
#     """
#     Returns the service account email to share spreadsheets with.
#     """
#     return google_config['service-account']['client_email']

def initialize_credentials(conn_id=default_google_conn_id):
    """
    initialize_credentials: -> oauth2client.service_account.ServiceAccountCredentials

    Returns credentials that allows you to access your Google Drive &
    Sheets using the Google Sheets API.

    You still need to share spreadsheets with the service account email.
    """
    
    credentials = GoogleBaseHook(conn_id).get_credentials()
    
#     credentials = ServiceAccountCredentials.from_json_keyfile_name(
#         google_conn[''],
#         scopes=google_conn['scopes'],
#     )

    return credentials

def create_sheets(conn_id=default_google_conn_id, credentials=None):
    """
    create_engine:

    Sets up Google Sheets API access using credentials (see above).
    """
    if credentials is None:
        credentials = initialize_credentials(conn_id)
    client = gspread.authorize(credentials)
    return client

# Set up credentials
# credentials = initialize_credentials()

# This is a wrapper for gspread.Client
# GoogleSheets = None if credentials is None else create_client(credentials)
