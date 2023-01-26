Theme Configuration: A Plugin for Pelican
==========================================

[![Build Status](https://img.shields.io/github/actions/workflow/status/pelican-plugins/theme-config/main.yml?branch=main)](https://github.com/pelican-plugins/theme-config/actions)
[![PyPI Version](https://img.shields.io/pypi/v/pelican-theme-config)](https://pypi.org/project/pelican-theme-config/)

This package provides a plugin for the Pelican static website generator and
adds support for themes to adjust Pelican's configuration using the
`themeconf.py` file located in the root directory of the theme.

Installation
------------

This plugin can be installed via:

    python -m pip install pelican-theme-config

Usage
-----

Add `theme_config` to the list of plugins in the `pelicanconf.py` file, e.g.

    PLUGINS = [ "theme_config" ]

From that point on, Pelican will try to load the `themeconf.py` from theme's
directory.

Overview
--------

This plugin allows theme authors to create more self-contained themes since
everything that a theme requires can be configured within the theme itself:

  * themes can be shipped with their own plugins
  * themes can provide their static content (e.g. a theme that implements
    Google's PWA can provide `manifest.json` that should be put into the
    root of the website)
  * basically, authors could do almost anything :) since with this plugin
    theme gets control

The code is hooked up early in Pelican's start-up sequence leveraging the
"initialized" Pelican event, so almost every configuration option can be
safely redefined and would take effect.

However, since the plugin hooks up after the sanity checks on the provided
configuration were done by Pelican this gives some opportunities and risks.
Basically, theme authors should be careful to adhere to Pelican's conventions
on the configuration directives, otherwise they may confuse their users.

This plugin protects the following configuration options from being modified
by the theme:

  - BIND
  - CACHE_PATH
  - PATH
  - PELICAN_CLASS
  - OUTPUT_PATH
  - SITEURL
  - THEME
  - THEME_CONFIG
  - THEME_CONFIG_PROTECTED
  - PORT

This list can be configured by the end user in `pelicanconf.py` if they want
to restrict it even further or make it more relaxed.  The goal is to give the
user the ability to define the expected behaviour for their configuration.

The plugin introduces the following configuration options one can specify in
the primary Pelican configuration file:

    # The name of the file to lookup in theme's directory
    THEME_CONFIG = "themeconf.py"

    # The list of configuration options to be protected from modification
    THEME_CONFIG_PROTECTED = ["PATH","OUTPUT_PATH"]

Contributing
------------

Contributions are welcome and much appreciated. Every little bit helps. You can
contribute by improving the documentation, adding missing features, and fixing
bugs. You can also help out by reviewing and commenting on [existing issues][].

To start contributing to this plugin, review the [Contributing to Pelican][]
documentation, beginning with the **Contributing Code** section.

Credits
-------

Authored by [Dmitry Khlebnikov](https://dmitry.khlebnikov.net/).

[existing issues]: https://github.com/pelican-plugins/theme-config/issues
[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html
