/*
Script: bithaiku.js
    The client-side javascript code for the BitHaiku plugin.

Copyright:
    (C) Brandon Haynes, Ryan Maas 2016 <bhaynes@cs.washington.edu, maas@cs.washington.edu>

    This file is part of BitHaiku and is licensed under GNU General Public License 3.0, or later, with
    the additional special exception to link portions of this program with the OpenSSL library.
    See LICENSE for more details.
*/

BitHaikuPlugin = Ext.extend(Deluge.Plugin, {
    constructor: function(config) {
        config = Ext.apply({
            name: "BitHaiku"
        }, config);
        BitHaikuPlugin.superclass.constructor.call(this, config);
    },

    onDisable: function() {

    },

    onEnable: function() {

    }
});
new BitHaikuPlugin();
