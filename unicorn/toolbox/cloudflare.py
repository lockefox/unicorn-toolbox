#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLI tools for cloudflare automation
.. currentmodule:: unicorn.toolbox.cloudflare
.. moduleauthor:: John <jpurcell.ee@gmail.com>
"""

import os

import requests
from plumbum import cli

from . import __version__
from . import common


class CloudflareDDNS(common.CommonCLI):
    """Updates Cloudflare DNS entries around a dynamically switching local IP address

    Adapted from: https://github.com/K0p1-Git/cloudflare-ddns-updater
    By Way of: https://learn.networkchuck.com/courses/take/ad-free-youtube-videos/lessons/26055468-ddns-on-a-raspberry-pi-using-the-cloudflare-api-dynamic-dns

    """

    PROGNAME = "cloudflare-ddns"
    VERSION = __version__

    def main(self):
        print("Hello world")


def run_cloudflare_DDNS():
    """Hook for entry_points"""
    CloudflareDDNS.run()


if __name__ == "__main__":
    run_cloudflare_DDNS()
