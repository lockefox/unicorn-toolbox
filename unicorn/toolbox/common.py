#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Shared utils for Unicorn Toolbox
.. currentmodule:: unicorn.toolbox.common
.. moduleauthor:: John <jpurcell.ee@gmail.com>
"""
import os

from plumbum import cli
import dotenv


class CommonCLI(cli.Application):
    """Common CLI wrapper so all CLI's share similar arguments and functions"""

    verbose = cli.Flag(["v", "--verbose"], help="Increase logging verbosity")

    @cli.switch(["e", "--env-file"], str, help=".env file with defaults for CLI")
    def parse_env_file(self, env_file):
        dotenv.load_dotenv(env_file)
