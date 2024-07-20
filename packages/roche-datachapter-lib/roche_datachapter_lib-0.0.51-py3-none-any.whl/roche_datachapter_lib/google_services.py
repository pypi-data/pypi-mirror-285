"""Google Services Adapter module"""
import time
from typing import List, Dict, Any
from os import environ, path as os_path
from io import BytesIO
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource, HttpRequest
import pandas as pd
from .result_type import ResultType
from .google_services_enums import ValueInputOption, ValueRenderOption

# Considerar gspread como biblioteca a implementar para las funcionalidades que requieran interacción con google sheets

SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']
ENV_VAR_NAMES = ["GOOGLE_TOKEN_PATH", "GOOGLE_CREDENTIALS_PATH"]

for env_var_name in ENV_VAR_NAMES:
    value = environ.get(env_var_name)
    if value is not None:
        globals()[env_var_name] = value
    else:
        raise EnvironmentError(
            f'Environment variable "{env_var_name}" is NOT set')


class GoogleServices():
    """Decorator for Google Services"""

    @classmethod
    def retry_request(cls, func, *args, retries=3, delay=10, **kwargs):
        """Retries a function call in case of TimeoutError or HttpError"""
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except (TimeoutError, HttpError) as e:
                print(
                    f"Error en intento {attempt + 1}/{retries} - {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    raise

    @classmethod
    def __get_google_credentials__(cls):
        creds = None
        try:
            if os_path.exists(GOOGLE_TOKEN_PATH):  # pylint:disable=undefined-variable
                creds = Credentials.from_authorized_user_file(
                    GOOGLE_TOKEN_PATH, SCOPES)  # pylint:disable=undefined-variable
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        GOOGLE_CREDENTIALS_PATH, SCOPES)  # pylint:disable=undefined-variable
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(GOOGLE_TOKEN_PATH, 'w', encoding="utf-8") as token:  # pylint:disable=undefined-variable
                    token.write(creds.to_json())
        except Exception as err:
            raise ValueError(
                f'Google Authentication Error {err}') from err
        return creds

    @classmethod
    def __standarized_dataframe__(cls, p_df: pd.DataFrame) -> pd.DataFrame:
        p_df.columns = p_df.columns.astype(str)
        p_df.columns = p_df.columns.str.lower()
        p_df.columns = p_df.columns.str.strip()
        p_df = p_df.dropna(how='all')
        return p_df

    @classmethod
    def get_spreadsheet_values(cls, spreadsheet_id: str, range_name: str, render_value_option: ValueRenderOption = ValueRenderOption.FORMATTED_VALUE) -> List[List[Any]]:
        """Lee datos de una Google spreadsheet especifica y lo devuelve como matriz.
        Si el rango no tiene contenido devuelve una lista vacía"""
        def fetch_sheet_values():
            service = build(
                'sheets', 'v4', credentials=cls.__get_google_credentials__())
            if hasattr(service, 'spreadsheets'):
                sheet: Resource = service.spreadsheets()
                result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                            range=range_name, valueRenderOption=render_value_option.value).execute()
                return result.get('values', [])
            return []
        try:
            return cls.retry_request(fetch_sheet_values)
        except Exception as err:
            raise ConnectionError('Error al leer datos de Google Sheets: ', err) from err

    @classmethod
    def update_spreadsheet_values(cls, spreadsheet_id: str, range_name: str, values: List[List[Any]], value_input_option: ValueInputOption = ValueInputOption.USER_ENTERED) -> int:
        """Actualiza datos en un rango especifico de una Google spreadsheet.
        Devuelve la cantidad de celdas actualizadas."""
        def update_sheet_values():
            service = build(
                'sheets', 'v4', credentials=cls.__get_google_credentials__())
            if hasattr(service, 'spreadsheets'):
                sheet: Resource = service.spreadsheets()
                result: dict = sheet.values().update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    body={
                        "values": values
                    },
                    valueInputOption=value_input_option.value
                ).execute()
                return result.get('updatedCells', 0)
            return 0
        try:
            return cls.retry_request(update_sheet_values)
        except Exception as err:
            raise ConnectionError('Error al actualizar el contenido de la hoja de Google Sheets: ', err) from err

    @classmethod
    def read_gsheet_data(cls, spreadsheet_id: str, range_name: str, result_type: ResultType = ResultType.JSON_LIST, render_value_option: ValueRenderOption = ValueRenderOption.FORMATTED_VALUE) -> pd.DataFrame | List[Dict[str, Any]]:
        """Lee datos de una Google spreadsheet especifica y lo devuelve como pandas DataFrame o JSON List"""
        df = pd.DataFrame()
        values = cls.get_spreadsheet_values(
            spreadsheet_id, range_name, render_value_option)
        if values:
            headers = values[0]
            data = values[1:]
            df = cls.__standarized_dataframe__(
                pd.DataFrame(data, columns=headers))
        if result_type == ResultType.JSON_LIST:
            return df.to_dict(orient='records')
        return df

    @classmethod
    def write_gsheet_data(cls, spreadsheet_id: str, range_name: str, values_as_df: pd.DataFrame = pd.DataFrame()) -> int:
        """Escribe datos en una Google spreadsheet especifica.
        Devuelve la cantidad de celdas escritas."""
        values = [values_as_df.columns.tolist()] + values_as_df.values.tolist()
        return cls.update_spreadsheet_values(spreadsheet_id, range_name, values)

    @classmethod
    def clear_gsheet_and_keep_format(cls, spreadsheet_id: str, range_name: str) -> bool:
        """Borra el contenido de las celdas pero mantiene el formato previo"""
        try:
            actual_values = cls.get_spreadsheet_values(
                spreadsheet_id, range_name)
            if actual_values:
                new_empty_values = [
                    ["" for _ in range(len(value))] for value in actual_values]
                updated_cells = cls.update_spreadsheet_values(
                    spreadsheet_id, range_name, new_empty_values)
                return sum(len(sublista) for sublista in actual_values) == updated_cells
        except Exception as err:
            raise ConnectionError(
                "Error al borrar el contenido de la hoja de Google Sheets manteniendo el formato: ", err) from err
        return False

    @classmethod
    def read_excel_data_from_google_drive(cls, file_id: str, sheet_name: str, output_data_type=None, result_type: ResultType = ResultType.JSON_LIST, skiprows=None) -> pd.DataFrame | List[Dict[str, Any]]:
        """Lee datos de un XLS o XSLX de Google Drive y lo devuelve como pandas DataFrame o JSON List"""
        df = pd.DataFrame()
        def fetch_excel_data():
            service: Resource = build(
                'drive', 'v3', credentials=cls.__get_google_credentials__())
            if hasattr(service, 'files'):
                request: HttpRequest = service.files().get_media(fileId=file_id)
                downloader = request.execute()
                with BytesIO(downloader) as f:
                    xls = pd.ExcelFile(f)
                    for sheet in xls.sheet_names:
                        if sheet.strip() == sheet_name:
                            df = cls.__standarized_dataframe__(
                                pd.read_excel(xls, sheet_name, dtype=output_data_type, skiprows=skiprows))
            return df # pylint:disable=used-before-assignment
        try:
            df = cls.retry_request(fetch_excel_data)
            if result_type == ResultType.JSON_LIST:
                return df.to_dict(orient='records')
            return df
        except Exception as err:
            raise ConnectionError(
                f'Error al leer datos en formato Excel desde Google Drive file id "{file_id}"') from err

    @classmethod
    def move_file(cls, file_id, new_folder_id) -> bool:
        """Mueve un archivo de Drive a una carpeta específica"""
        def move_drive_file():
            service: Resource = build(
                'drive', 'v3', credentials=cls.__get_google_credentials__())
            if hasattr(service, 'files'):
                file = service.files().get(fileId=file_id, fields='parents').execute()
                previous_parents = ",".join(file.get('parents'))
                file = service.files().update(fileId=file_id,
                                              addParents=new_folder_id,
                                              removeParents=previous_parents,
                                              fields='id, parents').execute()
            return True
        try:
            return cls.retry_request(move_drive_file)
        except Exception as err:
            raise ConnectionError(
                f'Error al mover el archivo "{file_id}" a la carpeta "{new_folder_id}"') from err

    @classmethod
    def read_directory_content_from_google_drive(cls, dir_id: str, mime_type_filter: str) -> pd.DataFrame | List[Dict[str, Any]]:
        """Lee el contenido de un directorio de Google drive y lo devuelve en JSON.
        Valores posibles para el parámetro mime_type_filter en https://developers.google.com/drive/api/guides/mime-types"""
        data_as_json: list = []
        def fetch_directory_content():
            service: Resource = build(
                'drive', 'v3', credentials=cls.__get_google_credentials__())
            if hasattr(service, 'files'):
                results = service.files().list(
                    q=f"'{dir_id}' in parents and trashed=false", fields="files(id, name, mimeType)", supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
                items = results.get('files', [])
                if items:
                    for item in items:
                        if item.get('mimeType') == mime_type_filter:
                            data_as_json.append(item)
            return data_as_json
        try:
            return cls.retry_request(fetch_directory_content)
        except Exception as err:
            raise ConnectionError(
                f'Error al leer el directorio "{dir_id}" de Google Drive') from err
        
    
    
    @classmethod
    def get_file_name_by_file_id(cls, file_id: str) -> str:
        """Obtiene el nombre de un archivo de Google Drive por su ID"""
        def fetch_file_name():
            service: Resource = build(
                'drive', 'v3', credentials=cls.__get_google_credentials__())
            if hasattr(service, 'files'):
                file = service.files().get(fileId=file_id, fields='name').execute()
                return file.get('name')
            return ''
        try:
            return cls.retry_request(fetch_file_name)
        except Exception as err:
            raise ConnectionError(
                f'Error al obtener el nombre del archivo "{file_id}" de Google Drive') from err
    
    @classmethod
    def upload_file_to_drive(cls, file_path: str, file_name: str, folder_id: str, mime_type: str) -> str:
        """Sube un archivo .xlsx a una carpeta especifica en Google Drive y devuelve el nombre del archivo"""
        def upload_file():
            service: Resource = build(
                'drive', 'v3', credentials=cls.__get_google_credentials__())
            if hasattr(service, 'files'):
                file_metadata = {
                    'name': file_name,
                    'parents': [folder_id]
                }
                media = MediaFileUpload(file_path, mimetype=mime_type)
                file = service.files().create(body=file_metadata,
                                              media_body=media,
                                              fields='id').execute()
                return file.get('id')
        try:
            return cls.retry_request(upload_file)
        except Exception as err:
            raise ConnectionError(
                f'Error al subir el archivo "{file_name}" a la carpeta "{folder_id}" de Google Drive') from err
