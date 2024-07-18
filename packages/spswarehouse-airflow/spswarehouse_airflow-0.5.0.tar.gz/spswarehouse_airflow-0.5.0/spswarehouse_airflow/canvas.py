from airflow.hooks.base_hook import BaseHook
from spswarehouse.canvas import CanvasClient

default_canvas_conn_id = 'canvas_api'

def create_canvas(conn_id=default_canvas_conn_id, config=None):
    if config is None:
        canvas_conn = BaseHook.get_connection(conn_id)
        config = {
            "host": canvas_conn.host,
            "api_token": canvas_conn.password,
        }
    
    return CanvasClient(config=config)
