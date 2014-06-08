import os
import logging

try:
    from ConfigParser import RawConfigParser, NoOptionError, NoSectionError
except ImportError:
    from configparser import RawConfigParser, NoOptionError, NoSectionError

import mod_wsgi

from .interface import Interface
from .sampler import Sampler

_logger = logging.getLogger(__name__)

class Agent(object):

    def __init__(self, app_name=None, license_key=None, config_file=None,
            environment=None):

        self.sampler = None

        if mod_wsgi.version < (4, 2, 0):
            _logger.fatal('Version 4.2.0 or newer of mod_wsgi is required '
                    'for running the New Relic platform plugin. The plugin '
                    'has been disabled.')

            return

        if config_file is None:
            config_file = os.environ.get('NEW_RELIC_CONFIG_FILE', None)

        if config_file is not None:
            config_object = RawConfigParser()

            if config_file:
                config_object.read([config_file])

            if environment is None:
                environment = os.environ.get('NEW_RELIC_ENVIRONMENT', None)

            def _option(name, section='newrelic', type=None, **kwargs):
                try:
                    getter = 'get%s' % (type or '')
                    return getattr(config_object, getter)(section, name)
                except NoOptionError:
                    if 'default' in kwargs:
                        return kwargs['default']
                    else:
                        raise

            def option(name, type=None, **kwargs):
                sections = []

                if environment is not None:
                    sections.append('newrelic-platform:%s' % environment)

                sections.append('newrelic-platform')

                if environment is not None:
                    sections.append('newrelic:%s' % environment)

                sections.append('newrelic')

                for section in sections:
                    try:
                        return _option(name, section, type)
                    except (NoOptionError, NoSectionError):
                        pass

                if 'default' in kwargs:
                    return kwargs['default']

            if app_name is None:
                app_name = os.environ.get('NEW_RELIC_APP_NAME', None)
                app_name = option('app_name', default=app_name)

            if license_key is None:
                license_key = os.environ.get('NEW_RELIC_LICENSE_KEY', None)
                license_key = option('license_key', default=license_key)

        if app_name is not None:
            app_name = app_name.split(';')[0].strip()

        if not license_key or not app_name:
            _logger.fatal('Either the license key or application name was '
                    'not specified for the New Relic platform plugin. The '
                    'plugin has been disabled.')

            return

        _logger.info('New Relic platform plugin reporting to %r.', app_name)

        self.interface = Interface(license_key)
        self.sampler = Sampler(self.interface, app_name)

    def start(self):
        if self.sampler is not None:
            self.sampler.start()
