"""Clase para peticiones de appsheet con metodos para obtener, editar y crear registros en la base de datos de appshet"""
import requests
from .google_services import GoogleServices


class AppsheetService():
    """Servicio para invocar API de Appsheet"""

    def __init__(self, application_id: str, application_access_key: str):
        self.application_id = application_id
        self.application_access_key = application_access_key

    def get_table_data(self, table_name: str, selector=None):
        """Obtiene los datos de una tabla de appsheet de una aplicación"""

        url = f"https://api.appsheet.com/api/v2/apps/{
            self.application_id}/tables/{table_name}/Action"
        headers = {
            "Content-Type": "application/json",
            "muteHttpExceptions": "true"
        }
        json_body = {
            "Action": "Find",
            "Properties": {
                "Locale": "en-US",
                "Timezone": "Pacific Standard Time",
                selector if selector else "": ""
            },
            "Rows": []
        }
        params = {
            'applicationAccessKey': self.application_access_key
        }

        def make_request_get_data():
            """Funcion encapsulada para reintentar la peticion en caso de error"""
            response = requests.post(                                   # pylint: disable= missing-timeout
                url, headers=headers, params=params, json=json_body, verify=False)
            response.raise_for_status()
            return response
        try:
            response = GoogleServices.retry_request(make_request_get_data)
            return response.json()
        except Exception as error:  # pylint: disable=broad-exception-caught
            print(f"Error al obtener datos de la tabla: {error}")
            return None

    def add_registers_to_table(self, rows_list, table_name):
        """Agrega registros a una tabla de appsheet de una aplicación"""
        url = f"https://api.appsheet.com/api/v2/apps/{
            self.application_id}/tables/{table_name}/Action"
        headers = {
            "Content-Type": "application/json",
            "muteHttpExceptions": "true"
        }
        json_body = {
            "Action": "Add",
            "Properties": {
                "Locale": "en-US",
                "Timezone": "Pacific Standard Time"
            },
            "Rows": rows_list
        }
        params = {
            'applicationAccessKey': self.application_access_key
        }

        def make_request_add_data():
            """Funcion encapsulada para reintentar la peticion en caso de error"""
            response = requests.post(                                   # pylint: disable= missing-timeout
                url, headers=headers, params=params, json=json_body, verify=False)
            response.raise_for_status()
            return response
        try:
            response = GoogleServices.retry_request(make_request_add_data)
            return response.json()
        except Exception as error:
            raise TimeoutError(
                f"Error al agregar registros a la tabla: {error}") from error
