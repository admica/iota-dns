#!/usr/bin/env python

from iota import Iota,Address,ProposedTransaction,TryteString,Tag
from updater.get_data import Get_Data
from updater.getaddr import getaddr
from time import sleep, time
import argparse
import yaml

class Lookup():

    def __init__(self, config_file=None):
        if not config_file:
            self.config_file = 'config.yaml'

        # load config
        self.CONFIG = yaml.load(open(config_file, 'r'))

        # encryption cipher
        self.cipher = Cipher(self.CONFIG['key'])
        
    def fetch(self, addr):
        """get iota payload for a given address, return decrypted contents"""
        # get encrypted payload
        encr = getaddr(addr)

        # decrypt
        raw = self.cipher.decrypt(encr)

        # decode
        d = json.loads(raw)

        # include addr
        d['addr'] = addr

        return d

    def read(self, addr):
        """read a file looking for any number of ip address mappings
        return the contents as a dictionary.

        Example: 2 ip addresses with single and multiple name mappings:
        1.2.3.4 name.com alias1.name.com
        2.2.2.2 other.com
        """

        # init dictionary with addr filename
        d = {}
        d['addr'] = addr

        with open(addr, 'r') as f:
            for line in f.readlines():
                parts = line.strip().split(' ')
                ip = parts[0]
                names = parts[1:]
                d[ip] = names
        # d may be just the addr if there were no mappings or the file did not exist
        return d

    def write(self, d):
        """write output file from dictionary"""
        if len(d) < 2:
            print("No mappings found, not writing file")
            return False

        try:
            filename = d['addr']
            with open(filename, 'w') as f:
                for key in d:
                    # parse d[key] == ['name1','name2',...] into string
                    if key != 'addr':
                        payload = str(key)
                        for name in d[key]:
                            payload += " {}".format(name)
                        # output line
                        f.writeline(payload)

        except Exception as e:
            print("Error in write: {}".format(e))        
            return False
        return True

    def fetchall(self):
        """get iota payload for every known address"""
        for addr in self.CONFIG['addresses']:
            try:
                d = self.fetch(addr)
            except Exception as e:
                print("Error in fetchall: {}".format(e))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, help="Config filename to parse.", default="config.yaml")
    args = parser.parse_args()

    obj = Updater(config=args.config)
    print(obj)

