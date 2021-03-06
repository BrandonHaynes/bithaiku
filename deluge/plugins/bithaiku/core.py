#
# -*- coding: utf-8 -*-#

# Copyright (C) 2016 Brandon Haynes, Ryan Maas <bhaynes@cs.washington.edu, maas@cs.washington.edu>

import logging
import collections
from functools import partial
from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export
from deluge.plugins.bithaiku import BitHaikuMonitor
from deluge.plugins.bithaiku.listeners import ServerTCPHandler, WitnessTCPHandler
from deluge.plugins.bithaiku.configuration import BitHaikuConfiguration
from deluge.plugins.bithaiku.dht import BitHaikuDHT

DEFAULT_CONFIG = {
    "haiku": "Hippopotamus\n"
             "Antihippopotamus\n"
             "Annihilation",
    "commands": [],
    "torrents": []
}

log = logging.getLogger(__name__)


class Core(CorePluginBase):
    def __init__(self, plugin_name):
        super(Core, self).__init__(plugin_name)
        self.config = None
        self.monitors = {}
        self.configuration = BitHaikuConfiguration()
        self.dht = None
        self.listeners = collections.namedtuple('Listeners', 'server witness client')

    @staticmethod
    def on_torrent_added(plugin, torrent_id, *args):
        log.error("Torrent added; initiating BitHaiku")
        torrent = component.get("TorrentManager")[torrent_id]

        plugin.config["torrents"].append(torrent_id)
        plugin.config.save()
        plugin.monitors[torrent_id] = BitHaikuMonitor(plugin.configuration, torrent, plugin.config["haiku"], plugin.dht)
        plugin.monitors[torrent_id].monitor()

    @staticmethod
    def on_torrent_removed(plugin, torrent_id, *args):
        if torrent_id in plugin.monitors:
            plugin.monitors[torrent_id].terminate()
            del plugin.monitors[torrent_id]

    def enable(self):
        self.config = deluge.configmanager.ConfigManager("bithaiku.conf", DEFAULT_CONFIG)
        component.get("EventManager").register_event_handler("TorrentAddedEvent",
                                                             partial(self.on_torrent_added, self))
        component.get("EventManager").register_event_handler("TorrentRemovedEvent",
                                                             partial(self.on_torrent_removed, self))
        self.dht = BitHaikuDHT(self.configuration)
        self.listeners.server = ServerTCPHandler.listen(self.configuration, self.dht)
        self.listeners.witness = WitnessTCPHandler.listen(self.configuration)
        log.error("BitHaiku plugin enabled.")

    def disable(self):
        for monitor in self.monitors.values():
            monitor.terminate()
        self.monitors = {}
        log.error("Stopping server")
        self.listeners.server.terminate()
        self.listeners.witness.terminate()
        log.error("Stopped server")

    def update(self):
        pass

    @export
    def set_config(self, config):
        for key in config.keys():
            self.config[key] = config[key]
        self.config.save()

    @export
    def get_config(self):
        return self.config.config
