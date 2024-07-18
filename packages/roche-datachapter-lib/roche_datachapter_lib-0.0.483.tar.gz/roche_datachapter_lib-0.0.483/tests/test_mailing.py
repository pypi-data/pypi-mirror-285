"""Test module for mailing module."""
import os
import pandas as pd
from roche_datachapter_lib.db_config import DB_CONFIG
from roche_datachapter_lib.query_manager import QueryManager
from roche_datachapter_lib.result_type import ResultType
from roche_datachapter_lib.excel_generator import ExcelFile
from roche_datachapter_lib.email_service import EmailService, AttachmentFile, EmailDestination

QUERIES_DIR = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'queries')
QUERY_MANAGER = QueryManager(QUERIES_DIR)


query_rdi = QUERY_MANAGER.get_query('ej_rdi.sql')
df_usuarios_rdi = DB_CONFIG.execute_custom_select_query(
    query_rdi, "rdi_latam_ar", result_set_as=ResultType.PANDAS_DATA_FRAME)
df_usuarios_rdi['bookmark_dts'] = pd.to_datetime(
    df_usuarios_rdi['bookmark_dts']).dt.strftime('%Y-%m-%d')
df_usuarios_rdi['load_dts'] = pd.to_datetime(
    df_usuarios_rdi['load_dts']).dt.strftime('%Y-%m-%d')

query_rexis = QUERY_MANAGER.get_query('ej_rexis.sql')
df_usuarios_rexis = DB_CONFIG.execute_custom_select_query(
    query_rexis, "rexis_sales", result_set_as=ResultType.PANDAS_DATA_FRAME)


destinatario = 'lucas.frias@roche.com, uciel.bustamante@contractors.roche.com'
subject = 'Test email from roche_datachapter_lib'
body = 'Esto es una prueba de envío de email desde roche_datachapter_lib'

# get current file path directory
current_file_path_dir = os.path.dirname(os.path.realpath(__file__))
file_name_rdi = 'query_rdi.xlsx'
excel_file_rdi = ExcelFile(os.path.join(current_file_path_dir, file_name_rdi))
excel_file_rdi.append_sheet_from_df(df_usuarios_rdi)
excel_file_rdi.save()

file_name_rexis = 'query_rexis.xlsx'
excel_file_rexis = ExcelFile(os.path.join(
    current_file_path_dir, file_name_rexis))
excel_file_rexis.append_sheet_from_df(df_usuarios_rexis)
excel_file_rexis.save()

file_name_merge = 'rdi_rexis.xlsx'
excel_file_merge = ExcelFile(os.path.join(
    current_file_path_dir, file_name_merge))
excel_file_merge.append_sheet_from_df(df_usuarios_rdi, 'rdi')
excel_file_merge.append_sheet_from_df(df_usuarios_rexis, 'rexis')
excel_file_merge.save()

destinatarios = EmailDestination(
    ['lucas.frias@roche.com', 'uciel.bustamante@contractors.roche.com'])
attachments = [AttachmentFile(excel_file_rdi.get_destination_path()), AttachmentFile(
    excel_file_rexis.get_destination_path()), AttachmentFile(excel_file_merge.get_destination_path())]


EmailService().send_email(destinatarios, subject, body, attachments)
