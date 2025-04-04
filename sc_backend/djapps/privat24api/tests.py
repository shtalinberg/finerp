import json

import pytest
from privat24api.autoclient import P24ApiAutoClient

from . import settings as pb_conf

# Пропускаємо тест, якщо немає токена
need_token = pytest.mark.skipif(
    not pb_conf.PRIVAT24_API_TOKEN,
    reason="Not run this test without token"
)

class TestP24ApiAutoClient:

    @need_token
    def test_get_server_time(self):
        p24_client = P24ApiAutoClient()
        resp = p24_client.get_server_time()

        assert resp.status_code == 200
        jdata = json.loads(resp.content)
        assert jdata['status'] == 'SUCCESS'
        assert jdata['type'] == 'settings'
        assert jdata['settings']['phase'] == 'WRK'

    @need_token
    def test_get_transactions(self):
        p24_client = P24ApiAutoClient()
        jdata = p24_client.get_transactions(interim=True)

        assert len(jdata) >= 0