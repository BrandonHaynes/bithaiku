#
# -*- coding: utf-8 -*-#

# Copyright (C) 2016 Brandon Haynes, Ryan Maas <bhaynes@cs.washington.edu, maas@cs.washington.edu>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
# Copyright (C) 2010 Pedro Algarvio <pedro@algarvio.me>
#
# This file is part of BitHaiku and is licensed under GNU General Public License 3.0, or later, with
# the additional special exception to link portions of this program with the OpenSSL library.
# See LICENSE for more details.
#

from deluge.plugins.init import PluginInitBase
from bithaiku import BitHaikuMonitor

class CorePlugin(PluginInitBase):
    def __init__(self, plugin_name):
        from core import Core as _plugin_cls
        self._plugin_cls = _plugin_cls
        super(CorePlugin, self).__init__(plugin_name)

class GtkUIPlugin(PluginInitBase):
    def __init__(self, plugin_name):
        from gtkui import GtkUI as _plugin_cls
        self._plugin_cls = _plugin_cls
        super(GtkUIPlugin, self).__init__(plugin_name)

class WebUIPlugin(PluginInitBase):
    def __init__(self, plugin_name):
        from webui import WebUI as _plugin_cls
        self._plugin_cls = _plugin_cls
        super(WebUIPlugin, self).__init__(plugin_name)
