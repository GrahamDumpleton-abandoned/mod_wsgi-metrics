==================
MOD_WSGI (METRICS)
==================

The mod_wsgi-metrics package is an add on package for Apache/mod_wsgi. It
generates metric information about the run time performance of Apache and
mod_wsgi. At least mod_wsgi version 4.2.0 is required.

In this version, metrics collected cover the performance of the Apache web
server as a whole. In future versions additional metrics will be added
which monitor aspects of mod_wsgi itself.

At the present time the package provides a plugin for the
`New Relic Platform <http://www.newrelic.com/platform>`_. This plugin is
distinct from New Relic's own Python agent for use in monitoring Python web
applications. The plugin instead focuses on metrics specific to Apache and
mod_wsgi. The information from these metrics can be used to help in tuning
your Apache/mod_wsgi installation for best performance.

The New Relic Platform is a free feature of New Relic and so in order to
use this plugin for Apache/mod_wsgi, you do not need to have a paid account
for New Relic.

Even if using the Python agent for New Relic, New Relic provides a free
Lite tier for it, so there is no excuse for not using both the Python agent
and this plugin to give you that extra visibility. Learn about what your
Python web application is really doing. [1]_

Using the New Relic plugin with a mod_wsgi express installation
---------------------------------------------------------------

When using `mod_wsgi express <https://pypi.python.org/pypi/mod_wsgi>`_,
the plugin will be automatically started and will report data when using
the builtin support of mod_wsgi express for New Relic. See the mod_wsgi
express documentation for more information on starting it with New Relic
support enabled.

Using New Relic plugin with a standard mod_wsgi installation
------------------------------------------------------------

If you have installed mod_wsgi as an Apache module direct into your Apache
installation, or have installed an operating system binary package, and are
configuring Apache manually to host your Python web application, additional
setup will be required to enable the plugin.

The steps for manually enabling the plugin are as follows:

1. Create a Python script file called ``server-metrics.py``. In that file
place::

    import logging

    logging.basicConfig(level=logging.INFO,
        format='%(name)s (pid=%(process)d, level=%(levelname)s): %(message)s')

    from mod_wsgi.metrics.newrelic import Agent

    config_file = '/some/path/newrelic.ini'

    agent = Agent(config_file=config_file)
    agent.start()

This would normally be placed along side your Python web application code.

The ``config_file`` variable should be set to the location of the
``newrelic.ini`` agent configuration file you created for use with the New
Relic Python agent.

Alternatively, you can set the New Relic license key and application name
to report to within the Python script file::

    license_key = 'YOUR-NEW-RELIC-LICENSE-KEY'
    app_name = 'THE-APPLICATION-NAME-TO-REPORT-AGAINST'

    agent = Agent(app_name=app_name, license_key=license_key)
    agent.start()

This Python script file would normally be placed along side your Python web
application code.

2. Ensure that the ``mod_status`` module is being loaded into Apache and that
``ExtendedStatus`` is ``On``::

    LoadModule status_module modules/mod_status.so
    ExtendedStatus On

The exact way in which this needs to be done will differ between Apache
installations, especially with Apache installations provided by a Linux
distribution. You should therefore look closely at how this is managed
for your Apache installation.

Note that it is only necessary to load ``mod_status`` and enable
``ExtendedStatus``. It is not necessary to expose the traditional
``/server-status`` URL generally associated with the use of ``mod_status``
as the plugin will not use that. Instead the plugin obtains the information
from the ``mod_wsgi`` module. The ``mod_status`` module still has to be
loaded though, otherwise Apache will not collect the information that is
required.

3. Create a dedicated mod_wsgi daemon process group using the
``WSGIDaemonProcess`` directive. This should have only a single process and
a single thread. It should also enable visibility of internal server
metrics from mod_wsgi using the ``server-metrics`` option::

    WSGIDaemonProcess newrelic display-name=%{GROUP} \
        processes=1 threads=1 server-metrics=On

This daemon process group should not be used to host your actual Python
web application.

4. Specify that the ``server-metrics.py`` Python script file you created
should be loaded when Apache is (re)started using the ``WSGIImportScript``
directive::

    WSGIImportScript /some/path/server-metrics.py \
        process-group=newrelic application-group=%{GLOBAL}

The path should match where you saved the ``server-metrics.py`` script.
The ``process-group`` option should match the name of the daemon process
group created with using the ``WSGIDaemonProcess`` directive.

4. Restart Apache. Within the New Relic UI you should automatically see
a new entry appear in the left hand navigation bar labelled 'mod_wsgi'. The
reported data will then appear under the application name used.

.. [1] Disclaimer: I work for New Relic and am the primary developer of
       the Python agent. So of course it is awesome. The work I do on
       this plugin for the New Relic platform is independent of any work
       I do for New Relic and is done on my own time though. :-)
