"""Theme Configuration: A Plug-In for Pelican

This package provides a plug-in for the Pelican static website generator and
enables support for themes to adjust Pelican's configuration using the
'themeconf.py' file located in the root directory of the theme.

The plug-in can be customised via the following configuration options in the
primary Pelican configuration file:

    THEME_CONFIG = 'themeconf.py'
    THEME_CONFIG_PROTECTED = []

This package does not expose any functions and is hooked up early in Pelican's
start-up sequence leveraging the "initialized" Pelican event.
"""
from .theme_config import register

__all__ = ["register"]
