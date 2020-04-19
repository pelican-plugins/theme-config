Theme Configuration Plug-In for Pelican
=======================================

This package provides a plug-in for the Pelican static website generator and
allows the selected theme to adjust Pelican's configuration using the
'themeconf.py' file located in the root directory of the theme.

This allows theme authors create more self-contained themes since everything
that theme requires can be configured within the theme itself:

  * themes can be shipped with their own plugins
  * themes can provide their static content (e.g. a theme that implements
    Google's PWA can provide `manifest.json` that should be put into the
    root of the website)
  * basically, authors could do almost anything :) since with this plugin
    theme gets control

The code is hooked up early in Pelican's start-up sequence leveraging the
"initialized" Pelican event, so almost every configuration option can be
safely redefined and would take effect.

However, since the plug-in hooks up after the sanity checks on the provided
configuration were done by Pelican this gives some opportunities and risks.
Basically, theme authors should be careful to adhere to Pelican's conventions
on the configuration directives, otherwise they may confuse their users.

This plug-in protects the following configuration options from being modified
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

The plug-in introduce the following configuration options one can specify in
the primary Pelican configuration file:

    # The name of the file to lookup in theme's directory
    THEME_CONFIG = 'themeconf.py'

    # The list of configuration options to be protected from modification
    THEME_CONFIG_PROTECTED = ['PATH','OUTPUT_PATH']

Usage
-----

Add `theme_config` to the list of plugins in the `pelicanconf.py` file, e.g.

    PLUGINS = [ 'theme_config' ]

From that point on, Pelican will try to load the `themeconf.py` from theme's
directory.
