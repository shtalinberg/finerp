"""
Privat24 API client for interacting with the banking API.
"""
import datetime
import json
import logging
from typing import Any, Dict, List, Optional, Union

from django.conf import settings

import requests
import urllib3

# Configuration either from specific settings or from django settings
from . import settings as pb_conf

logger = logging.getLogger(__name__)

# Disable insecure request warnings - should be removed in production
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class P24ApiAutoClient:
    """
    Client for Privat24 API version 3.0.0

    Provides methods to interact with the Privat24 banking API for retrieving
    transactions, currency rates, and other banking information.

    Documentation: https://docs.google.com/document/d/e/2PACX-1vTtKvGa3P4E-lDqLg3bHRF6Wi9S7GIjSMFEFxII5qQZBGxuTXs25hQNiUU1hMZQhOyx6BNvIZ1bVKSr/pub
    """

    API_VERSION = '3.0.0'
    DEFAULT_TIMEOUT = 120  # 2 minutes in seconds
    DATE_FORMAT = "%d-%m-%Y"

    def __init__(self, token: Optional[str] = None, verify_ssl: bool = True):
        """
        Initialize the API client.

        Args:
            token: API token for authentication (defaults to settings)
            verify_ssl: Whether to verify SSL certificates
        """
        self.user_agent = f'P24ApiAutoClient {self.API_VERSION} (Language=Python)'
        self.server_url = 'https://acp.privatbank.ua/api/'
        self.verify_ssl = verify_ssl
        self.token = token or pb_conf.PRIVAT24_API_TOKEN

    def _headers(self) -> Dict[str, str]:
        """
        Create request headers including authentication.

        Returns:
            Dict of HTTP headers
        """
        headers = requests.utils.default_headers()
        headers['User-Agent'] = self.user_agent
        headers['Content-Type'] = 'application/json;charset=utf8'
        headers['token'] = self.token
        return headers

    def send_request(
        self,
        operation: str,
        resource: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> requests.Response:
        """
        Send request to the API.

        Args:
            operation: HTTP method (get, post, put)
            resource: API endpoint
            timeout: Request timeout in seconds

        Returns:
            HTTP response object

        Raises:
            requests.RequestException: For request errors
        """
        if resource.startswith('/'):
            resource = resource[1:]

        request_url = f"{self.server_url}{resource}"
        request_headers = self._headers()

        try:
            if operation == "post":
                response = requests.post(
                    request_url,
                    timeout=timeout,
                    headers=request_headers,
                    verify=self.verify_ssl,
                )
            elif operation == "put":
                response = requests.put(
                    request_url,
                    timeout=timeout,
                    headers=request_headers,
                    verify=self.verify_ssl,
                )
            else:  # Default to GET
                response = requests.get(
                    request_url,
                    timeout=timeout,
                    headers=request_headers,
                    verify=self.verify_ssl,
                )

            # Log the request for debugging/monitoring
            logger.debug(
                "API Request: %s %s, Status: %s",
                operation.upper(),
                request_url,
                response.status_code
            )

            return response

        except requests.Timeout as timeout_error:
            logger.exception(
                "Timeout sending %s request to %s: %s",
                operation,
                request_url,
                timeout_error,
            )
            raise
        except requests.RequestException as req_error:
            logger.exception(
                "Error sending %s request to %s: %s",
                operation,
                request_url,
                req_error,
            )
            raise

    def get_server_time(self) -> requests.Response:
        """
        Get server time and settings from the API.

        Returns:
            Response containing server time and settings
        """
        return self.send_request('get', 'statements/settings')

    def get_transactions(
        self,
        interim: bool = False,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        limit: int = 100,
        follow_id: Optional[str] = None,
        acc: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get transactions for the specified period.

        Args:
            interim: Whether to get interim (pending) transactions
            start_date: Start date for transactions
            end_date: End date for transactions
            limit: Maximum number of transactions to return (max 500)
            follow_id: ID for pagination from next_page_id field
            acc: Account number

        Returns:
            Dictionary with transactions data including pagination info
            {
                'status': 'SUCCESS',
                'type': 'transactions',
                'exist_next_page': True/False,
                'next_page_id': '123456_online',
                'transactions': [...]
            }
        """
        resource = 'statements/transactions'
        if interim:
            resource = f'{resource}/interim'

        # Build query parameters
        resource = f'{resource}?limit={min(limit, 500)}'  # Ensure limit is within bounds

        if acc:
            resource = f'{resource}&acc={acc}'

        if follow_id:
            resource = f'{resource}&followId={follow_id}'

        if start_date and end_date:
            start_date_str = start_date.strftime(self.DATE_FORMAT)
            end_date_str = end_date.strftime(self.DATE_FORMAT)
            resource = f'{resource}&startDate={start_date_str}&endDate={end_date_str}'

        # Send request to API
        resp = self.send_request('get', resource)

        if resp.status_code != 200:
            logger.error("Failed to get transactions: %s", resp.status_code)
            return {'status': 'ERROR', 'transactions': []}

        try:
            jdata = json.loads(resp.content)
            if jdata.get('status') == 'SUCCESS':
                return jdata
            else:
                logger.error("API returned error: %s", jdata.get('errorMessage', 'Unknown error'))
                return {'status': 'ERROR', 'transactions': []}
        except json.JSONDecodeError:
            logger.exception("Failed to parse transaction response")
            return {'status': 'ERROR', 'transactions': []}

    def get_currency(self) -> Dict[str, Any]:
        """
        Get current currency exchange rates.

        Returns:
            Dictionary with currency rates
        """
        resource = 'proxy/currency'

        # Send request to API
        resp = self.send_request('get', resource)

        if resp.status_code != 200:
            logger.error("Failed to get currency rates: %s", resp.status_code)
            return {}

        try:
            jdata = json.loads(resp.content)
            if 'cache_info' in jdata:
                return jdata
        except json.JSONDecodeError:
            logger.exception("Failed to parse currency response")

        return {}

    def get_currency_history(
        self,
        start_date: Union[str, datetime.date],
        end_date: Union[str, datetime.date]
    ) -> Dict[str, Any]:
        """
        Get historical currency exchange rates.

        Args:
            start_date: Start date for history
            end_date: End date for history

        Returns:
            Dictionary with currency rate history

        Raises:
            ValueError: If dates are invalid or period is too long
        """
        # Convert string dates to datetime if needed
        if isinstance(start_date, str):
            start_date = datetime.datetime.strptime(start_date, self.DATE_FORMAT).date()
        if isinstance(end_date, str):
            end_date = datetime.datetime.strptime(end_date, self.DATE_FORMAT).date()

        # Validate dates
        if start_date > end_date:
            raise ValueError("start_date must be less than or equal to end_date")

        if (end_date - start_date).days > 15:
            raise ValueError("The difference between start_date and end_date must be less than or equal to 15 days")

        # Format dates for API
        start_date_str = start_date.strftime(self.DATE_FORMAT)
        end_date_str = end_date.strftime(self.DATE_FORMAT)

        resource = f'proxy/currency/history?startDate={start_date_str}&endDate={end_date_str}'

        # Send request to API
        resp = self.send_request('get', resource)

        if resp.status_code != 200:
            logger.error("Failed to get currency history: %s", resp.status_code)
            return {}

        try:
            jdata = json.loads(resp.content)
            if 'cache_info' in jdata:
                return jdata
        except json.JSONDecodeError:
            logger.exception("Failed to parse currency history response")

        return {}