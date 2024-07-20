# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=logging-fstring-interpolation
# pylint: disable=line-too-long

import datetime
from google.cloud import bigquery
from ipulse_shared_core_ftredge.enums.enums_common_utils import NoticeLevel
from ipulse_shared_core_ftredge.utils_common import Notice


def create_bigquery_schema_from_json(json_schema):
    schema = []
    for field in json_schema:
        if "max_length" in field:
            schema.append(bigquery.SchemaField(field["name"], field["type"], mode=field["mode"], max_length=field["max_length"]))
        else:
            schema.append(bigquery.SchemaField(field["name"], field["type"], mode=field["mode"]))
    return schema


def update_check_with_schema_template(updates, schema, dt_ts_to_str=True, check_max_length=True):

    """Ensure Update dict corresponds to the config schema, ensuring proper formats and lengths."""
    valid_updates = {}
    notices=[] ### THIS IS TO AVOID LOGGING A WARNING RANDOMLY, INSTEAD GROUPPING FOR A GIVEN RUN

    # Process updates to conform to the schema
    for field in schema:
        field_name = field["name"]
        field_type = field["type"]
        mode = field["mode"]

        # Initialize notice to None at the start of each field processing
        notice = None

        if field_name in updates:
            value = updates[field_name]

            # Handle date and timestamp formatting

            # Validate and potentially convert date and timestamp fields
            if field_type == "DATE":
                value, notice = handle_date_fields(field_name, value, dt_ts_to_str)
            elif field_type == "TIMESTAMP":
                value, notice = handle_timestamp_fields(field_name, value, dt_ts_to_str)
            elif field_type in ["STRING", "INT64", "FLOAT64", "BOOL"]:
                value, notice = handle_type_conversion(field_type, field_name, value )

            if notice:
                notices.append(notice)

            # Check and handle max length restriction
            if check_max_length and "max_length" in field:
                value,notice = check_and_truncate_length(field_name, value, field["max_length"])
                if notice:
                    notices.append(notice)

            # Only add to the dictionary if value is not None or the field is required
            if value is not None or mode == "REQUIRED":
                valid_updates[field_name] = value

        elif mode == "REQUIRED":
            notice=Notice(level=NoticeLevel.WARNING_FIX_REQUIRED,
                             subject=field_name,
                             description=f"Required field '{field_name}' is missing in the updates.")

            notices.append(notice)

    return valid_updates, notices

def handle_date_fields(field_name, value, dt_ts_to_str):
    """Handles date fields, ensuring they are in the correct format and optionally converts them to string."""
    if isinstance(value, datetime.date):
        if dt_ts_to_str:
            return value.strftime("%Y-%m-%d"), None
        return value, None
    elif isinstance(value, str):
        try:
            parsed_date = datetime.datetime.strptime(value, "%Y-%m-%d").date()
            if dt_ts_to_str:
                return value, None
            return parsed_date, None
        except ValueError:
            return None, Notice(level=NoticeLevel.WARNING_FIX_REQUIRED,
                                                  subject=field_name,
                                                   description=f"Expected a DATE in YYYY-MM-DD format but got {value}.")
    else:
        return None, Notice(level=NoticeLevel.WARNING_FIX_REQUIRED,
                                              subject=field_name,
                                              description= f"Expected a DATE or YYYY-MM-DD str format but got {value} of type {type(value).__name__}.")


def handle_timestamp_fields(field_name, value, dt_ts_to_str):
    """Handles timestamp fields, ensuring they are in the correct format and optionally converts them to ISO format string."""
    if isinstance(value, datetime.datetime):
        if dt_ts_to_str:
            return value.isoformat(), None
        return value, None
    elif isinstance(value, str):
        try:
            parsed_datetime = datetime.datetime.fromisoformat(value)
            if dt_ts_to_str:
                return value, None
            return parsed_datetime, None
        except ValueError:
            return None, Notice(level=NoticeLevel.WARNING_FIX_REQUIRED,
                                                  subject=field_name,
                                                  description= f"Expected ISO format TIMESTAMP but got {value}.")
    else:
        return None, Notice(level=NoticeLevel.WARNING_FIX_REQUIRED,
                                              subject=field_name,
                                              description= f"Expected ISO format TIMESTAMP but got {value} of type {type(value).__name__}.")


def check_and_truncate_length(field_name, value, max_length):
    """Checks and truncates the length of string fields if they exceed the max length."""
    if isinstance(value, str) and len(value) > max_length:
        return value[:max_length], Notice(level=NoticeLevel.WARNING_FIX_RECOMMENDED,
                            subject= field_name,
                             description= f"Field exceeds max length: {len(value)}/{max_length}. Truncating.")

    return value, None



def handle_type_conversion(field_type, field_name, value):
    if field_type == "STRING" and not isinstance(value, str):
        return str(value), Notice(level=NoticeLevel.WARNING_REVIEW_RECOMMENDED,
                             subject=field_name,
                             description= f"Expected STRING but got {value} of type {type(value).__name__}.")

    if field_type == "INT64" and not isinstance(value, int):
        try:
            return int(value), None
        except ValueError:
            return None, Notice(level=NoticeLevel.WARNING_FIX_REQUIRED,
                                                subject= field_name,
                                                description=f"Expected INTEGER, but got {value} of type {type(value).__name__}.")
    if field_type == "FLOAT64" and not isinstance(value, float):
        try:
            return float(value), None
        except ValueError:
            return None, Notice(level=NoticeLevel.WARNING_FIX_REQUIRED, 
                                                subject=field_name,
                                                description=f"Expected FLOAT, but got  {value} of type {type(value).__name__}.")
    if field_type == "BOOL" and not isinstance(value, bool):
        return bool(value), Notice(level=NoticeLevel.WARNING_REVIEW_RECOMMENDED, 
                                                subject=field_name,
                                                description=f"Expected BOOL, but got  {value}. Converting as {bool(value)}.")

    return value, None
