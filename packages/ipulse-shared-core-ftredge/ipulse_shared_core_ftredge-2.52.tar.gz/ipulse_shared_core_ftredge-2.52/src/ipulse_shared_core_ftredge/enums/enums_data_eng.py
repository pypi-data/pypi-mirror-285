# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
from enum import Enum

class SourcingTriggerType(Enum):
    HISTORIC_MANUAL = "historic_manual"
    LIVE_SCHEDULED = "live_scheduled"
    ADHOC_MANUAL = "adhoc_manual"
    ADHOC_SCHEDULED = "adhoc_scheduled"
    LIVE_MANUAL = "live_manual"

class SourcingPipelineType(Enum):
    LOCAL_GET_API_TO_GCS = "local_get_api_to_gcs"
    LOCAL_GET_API_INMEMORY = "local_get_api_inmemory"
    LOCAL_GET_API_TO_LOCAL_FILE = "local_get_api_to_local_file"
    LOCAL_DOWNLOAD_WEB_FILE_TO_LOCAL = "local_download_web_file_to_local"
    LOCAL_DOWNLOAD_WEB_FILE_TO_GCS = "local_download_web_file_to_gcs"
    CLOUD_GET_API_TO_GCS = "cloud_get_api_to_gcs"
    CLOUD_GET_API_INMEMORY = "cloud_get_api_inmemory"

class DWEventTriggerType(Enum):
    GCS_UPLOAD_TRIGGER_CF = "gcs_upload_trigger_cf"
    HTTP_TRIGGER_CF_FOR_GCS_FILE = "http_trigger_cf_for_gcs_file"
    PUBSUB_TRIGGER_CF_FOR_GCS_FILE = "pubsub_trigger_cf_for_gcs_file"
    LOCAL_SCRIPT_FOR_GCS_FILE = "local_script_for_gcs_file"
    INSIDE_SOURCING_FUNCTION = "inside_sourcing_function"

class DWEvent(Enum):
    INSERT_NOREPLACE_1O_NT = "insert_noreplace_1o_nt"
    MERGE_NOREPLACE_NO_1T = "merge_noreplace_no_1t"
    MERGE_NOREPLACE_NO_NT = "merge_noreplace_no_nt"
    INSERT_NOREPLACE_1O_1T = "insert_noreplace_1o_1t"
    MERGE_NOREPLACE_1O_NT = "merge_noreplace_1o_nt"
    INSERT_REPLACE_1O_1T = "insert_replace_1o_1t"
    INSERT_REPLACE_1O_NT = "insert_replace_1o_nt"
    MERGE_REPLACE_NO_NT = "merge_replace_no_nt"
    MERGE_REPLACE_1O_NT = "merge_replace_1o_nt"
    MERGE_REPLACE_NO_1T = "merge_replace_no_1t"
    DELETE_1O_1T = "delete_1o_1t"
    DELETE_1O_NT = "delete_1o_nt"
    DELETE_NO_1T = "delete_no_1t"
    DELETE_NO_NT = "delete_no_nt"