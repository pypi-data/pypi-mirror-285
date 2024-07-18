import dataclasses
import hashlib
import io
import json
import logging
import sys
import time
import traceback
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from datetime import datetime
from types import TracebackType
from typing import Any, Callable, Generator, Iterable, Optional, Type

import requests
from jira.exceptions import JIRAError
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3 import Retry

from jf_ingest import logging_helper

logger = logging.getLogger(__name__)

# Exponent base of 4 gives more reasonable
# max timeout of 4m16 rather than 10m25s for
# 5 retries
RETRY_EXPONENT_BASE = 4
DEFAULT_HTTP_CODES_TO_RETRY_ON = (429, 502, 503, 504)

# There appears to be intermittent 404s that get thrown for versions and components.
# When we retry, the 404 goes away.
PROJECT_HTTP_CODES_TO_RETRY_ON = tuple(list(DEFAULT_HTTP_CODES_TO_RETRY_ON) + [404])

DEFAULT_EXCEPTIONS_TO_RETRY_ON = (
    requests.exceptions.ReadTimeout,
    requests.exceptions.ConnectionError,
)


class RetryLimitExceeded(Exception):
    pass


class StrDefaultEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return str(o)


class ReauthSession(requests.Session):
    """
    A requests session that will re-authenticate on 401s
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def request(self, method, url, **kwargs) -> requests.Response:
        """
        Run a request, and if we get a 401, re-authenticate and try again.
        @:param: method: The HTTP method to use
        @:param: url: The URL to request
        @:param: kwargs: Any additional kwargs to pass to the request
        (a reauth session is usually instantiated with just ReauthSession(**kwargs))
        @:return: The response object from calling request()
        """
        # If we get HTTP 401, re-authenticate and try again
        response = super().request(method, url, **kwargs)
        if response.status_code == 401:
            # Use print instead of logger.log, as URL could be considered sensitive data
            logger.warn(f"Received 401 for the request [{method}] {url} - resetting client session")

            # Clear cookies and re-auth
            self.cookies.clear()
            response = super().request(method, url, **kwargs)
            self.cookies = response.cookies
        return response


def retry_session(**kwargs) -> requests.Session:
    """
    Obtains a requests session with retry settings.
    :return: session: Session
    """

    session = ReauthSession(**kwargs)

    retries = 3
    backoff_factor = 0.5
    status_forcelist = (500, 502, 503, 504, 104)

    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def get_wait_time(e: Optional[Exception], retries: int) -> int:
    """
    This function attempts to standardize determination of a wait time on a retryable failure.
    If the exception's response included a Retry-After header, respect it.
    If it does not, we do an exponential backoff - 1s, 4s, 16s, 64s, 256s.

    A possible future addition would be to add a jitter factor.
    This is a fairly standard practice but not clearly required for our situation.
    """
    # getattr with a default works on _any_ object, even None.
    # We expect that almost always e will be a JIRAError or a RequestException, so we will have a
    # response and it will have headers.
    # So I'm choosing to use the getattr call to handle the valid but infrequent possibility
    # that it may not (None or another Exception type that doesn't have a response), rather tha
    # preemptively checking.
    response = getattr(e, "response", None)
    headers = getattr(response, "headers", {})
    retry_after = headers.get("Retry-After")

    # Normalize retry after if it is a string
    if isinstance(retry_after, str) and retry_after.isnumeric():
        retry_after = int(retry_after)
    # Don't do anything if we have a valid int for retry after
    elif isinstance(retry_after, int):
        pass
    else:
        # Null out any invalid retry after values
        retry_after = None

    if retry_after:
        return retry_after
    else:
        return RETRY_EXPONENT_BASE**retries


def retry_for_status(
    f: Callable[..., Any],
    *args,
    max_retries_for_retry_for_status: int = 5,
    statuses_to_retry: Iterable[int] = DEFAULT_HTTP_CODES_TO_RETRY_ON,
    exceptions_to_retry: Iterable[Type[Exception]] = DEFAULT_EXCEPTIONS_TO_RETRY_ON,
    **kwargs,
) -> Any:
    """
    This function allows for us to retry for a variety of retryable errors from Jira.
    There are much more elegant ways of accomplishing this, but this is a quick and
    reasonable approach to doing so.

    Default statuses are 429 (rate limit exceeded) and 5xx errors (server errors).

    Note:
        - max_retries=5 will give us a maximum wait time of 4m16s.
    """
    for retry in range(max_retries_for_retry_for_status + 1):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            if retry >= max_retries_for_retry_for_status:
                raise RetryLimitExceeded(e)
            is_handled_exception = any(
                isinstance(e, exception) for exception in exceptions_to_retry
            )
            if not (is_handled_exception or getattr(e, "status_code", None) in statuses_to_retry):
                # Raise any non-429 related errors
                raise e

            # Otherwise retry
            wait_time = get_wait_time(e, retries=retry)
            error_code = 3071
            msg_args = [
                f"err={e.__class__.__name__},status={e.status_code}"
                if hasattr(e, "status_code")
                else f"err={e.__class__.__name__}",
                retry + 1,
                max_retries_for_retry_for_status,
                wait_time,
            ]
            logging_helper.log_standard_error(
                logging.WARNING,
                msg_args=msg_args,
                error_code=error_code,
            )
            time.sleep(wait_time)
            continue


def test_jira_or_git_object_access(
    f: Callable[..., Any],
    *args,
    is_sprint: bool = False,
    return_objs: bool = True,
    return_attr: Optional[str] = None,
    **kwargs,
) -> tuple[bool, list[Any]]:
    """
    Determines whether we can access a particular class of objects within jira or git. In general, this returns True
    if no errors are thrown and False otherwise. Sprints are a special case. Boards may not support sprints,
    the board could be misconfigured, etc. If we are looking for a sprint and get a 400, 404, or 500 error
    response, assume that everything is ok and we're not missing any access.

    Args:
        f (Callable[..., Any]): JIRA.<function>
        is_sprint (bool, optional): whether we are looking for sprint data. Defaults to False. Only applicable to Jira
        return_obj (bool, optional): whether we want to return some data from the accessed objects. Returns an empty list if False. Defaults to True.
        return_attr (Any): attribute to return in a list from the accessed objects.

    Returns:
        bool: whether access to the specified object type is available.
    """

    return_attr = return_attr or 'name'

    def _get_return_list(objs: Iterable) -> list:
        objs = list(objs)  # put generator items into memory if we're dealing with git
        if not return_objs or not objs:
            return []
        if isinstance(objs[0], dict):
            return [d.get(return_attr) for d in objs]
        if not hasattr(objs[0], return_attr):
            return []
        return [getattr(obj, return_attr) for obj in objs]

    try:
        objs = retry_for_status(f, *args, **kwargs)
        return True, _get_return_list(objs)
    except JIRAError as e:
        if is_sprint:
            return e.status_code in [400, 404, 500], []
        logger.debug(
            f'Jira Error ({e.status_code}) encountered when attempting to hit function {f.__name__}. Error: {e}'
        )
        return False, []
    except Exception as e:
        logger.debug(f'Error encountered when attempting to hit function {f.__name__}. Error: {e}')
        return False, []


def batch_iterable(iterable: Iterable, batch_size: int) -> Generator[list[Any], None, None]:
    """Helper function used for batching a given iterable into equally sized batches

    Args:
        iterable (Iterable): An iterable you want to split into batches
        batch_size (int): The size of the batches you want

    Yields:
        Generator[list[Any], None, None]: This generator yields a list of equal size batches, plus a potential final batch that is less than the batch_size arg
    """
    chunk = []
    i = 0
    for item in iterable:
        chunk.append(item)
        i += 1
        if i == batch_size:
            yield chunk
            chunk = []
            i = 0

    if chunk:
        yield chunk


def get_object_bytes_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = 0
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_object_bytes_size(v, seen) for v in obj.values()])
        size += sum([get_object_bytes_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_object_bytes_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_object_bytes_size(i, seen) for i in obj])
    else:
        size += sys.getsizeof(obj)
    return size


def batch_iterable_by_bytes_size(
    iterable: Iterable, batch_byte_size: int
) -> Generator[list[Any], None, None]:
    """Helper function that batches an iterable by it's total size in bytes

    Args:
        iterable (Iterable): An iterable type object that you want batched
        batch_byte_size (int): The total size of each batch size, in bytes

    Yields:
        Generator[list[Any], None, None]: A generator that returns roughly equal sized batches of data (in byte size)
    """
    chunk = []
    current_chunk_size = 0
    for item in iterable:
        chunk.append(item)
        current_chunk_size += get_object_bytes_size(item)

        if current_chunk_size >= batch_byte_size:
            yield chunk
            # Reset batch information
            chunk = []
            current_chunk_size = 0

    # Write the final batch, if applicable
    if chunk:
        yield chunk


def format_date_to_jql(_datetime: datetime) -> str:
    """Formats a python datetime to a str in this format: YYYY-MM-DD, which is JQL friendly

    Args:
        datetime (datetime): A valid Python Datetime

    Returns:
        str: Returns a formatted datetime str in this format (with padded 0s, if needed): YYYY-MM-DD
    """
    # Special case: if we've got date.min, always return year 1, month 1, day 1.
    # This value should really never be provided, but for legacy reasons we used
    # to mark issues needing redownload as having an updated value as datetime.min
    if _datetime == datetime.min:
        return f'"0001-01-01"'

    return f'"{_datetime.year:04}-{_datetime.month:02}-{_datetime.day:02}"'


def format_datetime_to_ingest_timestamp(datetime: datetime):
    return datetime.strftime("%Y%m%d_%H%M%S")


class TqdmToLogger(io.StringIO):
    """
    Output stream for TQDM which will output to logger module instead of
    the StdOut.
    """

    logger = None
    level = None
    buf = ''

    def __init__(self, logger, level=None):
        super(TqdmToLogger, self).__init__()
        self.logger = logger
        self.level = level or logging.INFO

    def write(self, buf):
        self.buf = buf.strip('\r\n\t ')

    def flush(self):
        self.logger.log(self.level, self.buf)


def tqdm_to_logger(*args, **kwargs) -> tqdm:
    """HACK helper function to wrap up the TQDM progress bar to extend it's functionality.
    If you use this helper function in place of the normal tqdm() call it will behave differently
    in Agent and in Direct Connect. In Agent, TQDM will act as if you called it directly.
    If you call this function in a DIRECT_CONNECT context, it will print each TQDM progress
    update to our logger wrapper (at the INFO level), which will get caught up in Prefect.

    Returns:
        tqdm: A TQDM object
    """
    from jf_ingest.config import IngestionType

    ingestion_type = logging_helper.get_ingestion_type()
    if ingestion_type == IngestionType.DIRECT_CONNECT:
        tqdm_out = TqdmToLogger(logger, level=logging.INFO)
        # Log progress bar every 10 minutes (minimum) in prefect
        mininterval = kwargs.get('mininterval', 60 * 10)
        return tqdm(file=tqdm_out, mininterval=mininterval, ascii=False, *args, **kwargs)
    return tqdm(*args, **kwargs)


class ThreadPoolWithTqdm(ThreadPoolExecutor):
    """THIS CLASS MUST BE USED AS A CONTEXT MANAGER ONLY!!!!

    This is a custom class that extends the ThreadPoolExecutor class,
    and combines it with some TQDM (progress bar) functionality. This
    should help reduce the number of repeated code around jf_ingest

    Yes, I know there is a concurrency extension for TQDM (tqdm.contrib.concurrent)
    BUT this library only has .map style functions, and it does NOT have a submit style
    function. There are instances where using submit is preferred, and often it lends itself
    to simpler code. That is what this library is for

    Args:
        ThreadPoolExecutor (ThreadPoolExecutor): The parent class that this extends

    Returns:
        ThreadPoolWithTqdm: ThreadPoolWithTqdm
    """

    desc: str
    total: int
    futures: set[Future]
    raise_exceptions: bool
    prog_bar: tqdm

    def __init__(
        self,
        desc: str = None,
        total: int = 0,
        max_workers: int | None = None,
        raise_exceptions: bool = False,
        thread_name_prefix: str = "",
        initializer: Callable[..., object] | None = None,
        initargs: tuple[Any, ...] = ...,
    ) -> None:
        """Custom Constructor, to allow us to set the progress bar values

        Args:
            desc (str, optional): The description field on the TQDM progress bar. Defaults to None.
            total (int, optional): The total value to set on the TQDM progress bar. Defaults to 0.
            max_workers: The maximum number of threads that can be used to execute the given calls.
            thread_name_prefix: An optional name prefix to give our threads.
            initializer: A callable used to initialize worker threads.
            initargs: A tuple of arguments to pass to the initializer.

        """

        self.desc = desc
        self.total = total
        self.futures = set()
        self.raise_exceptions = raise_exceptions
        super().__init__(max_workers, thread_name_prefix, initializer, initargs)

    def __enter__(self):
        """Override the __enter__ function to instantiate a progress bar (TQDM)
        when using this as a context manager.
        """
        self.prog_bar = tqdm_to_logger(desc=self.desc, total=self.total)
        return super().__enter__()

    def submit(self, fn: Callable, *args, **kwargs) -> Future:
        future = super().submit(fn, *args, **kwargs)
        self.futures.add(future)
        return future

    def get_results(self) -> Generator[Any, None, None]:
        while self.futures:
            done_futures, _ = wait(self.futures, return_when=FIRST_COMPLETED)
            for done_future in done_futures:
                # Update the progress bar each time we get a future back
                try:
                    self.update_progress_bar(done_future)
                    yield done_future.result()
                except Exception as e:
                    logging_helper.send_to_agent_log_file(
                        f'Exception encountered in ThreadPoolExecutor: {e}',
                        level=logging.ERROR,
                        exc_info=True,
                    )
                    if self.raise_exceptions:
                        raise
                finally:
                    # Remove the future from the pool, for memory performance management
                    self.futures.remove(done_future)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        """Override the __exit__ function to tear down a progress bar (TQDM)
        when using this as a context manager.
        Progress bar .close() call MUST BE AFTER THE THREADPOOLEXECUTOR TEARDOWN.

        Also raises any exceptions we encountered
        """

        # Always empty the thread pool before exiting, so that the progress bar increments
        # even if nobody ever called the get_results function
        if self.futures:
            for _ in self.get_results():
                # Iterate through the get_results generate to force progress bar load
                pass
        retval = super().__exit__(exc_type, exc_val, exc_tb)

        # Progress bar must be close AFTER the parent __exit__ call,
        # because the parent __exit__ call is blocking
        self.prog_bar.close()

        return retval

    def update_progress_bar(self, future: Future):
        """A custom callback function that iterates on the progress bar by
        default. Does some guessing to see how much we should updated the
        progress bar by

        Args:
            future (Future): A ThreadPoolExecutor Future object
        """
        if future.exception():
            return

        result = future.result()

        with tqdm.get_lock():
            if isinstance(result, Iterable):
                self.prog_bar.update(len(result))
            else:
                self.prog_bar.update(1)


def get_s3_base_path(company_slug: str, timestamp: str):
    return f"{company_slug}/{timestamp}"


class RewriteJiraSessionHeaders(object):
    """
    This context manager will temporarily rewrite the headers of the JIRA session to
    only use the Accept: application/json header, no other additional value. This gets around
    the incident where resolutions endpoint failed with HTTP 406 errors
    https://jelly-ai.atlassian.net/browse/OJ-31563
    """

    saved_old_accept_headers = ""
    jira_connection = None

    def __init__(self, jira_connection):
        self.jira_connection = jira_connection

    def __enter__(self):
        self.old_headers = self.jira_connection._session.headers
        self.saved_old_accept_headers = self.jira_connection._session.headers["Accept"]
        self.jira_connection._session.headers["Accept"] = "Application/json"

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.jira_connection._session.headers["Accept"] = self.saved_old_accept_headers


def chunk_iterator_in_lists(n, iterable) -> list[list]:
    """
    :param n: The size of the chunks
    :param iterable: The iterable to chunk
    :return: A list of lists where each inner list is of size n with the final inner list having size len(iterable) % n
    if n == 0 then return [[], [<all elements>]] as it produces a chunk of size 0, and then all remainders
    """
    parent_list = []
    counter = 0
    while counter + n <= len(iterable):
        parent_list.append(iterable[counter : counter + n])
        counter += n
    if counter < len(iterable):
        parent_list.append(iterable[counter : len(iterable)])
    return parent_list


def hash_filename(filepath: str):
    """
    Helper function for files. Hashes a filepath, tokenized by '/'.
    :param filepath: Input filepath.
    """

    def _compute_hash(string):
        return hashlib.md5(string.encode('utf-8'), usedforsecurity=False).hexdigest()[:12]

    extension = filepath.split(".")[-1]
    paths_list = filepath.split("/")

    # Check if a file extension (.) exists
    if len(extension) == len(filepath):
        return _compute_hash(filepath)
    return "/".join([_compute_hash(path) for path in paths_list]) + f".{extension}"
