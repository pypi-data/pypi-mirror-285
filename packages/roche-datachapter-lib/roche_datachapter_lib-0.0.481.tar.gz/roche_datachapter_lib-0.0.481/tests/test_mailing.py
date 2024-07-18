"""Test module for mailing module."""
import pandas as pd
from roche_datachapter_lib.db_config import DB_CONFIG
from roche_datachapter_lib.result_type import ResultType
from roche_datachapter_lib.email_service import EmailService


query="SELECT * FROM gtm_latam_arg.stg_oceo.oceo_omuser_latest"
bind="rdi_latam_ar"
df = DB_CONFIG.execute_custom_select_query(
            query, bind, result_set_as=ResultType.PANDAS_DATA_FRAME)
df['bookmark_dts'] = pd.to_datetime(df['bookmark_dts']).dt.strftime('%Y-%m-%d')
df['load_dts'] = pd.to_datetime(df['load_dts']).dt.strftime('%Y-%m-%d')

file_name='prueba_roche_datachapter_lib'
destinatario='lucas.frias@roche.com, uciel.bustamante@contractors.roche.com'
subject='Test email from roche_datachapter_lib'
body='Esto es una prueba de envío de email desde roche_datachapter_lib'


EmailService().send_email(destinatario, subject, body, df, file_name)