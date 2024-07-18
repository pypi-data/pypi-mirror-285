from .powerschool import PowerSchool
from spswarehouse.powerschool.powerschool_calpads import PowerSchoolCALPADS as BasePSCalpads
from spswarehouse.powerschool.powerschool_calpads import (
    swap_value_in_column_of_calpads_file,
    remove_sela_records_beginning_before_report_start_date
)

default_conn_id = 'powerschool_ca_ui'

class PowerSchoolCALPADS(PowerSchool, BasePSCalpads):
    """
    Wrapper class for the spswarehouse PowerSchoolCALPADS class that
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
        
        super().__init__(download_location, conn_id)