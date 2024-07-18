import os
import pickle

# from .credentials import google_config

from googleapiclient.discovery import build

from airflow.providers.google.common.hooks.base_google import GoogleBaseHook

default_google_conn_id = 'google_cloud_default'

# def get_google_service_account_email():
#     """
#     Returns the service account email to share slides with.
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
    return credentials

def create_slides(conn_id=default_google_conn_id, credentials=None):
    """
    create_engine:

    Sets up Google Drive API access using credentials (see above).
    """
    if credentials is None:
        credentials = initialize_credentials(conn_id)
    slides = build('slides', 'v1', credentials=credentials)
    return slides

# Set up credentials
# credentials = initialize_credentials()

# This is a wrapper for gspread.Client
# GoogleSlides = None if credentials is None else create_client(credentials)
