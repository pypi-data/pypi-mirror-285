"""
A POSIX-compliant, CLI parser library for building CLI interfaces, designed
to be flexible, intelligent, and uncompromisingly simple. Clipp aims to make
code more reusable and easily scalable, without compromising performance.
"""
from clipp.core import Command, fill_paragraph, OptionGroup

__author__ = "Ben Ohling"
__copyright__ = f"Copyright (C) 2024, {__author__}"
__version__ = "1.3.2"
__all__ = ["Command", "fill_paragraph", "OptionGroup"]
