import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from requests import Response, Session

from jf_ingest.utils import retry_for_status

logger = logging.getLogger(__name__)


GQL_PAGE_INFO_BLOCK = "pageInfo {hasNextPage, endCursor}"
GQL_RATE_LIMIT_QUERY_BLOCK = "rateLimit {remaining, resetAt}"


@dataclass
class GQLRateLimit:
    remaining: int
    reset_at: datetime


class GqlRateLimitedExceptionInner(Exception):
    pass


def gql_format_to_datetime(datetime_str: str) -> Optional[datetime]:
    """Attempt to formate a datetime str from the GQL format to a python Datetime Object
    NOTE: This currently is only verified to support the github GQL format. It is NOT YET
    GENERALIZED

    Args:
        datetime_str (str): The datetime from graphql

    Returns:
        datetime: A valid, timezone aware datetime
    """
    if datetime_str:
        return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    else:
        return None


def get_gql_rate_limit(session: Session, base_url: str) -> GQLRateLimit:
    """Attempt to pull the current rate limit information from GQL
    NOTE: Getting the rate limit info is never affected by the current rate limit

    Args:
        session (Session): A valid session connecting us to the GQL API
        base_url (str): The base URL we are hitting

    Returns:
        dict: A dictionary object containing rate limit information (remaing and resetAt)
    """
    query_body = f"{{{GQL_RATE_LIMIT_QUERY_BLOCK}}}"
    # NOTE: DO NOT CALL get_raw_gql_result TO GET THE RESULTS HERE! IT'S A RECURSIVE TRAP
    response: Response = retry_for_status(session.post, url=base_url, json={'query': query_body})
    response.raise_for_status()
    json_str = response.content.decode()
    raw_data: dict = json.loads(json_str)['data']['rateLimit']
    return GQLRateLimit(
        remaining=int(raw_data['remaining']), reset_at=gql_format_to_datetime(raw_data['resetAt'])
    )
