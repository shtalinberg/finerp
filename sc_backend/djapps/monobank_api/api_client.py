
import datetime
import logging
from typing import Dict, List, Optional

from django.conf import settings

import requests

logger = logging.getLogger(__name__)

class MonoBankClient:
    """
    Client for MonoBank API

    Documentation: https://api.monobank.ua/docs/
    """

    API_BASE_URL = 'https://api.monobank.ua'

    def __init__(self, token=None):
        """
        Initialize the MonoBank client

        Args:
            token: Personal API token
        """
        self.token = token or settings.MONOBANK_API_TOKEN

    def _headers(self) -> Dict[str, str]:
        """
        Create request headers including authentication

        Returns:
            Dict of HTTP headers
        """
        return {
            'X-Token': self.token,
            'Content-Type': 'application/json',
        }

    def get_client_info(self) -> Dict:
        """
        Get client information including account list

        Returns:
            Dict with client info and accounts list
        """
        url = f"{self.API_BASE_URL}/personal/client-info"

        try:
            response = requests.get(url, headers=self._headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching client info: {str(e)}")
            return {}

    def get_statement(self, account_id: str, from_time: int, to_time: Optional[int] = None) -> List[Dict]:
        """
        Get account statement for the given period

        Args:
            account_id: Account ID
            from_time: Start time in Unix timestamp (seconds)
            to_time: End time in Unix timestamp (seconds)

        Returns:
            List of transactions
        """
        # MonoBank API limits statement period to 31 days (2678400 seconds)
        max_period = 2678400

        if to_time is None:
            to_time = int(datetime.datetime.now().timestamp())

        # Check if period is more than 31 days
        if to_time - from_time > max_period:
            to_time = from_time + max_period

        url = f"{self.API_BASE_URL}/personal/statement/{account_id}/{from_time}/{to_time}"

        try:
            response = requests.get(url, headers=self._headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching statement: {str(e)}")
            return []