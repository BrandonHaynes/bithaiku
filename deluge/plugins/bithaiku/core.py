#
# -*- coding: utf-8 -*-#

# Copyright (C) 2016 Brandon Haynes, Ryan Maas <bhaynes@cs.washington.edu, maas@cs.washington.edu>

import logging
from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export

DEFAULT_CONFIG = {
    "test": "foo",
    "commands": []
}

EXECUTE_ID = 0
EXECUTE_EVENT = 1
EXECUTE_COMMAND = 2

EVENT_MAP = {
    "complete": "TorrentFinishedEvent",
    "added": "TorrentAddedEvent",
    "removed": "TorrentRemovedEvent"
}

log = logging.getLogger(__name__)


class Core(CorePluginBase):
    def __init__(self, plugin_name):
        super(Core, self).__init__(plugin_name)
        self.config = None

    @staticmethod
    def on_torrent_added(torrent_id, *args):
        log.error("Torrent added")

    def enable(self):
        self.config = deluge.configmanager.ConfigManager("bithaiku.conf", DEFAULT_CONFIG)
        component.get("EventManager").register_event_handler("TorrentAddedEvent", self.on_torrent_added)

        log.error("BitHaiku plugin enabled.")

    def disable(self):
        pass

    def update(self):
        pass

    @export
    def set_config(self, config):
        """Sets the config dictionary"""
        for key in config.keys():
            self.config[key] = config[key]
        self.config.save()

    @export
    def get_config(self):
        """Returns the config dictionary"""
        return self.config.config
