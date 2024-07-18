from airflow.hooks.base_hook import BaseHook
from spswarehouse.powerschool.student_passwords import PSStudentPassword as BasePS

default_conn_id = 'powerschool_ui'

class PSStudentPassword(BasePS):
    """
    Wrapper class for the spswarehouse PSStudentPassword class that
    handles retrieving the host from an Airflow connection
    """
    
    def __init__(self, download_location=',', conn_id=default_conn_id, wait_time=30):
        """
        Parameters:
        download_location: The folder that you want to download files to.
        conn_id: The name of a connection in your Airflow instance that
            contains the login details for your PS instance.
        """
        
        powerschool_conn = BaseHook.get_connection(conn_id)
        host = powerschool_conn.host
        
        super().__init__(
            host=host,
            # Airflow must be headless or it crashes
            headless=True,
            wait_time=wait_time,
            download_location=download_location
        )