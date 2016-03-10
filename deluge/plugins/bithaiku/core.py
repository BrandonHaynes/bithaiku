#
# -*- coding: utf-8 -*-#

# Copyright (C) 2016 Brandon Haynes, Ryan Maas <bhaynes@cs.washington.edu, maas@cs.washington.edu>

import logging
from functools import partial
from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export
from deluge.plugins.bithaiku import BitHaikuMonitor

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

    @staticmethod
    def on_torrent_added(plugin, torrent_id, *args):
        log.error("Torrent added; initiating BitHaiku")
        torrent = component.get("TorrentManager")[torrent_id]
        #torrent.force_error_state("Waiting for BitHaiku protocol to complete", False)
        #torrent.pause()
        #torrent.set_max_download_speed(-1)
        #torrent.set_max_upload_speed(-1)
        plugin.config["torrents"].append(torrent_id)
        plugin.config.save()

        BitHaikuMonitor(torrent, component.get("Core").session).monitor()

    def enable(self):
        self.config = deluge.configmanager.ConfigManager("bithaiku.conf", DEFAULT_CONFIG)
        component.get("EventManager").register_event_handler("TorrentAddedEvent", partial(self.on_torrent_added, self))
        log.error("BitHaiku plugin enabled.")

    def disable(self):
        pass

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
