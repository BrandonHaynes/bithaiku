import threading
import logging

log = logging.getLogger(__name__)

MIN_SPEED = 1./1024


class BitHaikuMonitor:
    def __init__(self, torrent, ip_filter, running_delay=0.1, paused_delay=2):
        self.lock = threading.Lock()
        self.torrent = torrent
        self.ip_filter = ip_filter
        self.verifying_peers = []
        self.verified_peers = []
        self.download_speed = self.torrent.options['max_download_speed']
        self.upload_speed = self.torrent.options['max_upload_speed']
        self.running_delay = running_delay
        self.paused_delay = paused_delay
        self.torrent.set_max_download_speed(MIN_SPEED)
        self.torrent.set_max_upload_speed(MIN_SPEED)

    @property
    def delay(self):
        return self.paused_delay if self.verifying_peers else self.running_delay

    def monitor(self):
        with self.lock:
            map(self.verify_peer, (peer['ip'] for peer in self.torrent.get_peers()
                                   if peer['ip'] not in (self.verified_peers + self.verifying_peers)))

            if self.verifying_peers:
                self.pause_torrent()
            else:
                self.resume_torrent()

            threading.Timer(self.delay, self.monitor).start()

    def verify_peer(self, ip):
        log.error('Verifying ' + ip)
        BitHaikuVerifier(ip, self).verify()

    def pause_torrent(self):
        self.torrent.set_max_download_speed(MIN_SPEED)
        self.torrent.set_max_upload_speed(MIN_SPEED)
        self.torrent.pause()

    def resume_torrent(self):
        self.torrent.set_max_download_speed(self.download_speed)
        self.torrent.set_max_upload_speed(self.upload_speed)
        self.torrent.resume()


class BitHaikuVerifier:
    def __init__(self, ip, monitor):
        self.monitor = monitor
        self.ip = ip
        self.monitor.verifying_peers.append(ip)

    def verify(self):
        threading.Timer(10, self.verified).start()

    def verified(self):
        with self.monitor.lock:
            log.error("Verified  " + self.ip)
            self.monitor.verified_peers.append(self.ip)
            self.monitor.verifying_peers.remove(self.ip)


