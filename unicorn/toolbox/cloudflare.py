#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLI tools for cloudflare automation
.. currentmodule:: unicorn.toolbox.cloudflare
.. moduleauthor:: John <jpurcell.ee@gmail.com>
"""
import collections
import os

import CloudFlare
import tldextract
import requests
from plumbum import cli
import dotenv

from . import __version__
from . import common

IP_Type = collections.namedtuple("IP_Type", ["address", "type"])
DNS_Change_Status = collections.namedtuple(
    "DNS_Change_Status", ["status", "message", "update_required"]
)  # TODO: class?


class NoPublicIPFound(Exception):
    """Unable to resolve public facing IP address"""

    def __init__(self, endpoints):
        endpoints = endpoints
        # TODO: logger/__repr__


def my_ip_address(endpoints: list) -> IP_Type:
    """find public IP address

    Args:
        endpoints (list): query endpoints for resolving public IP

    Raises:
        requests.exceptions.RequestException
        NoPublicIPFound: unable to resolve public facing IP

    Returns:
        IP_Type: public IP (v4)

    """
    if isinstance(endpoints, str):
        # Avoid `for str()` yielding character list
        endpoints = [endpoints]

    ip_addr = ""
    for endpoint in endpoints:
        req = requests.get(endpoint)
        req.raise_for_status()
        ip_addr = req.text.strip()
        if ip_addr:
            break
    if not ip_addr:
        raise NoPublicIPFound(endpoints)

    if ":" in ip_addr:
        return IP_Type(ip_addr, "AAAA")
    return IP_Type(ip_addr, "A")


def check_dns_change_status(
    public_ip: IP_Type, content: str, record: str
) -> DNS_Change_Status:
    """Helper to yield decision + logging message

    Args:
        public_ip (IP_Type): new target IP/type
        content (str): TODO
        record (str): TODO

    Returns:
        DNS_Change_Status: status/message/update_required

    """
    supported_types = ["A", "AAAA"]
    if public_ip.type not in supported_types:
        return DNS_Change_Status(
            "Invalid Type",
            f"Only support the following records: {supported_types}",
            False,
        )
    if public_ip.type != record:
        return DNS_Change_Status(
            "Unmatched Types",
            f"Previous record:{record} current record:{public_ip.type}",
            False,
        )
    if public_ip.address == content:
        return DNS_Change_Status(
            "No Update", f"Remote IP matches Local IP: {public_ip.address}", False
        )

    return DNS_Change_Status("Update", "No Skip case found", True)


def create_dns_record(
    cf: CloudFlare.CloudFlare, zone_id: str, fqdn: str, public_ip: IP_Type
) -> list:
    """creates new DNS record on cloudflare if one does not already exist

    Args:
        cf (CloudFlare.CloudFlare): CloudFlare API object
        zone_id (str): which zone to apply config to
        fqdn (str): fqdn of entry to be added
        public_ip (IP_Type): tuple with IP/type to create record

    Returns:
        list: return info from cf.put() command

    Raises:
        CloudFlare.exceptions.CloudFlareAPIError

    """
    dns_record = {"name": fqdn, "type": public_ip.type, "content": public_ip.address}
    dns_record = cf.zones.dns_records.post(zone_id, data=dns_record)
    return dns_record


def update_dns_record(
    cf: CloudFlare.CloudFlare, zone_id: str, fqdn: str, public_ip: IP_Type, record: dict
) -> list:
    """Updates existing DNS record on cloudflare

    Args:
        cf (CloudFlare.CloudFlare): CloudFlare API object
        zone_id (str): which zone to apply config to
        fqdn (str): fqdn of entry to be added
        public_ip (IP_Type): tuple with IP/type to update record
        record (dict): existing cf record

    Returns:
        list: return info from cf.put() command

    Raises:
        CloudFlare.exceptions.CloudFlareAPIError

    """
    dns_record = {
        "name": fqdn,
        "type": public_ip.type,
        "content": public_ip.address,
        "proxied": record["proxied"],
    }
    dns_record = cf.zones.dns_records.put(zone_id, record["id"], data=dns_record)
    return dns_record

def delete_dns_record(cf: CloudFlare.CloudFlare, zone_id: str, record_id) -> list:
    """Updates existing DNS record on cloudflare

    Args:
        cf (CloudFlare.CloudFlare): CloudFlare API object
        zone_id (str): which zone to apply config to
        fqdn (str): fqdn of entry to be added
        public_ip (IP_Type): tuple with IP/type to update record
        record (dict): existing cf record

    Returns:
        list: return info from cf.delete() command

    Raises:
        CloudFlare.exceptions.CloudFlareAPIError

    """
    dns_record = cf.zones.dns_records.delete(zone_id, record_id)
    return dns_record

class CloudflareCLI(common.CommonCLI):
    """parent class to hold args"""

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


    def get_zones(self, cf: CloudFlare.CloudFlare) -> list:
        """render zones information

        Args:
            cf (CloudFlare.CloudFlare):  CloudFlare API object

        Returns:
            list: list of zones for a given self.fqdn

        """
        tld = tldextract.extract(self.fqdn)
        return cf.zones.get(params={"name": f"{tld.domain}.{tld.suffix}"})

    def get_records(self, cf: CloudFlare.CloudFlare, zone_id: str, record_type: str) -> list:
        """query records from CloudFlare

        Args:
            cf (CloudFlare.CloudFlare): CloudFlare API object
            zone_id (str): CloudFlare zone id
            record_type (str): which record to look up

        Returns:
            list: list of records from CloudFlare

        """
        params = {"name": self.fqdn, "match": "all", "type": record_type}
        return cf.zones.dns_records.get(zone_id, params=params)

class CloudflareDDNS(CloudflareCLI):
    """Updates Cloudflare DNS entries around a dynamically switching local IP address

    Adapted from: https://github.com/K0p1-Git/cloudflare-ddns-updater
    Adapted from: https://github.com/cloudflare/python-cloudflare/blob/master/examples/example_update_dynamic_dns.py
    By Way of: https://learn.networkchuck.com/courses/take/ad-free-youtube-videos/lessons/26055468-ddns-on-a-raspberry-pi-using-the-cloudflare-api-dynamic-dns

    """

    PROGNAME = "cf-ddns"
    VERSION = __version__

    def main(self):
        print("Hello world")
        public_ip = my_ip_address(self.public_endpoint)
        print(f"public ip: {public_ip}")

        cf = CloudFlare.CloudFlare(token=self.cloudflare_token)

        zones = self.get_zones(cf)

        for zone in zones:
            dns_records = self.get_records(cf, zone["id"], public_ip.type)

            if not dns_records:
                print(f"creating new DNS record: {self.fqdn}:{public_ip.address}")
                result = create_dns_record(cf, zone["id"], self.fqdn, public_ip)
                print(f"--create_dns_record: {result}")
                continue

            for record in dns_records:
                status = check_dns_change_status(
                    public_ip, record["content"], record["type"]
                )
                if status.update_required is False:
                    print(f"SKIPPING: {status.message}")
                    continue

                print(f"updating DNS record: {self.fqdn}:{public_ip} {record}")
                result = update_dns_record(cf, zone["id"], self.fqdn, public_ip, record)
                print(f"--update_dns_record: {result}")


class CloudflareDelete(CloudflareCLI):
    """Removes Cloudflare DNS entries"""

    PROGNAME = "cf-ddns-delete"
    VERSION = __version__

    def main(self):
        print("Hello world")
        public_ip = my_ip_address(self.public_endpoint)
        print(f"public ip: {public_ip}")

        cf = CloudFlare.CloudFlare(token=self.cloudflare_token)

        zones = self.get_zones(cf)

        for zone in zones:
            dns_records = self.get_records(cf, zone["id"], public_ip.type)

            for record in dns_records:
                print(f"Removing record: {self.fqdn}:{record['id']}")
                result = delete_dns_record(cf, zone["id"], record["id"])

def run_cloudflare_DDNS():
    """Hook for entry_points"""
    CloudflareDDNS.run()


def delete_cloudflare_dns():
    """Hook for entry_points"""
    CloudflareDelete.run()

if __name__ == "__main__":
    run_cloudflare_DDNS()
