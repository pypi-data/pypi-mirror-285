from airflow.hooks.base_hook import BaseHook
from spswarehouse.powerschool.powerschool import PowerSchool as BasePS

default_conn_id = 'powerschool_ui'

class PowerSchool(BasePS):
    """
    Wrapper class for the spswarehouse PowerSchool class that
    handles retrieving credentials from Airflow connection
    """
    
    def __init__(self, download_location='.', conn_id=default_conn_id):
        """
        Parameters:
        download_location: The folder that you want to download files to.
        conn_id: The name of a connection in your Airflow instance that
            contains the login details for your PS instance.
            You must have filled in the host, login, and password fields.
        """
        
        powerschool_conn = BaseHook.get_connection(conn_id)
        host = powerschool_conn.host
        username = powerschool_conn.login
        password = powerschool_conn.password
        
        super().__init__(
            username=username,
            password=password,
            host=host,
            headless=True,
            download_location=download_location
        )