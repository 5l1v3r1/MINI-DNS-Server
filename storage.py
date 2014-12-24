import sqlite3
import time

__author__ = 'alex'


class Address(object):
    def __init__(self, domain=None, ip=None, expiration=0.0):
        self.domain = domain
        self.ip = ip
        self.expiration = expiration

    @property
    def time(self):
        return self.expiration - time.time()

    def is_valid(self):
        return bool(self.domain and self.ip)

    def __str__(self):
        return '[{0.ip}] {0.domain} {0.time:.2f}s'.format(self)


class Storage(object):

    name = 'iptables.sqlite'

    expiration = 300

    def __init__(self, name=None, expiration=0):
        self.conn = sqlite3.connect(name or self.name, check_same_thread=False)
        self.expiration = expiration or self.__class__.expiration

    def cleanup(self, cur):
        cur.execute('''DELETE FROM IP WHERE expiration<?''', (time.time() - self.expiration,))

    def create_tables(self):
        cur = self.conn.cursor()
        self.cleanup(cur)

        # Create table
        cur.execute('''CREATE TABLE IF NOT EXISTS IP (domain text, ip text, expiration real)''')

        self.conn.commit()
        cur.close()

    def find(self, domain):
        cur = self.conn.cursor()
        self.cleanup(cur)

        cur.execute('''SELECT * FROM IP WHERE domain=? AND expiration>=?''', (domain, time.time()))

        args = cur.fetchone()

        cur.close()

        return Address(*(args or ()))

    def add(self, domain, ip):
        cur = self.conn.cursor()

        cur.execute('''INSERT INTO IP(domain, ip, expiration) VALUES (?, ?, ?)''', (
            domain, ip, time.time() + self.expiration))

        self.conn.commit()
        cur.close()