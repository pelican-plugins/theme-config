# Copyright 2020 Openwall Pty Ltd
#
# Licensed under the GNU Affero General Public License, Version 3;
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import copy
from importlib.util import module_from_spec, spec_from_file_location
import logging
import os
import sys

from pelican.settings import get_settings_from_module
import six

from pelican import signals

logger = logging.getLogger(__name__)

PROTECTED_OPTIONS = [
    "BIND",
    "CACHE_PATH",
    "PATH",
    "PELICAN_CLASS",
    "OUTPUT_PATH",
    "SITEURL",
    "THEME",
    "THEME_CONFIG",
    "THEME_CONFIG_PROTECT",
    "PORT",
]


def load_config(config, context) -> dict:
    """Loads the provided config and parses it

    :param config: A path to the configuration file to load (should end with
        the .py extension)
    :type config: str
    :param context: A dictionary with settings to set the initial context for
        the config file to be loaded
    :type context: dict
    :returns: a dictionary representing key/value pairs loaded from the
        configuration file
    :rtype: dict
    """
    name = os.path.splitext(os.path.basename(config))[0]
    spec = spec_from_file_location(name, config)
    module = module_from_spec(spec)
    module.__dict__.update(context)
    spec.loader.exec_module(module)
    return get_settings_from_module(module)


def init_plugins(context):
    """A fork of pelican.init_plugins() method

    The primary reason for forkin is that we are initialising additional
    plugins and the state is not clean: some plugins where already loaded
    by Pelican().  We just need to load the new ones.

    :param context: an instance of the Pelican class
    :type context: class
    :returns: this function does not return anything useful
    :rtype: None
    """

    settings = context.settings
    logger.debug("Temporarily adding PLUGIN_PATHS to system path")
    _sys_path = sys.path[:]
    for pluginpath in settings["PLUGIN_PATHS"]:
        sys.path.insert(0, pluginpath)
    for plugin in settings["PLUGINS"]:
        # if it's a string, then import it
        if isinstance(plugin, six.string_types):
            if plugin in sys.modules:
                continue
            logger.debug("Loading plugin `%s`", plugin)
            try:
                plugin = __import__(plugin, globals(), locals(), str("module"))
            except ImportError as e:
                logger.error("Cannot load plugin `%s`\n%s", plugin, e)
                continue

        else:  # the plugin was loaded explicitly by the user
            if plugin.__name__ in sys.modules:
                continue
        logger.debug("Registering plugin `%s`", plugin.__name__)
        plugin.register()
        context.plugins.append(plugin)
    logger.debug("Restoring system path")
    sys.path = _sys_path


def initialize(pelican):
    theme_config = pelican.settings.get("THEME_CONFIG", "themeconf.py")
    settings = {}
    protected = pelican.settings.get("THEME_CONFIG_PROTECT", PROTECTED_OPTIONS)
    preserved = {}
    initialised = []

    if not isinstance(protected, list):
        if isinstance(protected, six.string_types):
            logger.warning(
                "THEME_CONFIG_PROTECT should be a list of values,"
                "but a string was provided"
            )
            protected = [protected]
        else:
            raise Exception(
                "The theme_config module requires the THEME_CONFIG_PROTECT "
                "configuration to be correctly set to be a list of strings. "
                "Please check the documentation and correct the issue."
            )

    if not os.path.isfile(theme_config):
        theme_config = os.path.join(pelican.settings.get("THEME"), theme_config)

    if os.path.isfile(theme_config):
        logger.debug('Theme provides a config "{}"'.format(theme_config))

        settings = dict(copy.deepcopy(pelican.settings))

        for p in protected:
            if settings.get(p) is not None:
                preserved.update({p: settings.get(p)})

        settings = load_config(theme_config, settings)

        for p in protected:
            if settings.get(p) is not None:
                if p in preserved.keys():
                    if settings[p] != preserved[p]:
                        logger.warning(
                            "Theme cannot override {}, " "ignoring".format(p)
                        )
                settings.pop(p)

        pelican.settings.update(settings)

        # Edge case: we need to load possible additional plugins since
        #            the earliest we could hook up into Pelican is after
        #            all plugin initialisation was done.

        # first, we memorise the current state in order to be able not
        # to trigger the plugins that were already initialised by now
        if signals.initialized.receivers:
            for plugin in signals.initialized.receivers_for(pelican):
                initialised.append(plugin)

        # second, we load and register the newly defined plugins (if any)
        init_plugins(pelican)

        # last, we call the initialisation of the plugins we did not
        # save state for: remember we are in the "initialized" handler
        # right now and if any plugin wanted to hook up there, this is
        # our chance to trigger them.
        if signals.initialized.receivers:
            for plugin in signals.initialized.receivers_for(pelican):
                if plugin not in initialised:
                    plugin(pelican)

        # this is amazing, isn't it?! :)


def register():
    """Registers the plugin using the "initialized" event"""
    signals.initialized.connect(initialize)
