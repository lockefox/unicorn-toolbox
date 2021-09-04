#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Helpers for linting Jenkinsfiles
.. currentmodule:: toolbox
.. moduleauthor:: John <jpurcell.ee@gmail.com>
"""
import io
import pkgutil

# import dotenv

__library_name__ = "toolbox"
__version__ = pkgutil.get_data(f"unicorn.{__library_name__}", "VERSION").decode("utf-8")
__release__ = pkgutil.get_data(f"unicorn.{__library_name__}", "VERSION").decode("utf-8")

# # __library_name__/.env not included in git
# dotenv.load_dotenv(
#     stream=io.StringIO(pkgutil.get_data(__library_name__, ".env").decode("utf-8"))
# )
