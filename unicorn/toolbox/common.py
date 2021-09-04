#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Shared utils for Unicorn Toolbox
.. currentmodule:: unicorn.toolbox.common
.. moduleauthor:: John <jpurcell.ee@gmail.com>
"""

from plumbum import cli


class CommonCLI(cli.Application):
    """Common CLI wrapper so all CLI's share similar arguments and functions"""

    verbose = cli.Flag(["v", "--verbose"], help="Increase logging verbosity")
