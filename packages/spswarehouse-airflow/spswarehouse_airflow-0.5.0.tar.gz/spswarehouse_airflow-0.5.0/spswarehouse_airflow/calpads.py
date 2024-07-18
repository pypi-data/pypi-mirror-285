from airflow.hooks.base_hook import BaseHook
from spswarehouse.calpads.calpads import CALPADS as BaseCalpads

default_conn_id = 'calpads_ui'

class CALPADS(BaseCalpads):
    """
    Wrapper class for the spswarehouse CALPADS class that
    handles retrieving credentials from Airflow connection
    """
    
    def __init__(self, download_location='./', conn_id=default_conn_id):
        """
        Parameters:
        download_location: The file path to download files too
        conn_id: The name of a connection in your Airflow instance that
            contains the login details for CALPADS.
            You must have filled in the host, login, and password fields.
        """
        
        calpads_conn = BaseHook.get_connection(conn_id)
        host = calpads_conn.host
        username = calpads_conn.login
        password = calpads_conn.password
        
        super().__init__(
            username=username,
            password=password,
            host=host,
            download_location=download_location,
            headless=True,
        )