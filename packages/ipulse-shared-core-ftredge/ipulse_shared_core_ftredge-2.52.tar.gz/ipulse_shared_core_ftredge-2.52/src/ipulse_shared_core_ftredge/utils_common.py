# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=logging-fstring-interpolation
# pylint: disable=line-too-long
# pylint: disable=missing-class-docstring
import traceback
import json
import uuid
from datetime import datetime, timezone
from contextlib import contextmanager
from typing import List
from google.cloud import logging as cloudlogging
from ipulse_shared_core_ftredge.enums.enums_common_utils import NoticeLevel, NoticeManagerCategory, NoticeStatus
from ipulse_shared_core_ftredge.utils_gcp import write_json_to_gcs


# ["data_import","data_quality", "data_processing","data_general","data_persistance","metadata_quality", "metadata_processing", "metadata_persistance","metadata_general"]

class Notice:
    MAX_TRACEBACK_LINES = 14  # Define the maximum number of traceback lines to include
    def __init__(self, level: NoticeLevel, start_context: str = None, notice_manager_id: str = None,
                 e: Exception = None, e_type: str = None, e_message: str = None, e_traceback: str = None,
                 subject: str = None, description: str = None, context: str = None,
                 notice_status: NoticeStatus = NoticeStatus.OPEN):
        if e is not None:
            e_type = type(e).__name__ if e_type is None else e_type
            e_message = str(e) if e_message is None else e_message
            e_traceback = traceback.format_exc() if e_traceback is None else e_traceback
        elif e_traceback is None and (e_type or e_message):
            e_traceback = traceback.format_exc()

        self.level = level
        self.subject = subject
        self.description = description
        self._start_context = start_context
        self._context = context
        self.notice_manager_id = notice_manager_id
        self.exception_type = e_type
        self.exception_message = e_message
        self.exception_traceback = self._format_traceback(e_traceback,e_message)
        self.notice_status = notice_status
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def _format_traceback(self, e_traceback, e_message):
        if not e_traceback or e_traceback == 'None\n':
            return None

        traceback_lines = e_traceback.splitlines()
        
        # Remove lines that are part of the exception message if they are present in traceback
        message_lines = e_message.splitlines() if e_message else []
        if message_lines:
            for message_line in message_lines:
                if message_line in traceback_lines:
                    traceback_lines.remove(message_line)

        # Filter out lines from third-party libraries (like site-packages)
        filtered_lines = [line for line in traceback_lines if "site-packages" not in line]
        
        # If filtering results in too few lines, revert to original traceback
        if len(filtered_lines) < 2:
            filtered_lines = traceback_lines

        # Combine standalone bracket lines with previous or next lines
        combined_lines = []
        for line in filtered_lines:
            if line.strip() in {"(", ")", "{", "}", "[", "]"} and combined_lines:
                combined_lines[-1] += " " + line.strip()
            else:
                combined_lines.append(line)

        # Determine the number of lines to keep from the start and end
        keep_lines_start = min(self.MAX_TRACEBACK_LINES // 2, len(combined_lines))
        keep_lines_end = min(self.MAX_TRACEBACK_LINES // 2, len(combined_lines) - keep_lines_start)

        if len(combined_lines) > self.MAX_TRACEBACK_LINES:
            # Include the first few and last few lines, and an indicator of truncation
            formatted_traceback = '\n'.join(
                combined_lines[:keep_lines_start] + 
                ['... (truncated) ...'] + 
                combined_lines[-keep_lines_end:]
            )
        else:
            formatted_traceback = '\n'.join(combined_lines)

        return formatted_traceback 

    @property
    def start_context(self):
        return self._start_context

    @start_context.setter
    def start_context(self, value):
        self._start_context = value

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        self._context = value

    def to_dict(self):
        return {
            "start_context": self.start_context,
            "context": self.context,
            "level_code": self.level.value,
            "level_name": self.level.name,
            "subject": self.subject,
            "description": self.description,
            "exception_type": self.exception_type,
            "exception_message": self.exception_message,
            "exception_traceback": self.exception_traceback,
            "notice_status": self.notice_status.value,
            "notice_manager_id": self.notice_manager_id,
            "timestamp": self.timestamp
        }

class NoticesManager:
    ERROR_CODE_START_VALUE = NoticeLevel.ERROR.value
    WARNING_CODE_START_VALUE = NoticeLevel.WARNING.value
    SUCCESS_CODE_START_VALUE = NoticeLevel.SUCCESS.value

    def __init__(self, start_context: str, category: NoticeManagerCategory = NoticeManagerCategory.NOTICES, logger_name=None):
        self._id = str(uuid.uuid4())
        self._notices = []
        self._early_stop = False
        self._errors_count = 0
        self._warnings_count = 0
        self._successes_count = 0
        self._level_counts = {level.name: 0 for level in NoticeLevel}
        self._start_context = start_context
        self._context_stack = []
        self._category = category.value
        self._logger = self._initialize_logger(logger_name)

    def _initialize_logger(self, logger_name):
        if logger_name:
            logging_client = cloudlogging.Client()
            return logging_client.logger(logger_name)
        return None


    @contextmanager
    def context(self, context):
        self.push_context(context)
        try:
            yield
        finally:
            self.pop_context()

    def push_context(self, context):
        self._context_stack.append(context)

    def pop_context(self):
        if self._context_stack:
            self._context_stack.pop()

    @property
    def current_context(self):
        return " >> ".join(self._context_stack)

    @property
    def start_context(self):
        return self._start_context

    @property
    def id(self):
        return self._id

    @property
    def early_stop(self):
        return self._early_stop

    def set_early_stop(self, max_errors_tolerance:int, create_error_notice=True,pop_context=False):
        self.early_stop = True
        if create_error_notice:
            if pop_context:
                self.pop_context()
            self.add_notice(Notice(level=NoticeLevel.ERROR,
                    subject="EARLY_STOP",
                    description=f"Total MAX_ERRORS_TOLERANCE of {max_errors_tolerance} has been reached."))

    def reset_early_stop(self):
        self._early_stop = False

    def get_early_stop(self):
        return self._early_stop

    def add_notice(self, notice: Notice):
        if (self._category == NoticeManagerCategory.SUCCESSES.value and notice.level != NoticeLevel.SUCCESS) or \
           (self._category == NoticeManagerCategory.WARN_ERRS.value and notice.level.value < self.WARNING_CODE_START_VALUE):
            raise ValueError(f"Invalid notice level {notice.level.name} for category {self._category}")
        notice.start_context = self.start_context
        notice.context = self.current_context
        notice.notice_manager_id = self.id
        notice_dict = notice.to_dict()
        self._notices.append(notice_dict)
        self._update_counts(notice_dict)

        if self._logger:
            if notice.level.value >= self.WARNING_CODE_START_VALUE:
                self._logger.log_struct(notice_dict, severity="WARNING")
            else:
                self._logger.log_struct(notice_dict, severity="INFO")

    def add_notices(self, notices: List[Notice]):
        for notice in notices:
            self.add_notice(notice)

    def clear_notices_and_counts(self):
        self._notices = []
        self._errors_count = 0
        self._warnings_count = 0
        self._successes_count = 0
        self._level_counts = {level.name: 0 for level in NoticeLevel}

    def clear_notices(self):
        self._notices = []

    def get_all_notices(self):
        return self._notices

    def get_notices_for_level(self, level: NoticeLevel):
        return [notice for notice in self._notices if notice["level_code"] == level.value]

    def get_notices_by_str_in_context(self, context_substring: str):
        return [
            notice for notice in self._notices
            if context_substring in notice["context"]
        ]
    
    def contains_errors(self):
        return self._errors_count > 0

    def count_errors(self):
        return self._errors_count

    def contains_warnings_or_errors(self):
        return self._warnings_count > 0 or self._errors_count > 0

    def count_warnings_and_errors(self):
        return self._warnings_count + self._errors_count

    def count_warnings(self):
        return self._warnings_count

    def count_successes(self):
        return self._successes_count

    def count_all_notices(self):
        return len(self._notices)

    def count_notices_by_level(self, level: NoticeLevel):
        return self._level_counts.get(level.name, 0)

    def _count_notices(self, context_substring: str, exact_match=False, level_code_min=None, level_code_max=None):
        return sum(
            1 for notice in self._notices
            if (notice["context"] == context_substring if exact_match else context_substring in notice["context"]) and
               (level_code_min is None or notice["level_code"] >= level_code_min) and
               (level_code_max is None or notice["level_code"] <= level_code_max)
        )

    def count_notices_for_current_context(self):
        return self._count_notices(self.current_context, exact_match=True)

    def count_notices_for_current_and_nested_contexts(self):
        return self._count_notices(self.current_context)

    def count_notices_by_level_for_current_context(self, level: NoticeLevel):
        return self._count_notices(self.current_context, exact_match=True, level_code_min=level.value, level_code_max=level.value)

    def count_notices_by_level_for_current_and_nested_contexts(self, level: NoticeLevel):
        return self._count_notices(self.current_context, level_code_min=level.value, level_code_max=level.value)

    def count_errors_for_current_context(self):
        return self._count_notices(self.current_context, exact_match=True, level_code_min=self.ERROR_CODE_START_VALUE)

    def count_errors_for_current_and_nested_contexts(self):
        return self._count_notices(self.current_context, level_code_min=self.ERROR_CODE_START_VALUE)

    def count_warnings_and_errors_for_current_context(self):
        return self._count_notices(self.current_context, exact_match=True, level_code_min=self.WARNING_CODE_START_VALUE)

    def count_warnings_and_errors_for_current_and_nested_contexts(self):
        return self._count_notices(self.current_context, level_code_min=self.WARNING_CODE_START_VALUE)

    def count_warnings_for_current_context(self):
        return self._count_notices(self.current_context, exact_match=True, level_code_min=self.WARNING_CODE_START_VALUE, level_code_max=self.ERROR_CODE_START_VALUE - 1)

    def count_warnings_for_current_and_nested_contexts(self):
        return self._count_notices(self.current_context, level_code_min=self.WARNING_CODE_START_VALUE, level_code_max=self.ERROR_CODE_START_VALUE - 1)

    def count_successes_for_current_context(self):
        return self._count_notices(self.current_context, exact_match=True, level_code_min=self.SUCCESS_CODE_START_VALUE, level_code_max=self.SUCCESS_CODE_START_VALUE)

    def count_successes_for_current_and_nested_contexts(self):
        return self._count_notices(self.current_context, level_code_min=self.SUCCESS_CODE_START_VALUE, level_code_max=self.SUCCESS_CODE_START_VALUE)

    def export_notices_to_gcs_file(self, bucket_name, storage_client, file_prefix=None, file_name=None, top_level_context=None, save_locally=False, local_path=None, logger=None, max_retries=2):
        def log_message(message):
            if logger:
                logger.info(message)

        def log_error(message, exc_info=False):
            if logger:
                logger.error(message, exc_info=exc_info)

        if not file_prefix:
            file_prefix = self._category
        if not file_name:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            if top_level_context:
                file_name = f"{file_prefix}_{timestamp}_{top_level_context}_len{len(self._notices)}.json"
            else:
                file_name = f"{file_prefix}_{timestamp}_len{len(self._notices)}.json"

        result=None
        try:
            result= write_json_to_gcs(
                bucket_name=bucket_name,
                storage_client=storage_client,
                data=self._notices,
                file_name=file_name,
                save_locally=save_locally,
                local_path=local_path,
                logger=logger,
                max_retries=max_retries,
                overwrite=True
            )
            log_message(f"{file_prefix} successfully saved (ovewritten={result.get("ovewritten")}) to GCS at {result.get("gcs_path")} and locally at {result.get("local_path")}.")
        except Exception as e:
            log_error(f"Failed at export_notices_to_gcs_file for {file_prefix} for file {file_name} to bucket {bucket_name}: {type(e).__name__} - {str(e)}")

        return result

    def import_notices_from_json(self, json_or_file, logger=None):
        def log_message(message):
            if logger:
                logger.info(message)

        def log_warning(message, exc_info=False):
            if logger:
                logger.warning(message, exc_info=exc_info)

        try:
            if isinstance(json_or_file, str):  # Load from string
                imported_notices = json.loads(json_or_file)
            elif hasattr(json_or_file, 'read'):  # Load from file-like object
                imported_notices = json.load(json_or_file)
            self.add_notices(imported_notices)
            log_message("Successfully imported notices from json.")
        except Exception as e:
            log_warning(f"Failed to import notices from json: {type(e).__name__} - {str(e)}", exc_info=True)

    def _update_counts(self, notice, remove=False):
        level_code = notice["level_code"]
        level_name = notice["level_name"]

        if remove:
            if level_code >= self.ERROR_CODE_START_VALUE:
                self._errors_count -= 1
            elif level_code >= self.WARNING_CODE_START_VALUE:
                self._warnings_count -= 1
            elif level_code >= self.SUCCESS_CODE_START_VALUE:
                self._successes_count -= 1
            self._level_counts[level_name] -= 1
        else:
            if level_code >= self.ERROR_CODE_START_VALUE:
                self._errors_count += 1
            elif level_code >= self.WARNING_CODE_START_VALUE:
                self._warnings_count += 1
            elif level_code == self.SUCCESS_CODE_START_VALUE:
                self._successes_count += 1
            self._level_counts[level_name] += 1