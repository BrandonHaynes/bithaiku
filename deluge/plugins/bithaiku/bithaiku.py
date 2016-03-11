import threading
import socket
import asyncore
import hashlib
import logging
import json

MIN_SPEED = 1./1024
SERVER_PORT = 12000
WITNESS_PORT = 12001
CLIENT_PORT = 12002
MAX_HAIKU_SIZE = 65535
ALL_INTERFACES = ''

log = logging.getLogger(__name__)


def hash_digest(value):
    return hashlib.sha256(value).hexdigest()


class BitHaikuMonitor:
    def __init__(self, torrent, haiku, running_delay=0.1, paused_delay=5):
        self.torrent = torrent
        self.haiku = haiku
        self.verifying_peers = []
        self.verified_peers = []
        self.pending_peers = []
        self.download_speed = self.torrent.options['max_download_speed']
        self.upload_speed = self.torrent.options['max_upload_speed']
        self.running_delay = running_delay
        self.paused_delay = paused_delay
        self.terminated = False

        self.torrent.set_max_download_speed(MIN_SPEED)
        self.torrent.set_max_upload_speed(MIN_SPEED)

    @property
    def delay(self):
        return self.paused_delay if self.verifying_peers else self.running_delay

    def monitor(self):
        if not self.terminated:
            success = all(map(self.verify_peer,
                              (peer['ip']
                               for peer in self.torrent.get_peers() + [{'ip': ip} for ip in self.pending_peers]
                               if peer['ip'] not in (self.verified_peers + self.verifying_peers))))

            if self.verifying_peers or not success:
                self.pause_torrent()
            else:
                self.resume_torrent()

            threading.Timer(self.delay, self.monitor).start()

    def terminate(self):
        self.terminated = True

    def verify_peer(self, ip):
        self.pause_torrent()
        return BitHaikuServerVerifier(ip, self).verify()

    def pause_torrent(self):
        self.torrent.set_max_download_speed(MIN_SPEED)
        self.torrent.set_max_upload_speed(MIN_SPEED)
        self.torrent.pause()

    def resume_torrent(self):
        self.torrent.set_max_download_speed(self.download_speed)
        self.torrent.set_max_upload_speed(self.upload_speed)
        self.torrent.resume()

    def abandon_verification(self, ip):
        self.pause_torrent()
        self.verifying_peers.remove(ip)
        self.pending_peers.append(ip)
        return False

    def verified(self, ip):
        log.error("Verified " + ip)
        self.verified_peers.append(ip)
        self.verifying_peers.remove(ip)


class BitHaikuServerVerifier:
    def __init__(self, ip, monitor):
        log.error('Verifying ' + ip)
        self.monitor = monitor
        self.ip = ip
        self.host, self.port = ip.split(":")
        self.monitor.verifying_peers.append(ip)
        if ip in self.monitor.pending_peers:
            self.monitor.pending_peers.remove(ip)

    def verify(self):
        client = socket.socket()
        client.settimeout(5)

        try:
            client.connect(('localhost', SERVER_PORT))
            # client.connect((self.host, SERVER_PORT))
            client.sendall(json.dumps({"host": "localhost", "data": self.monitor.haiku}))
        except socket.error as e:
            log.error(e)
            return self.monitor.abandon_verification(self.ip)
        else:
            log.error("Expecting hash " + hash_digest(self.monitor.haiku))
            BitHaikuWitnessVerifier(self.ip, self.monitor).resolve()
            return True
        finally:
            client.close()


class BitHaikuWitnessVerifier(asyncore.dispatcher_with_send):
    def __init__(self, ip, monitor):
        asyncore.dispatcher.__init__(self)
        self.monitor = monitor
        self.ip = ip

    def resolve(self):
        try:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.set_reuse_addr()
            self.bind((ALL_INTERFACES, CLIENT_PORT))
            self.listen(8)
            asyncore.loop()
        except socket.error as e:
            log.error(e)
            self.monitor.abandon_verification(self.ip)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            client, address = pair
            log.error("Incoming connection from " + str(address))

            data = client.recv(MAX_HAIKU_SIZE).strip()
            client.close()

            log.error("Read " + data)

            # {"hash": "9fc8b3b5a8b87a1d4886bb99c1450d9fed80191e94efcba0c0132296c3e4cce0"}
            if self.extract_hash(data) == hash_digest(self.monitor.haiku):
                self.monitor.verified(self.ip)
                self.close()
            else:
                log.error("Received value {} did not match expected value".format(data))

    @staticmethod
    def extract_hash(value):
        try:
            document = json.loads(value)
            return document['hash']
        except (ValueError, KeyError):
            return None
