#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLI tools for cloudflare automation
.. currentmodule:: unicorn.toolbox.cloudflare
.. moduleauthor:: John <jpurcell.ee@gmail.com>
"""

import os

import CloudFlare
import tldextract
import requests
from plumbum import cli
import dotenv

from . import __version__
from . import common

DEFAULT_ENV = os.environ.get("UNICORN_CLOUDFLARE_DDNS_ENV")
if DEFAULT_ENV:
    dotenv.load_dotenv(DEFAULT_ENV)


class NoPublicIPFound(Exception):
    """Unable to resolve public facing IP address"""

    def __init__(self, endpoints):
        endpoints = endpoints
        # TODO: logger/__repr__


def my_ip_address(endpoints: list) -> str:
    """find public IP address

    Args:
        endpoints (list): query endpoints for resolving public IP

    Raises:
        requests.exceptions.RequestException
        NoPublicIPFound: unable to resolve public facing IP

    Returns:
        str: public IP (v4)

    """
    if isinstance(endpoints, str):
        endpoints = [endpoints]
    for endpoint in endpoints:
        req = requests.get(endpoint)
        req.raise_for_status()
        if req.text:
            return req.text.strip()
    raise NoPublicIPFound(endpoints)


class CloudflareDDNS(common.CommonCLI):
    """Updates Cloudflare DNS entries around a dynamically switching local IP address

    Adapted from: https://github.com/K0p1-Git/cloudflare-ddns-updater
    By Way of: https://learn.networkchuck.com/courses/take/ad-free-youtube-videos/lessons/26055468-ddns-on-a-raspberry-pi-using-the-cloudflare-api-dynamic-dns

    """

    PROGNAME = "cloudflare-ddns"
    VERSION = __version__

    public_endpoint = cli.SwitchAttr(
        "--public-endpoint",
        str,
        list=True,
        help="Endpoint(s) for finding public IP",
        envname="UNICORN_PUBLIC_ENDPOINT",
        default=["https://api.ipify.org/", "https://ipv4.icanhazip.com/"],
    )

    cloudflare_email = cli.SwitchAttr(
        "--cloudflare-email",
        str,
        help="AUTH: login email for cloudflare",
        envname="CF_API_EMAIL",
        # mandatory=True,
    )
    cloudflare_token = cli.SwitchAttr(
        "--cloudflare-token",
        str,
        help="AUTH: API token or Globla API Key",
        envname="CF_API_KEY",
        # mandatory=True,
    )

    fqdn = cli.SwitchAttr(
        "--fqdn",
        str,
        help="Cloudflare zone indentifier - Found in Overview tab",
        envname="UNICORN_FQDN",
    )

    cloudflare_record_name = cli.SwitchAttr(
        "--cloudflare-record-name",
        str,
        help="Cloudflare record name",
        envname="UNICORN_CLOUDFLARE_RECORD_NAME",
    )

    def main(self):
        print("Hello world")
        public_ip = my_ip_address(self.public_endpoint)
        print(f"public ip: {public_ip}")
        tld = tldextract.extract(self.fqdn)

        cf = CloudFlare.CloudFlare(token=self.cloudflare_token)

        zones = cf.zones.get(params={"name": f"{tld.domain}.{tld.suffix}"})
        print(zones)


def run_cloudflare_DDNS():
    """Hook for entry_points"""
    CloudflareDDNS.run()


if __name__ == "__main__":
    run_cloudflare_DDNS()
