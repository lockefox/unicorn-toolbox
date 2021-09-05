"""tests for unicorn.toolbox.cloudflare"""

import pytest
import requests_mock

import unicorn.toolbox.cloudflare as cloudflare


class TestMyIPAddress:
    """tests for my_ip_address"""

    dummy_ip_checker = "http://fake.fake.fake"

    @pytest.mark.parametrize(
        "address,record_type", [("10.0.0.1", "A"), ("0:0:0:0:0:0:0:1", "AAAA")]
    )
    def test_my_ip_address(self, address, record_type):
        """test expected happy-path"""
        with requests_mock.Mocker() as m:
            m.get(self.dummy_ip_checker, text=address)
            result = cloudflare.my_ip_address([self.dummy_ip_checker])
        assert result.address == address
        assert result.type == record_type

    @pytest.mark.parametrize(
        "address,record_type", [("10.0.0.1", "A"), ("0:0:0:0:0:0:0:1", "AAAA")]
    )
    def test_my_ip_address_str(self, address, record_type):
        """test supported type change"""
        with requests_mock.Mocker() as m:
            m.get(self.dummy_ip_checker, text=address)
            result = cloudflare.my_ip_address(self.dummy_ip_checker)
        assert result.address == address
        assert result.type == record_type

    def test_my_ip_address_err(self):
        with pytest.raises(cloudflare.NoPublicIPFound):
            with requests_mock.Mocker() as m:
                m.get(self.dummy_ip_checker, text="")
                result = cloudflare.my_ip_address([self.dummy_ip_checker])
