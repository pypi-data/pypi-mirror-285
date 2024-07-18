"""Tests for RDI Redshift connection"""
from roche_datachapter_lib.db_config import DB_CONFIG

result = DB_CONFIG.execute_custom_select_query(
    "SELECT * FROM gtm_latam_arg.stg_oceo.oceo_omuser_latest", "rdi_latam_ar")
print(result)
