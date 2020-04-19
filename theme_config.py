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
import os
import logging
import copy

from importlib.util import spec_from_file_location, module_from_spec
from pelican import signals
from pelican.settings import get_settings_from_module

logger = logging.getLogger(__name__)

protected = [
                'BIND',
                'CACHE_PATH',
                'PATH',
                'PELICAN_CLASS',
                'OUTPUT_PATH',
                'SITEURL',
                'THEME',
                'PORT',
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

def initialize(pelican):
    theme_config = pelican.settings.get('THEME_CONFIG', 'themeconf.py')
    settings = {}

    if not os.path.isfile(theme_config):
        theme_config = os.path.join(pelican.settings.get('THEME'),
                                    theme_config)

    if os.path.isfile(theme_config):
        logger.debug('Theme provides a config "{}"'.format(theme_config))

        settings = dict(copy.deepcopy(pelican.settings))
        for p in protected:
            settings.pop(p)

        settings = load_config(theme_config, settings)

        for p in protected:
            if settings.get(p) is not None:
                logger.warning('Theme cannot override {},'
                               'ignoring'.format(p))
                settings.pop(p)

        pelican.settings.update(settings)

def register():
    """Registers the plugin using the "initialized" event"""
    signals.initialized.connect(initialize)
