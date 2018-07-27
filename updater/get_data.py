#!/usr/bin/env python

import yaml
import requests
import json
from cipher import Cipher

class Get_Data():

    def __init__(self, config_file=None, config_orig=None):
        if not config_file:
            config_file = "config.yaml"
        if not config_orig:
            config_orig = "config.yaml.sample"

        # load config
        self.config_file = config_file
        try:
            self.CONFIG = yaml.load(open(config_file,'r'))
        except IOError:
            self.CONFIG = yaml.load(open(config_orig, 'r'))

        self.CONFIG_ORIG = dict(self.CONFIG) # keep loaded copy for comparison

        # encryption cipher
        self.cipher = Cipher(self.CONFIG['key'])

        self.CONFIG['seed'] = self.get_seed()

        if self.CONFIG['addr'] is None:
            self.debug("Getting new address")
            self.get_addr()

        # if anything changed, it gets saved
        self.save()

        # fetch ip
        self.ip = None
        self.fetch()

        self.seed = self.CONFIG.get('seed','')
        self.addr = self.CONFIG.get('addr','')
        self.index = self.CONFIG.get('index','')
        self.name = self.CONFIG.get('name','')
        self.ns = self.CONFIG.get('ns','')
        self.node = self.CONFIG.get('node','')
        self.url = self.CONFIG.get('url','')
        self.interval = self.CONFIG.get('interval','')
        self.forced_interval = self.CONFIG.get('forced_interval', '')
        self.update_retries = self.CONFIG.get('update_retries', 3)

    def fetch(self):
        """Lookup current public ip address"""
        import sys
        r = requests.get( self.CONFIG['url'] )
        ip = r.json()['ip']
        if not ip:
            return False
        self.ip_last = self.ip # save last
        self.ip = ip # save current
        return True

    def ip_changed(self):
        if self.ip_last == None:
            # inital, changed
            return True
        if self.ip_last != self.ip:
            # changed
            return True
        # no change detected
        return False

    def get_seed(self):
        """load seed from config or generate one if undefined"""
        seed = self.CONFIG['seed']
        if seed is None:
            seed = self.generate_seed()
            self.debug("Generated new seed: {} {}".format(seed, len(seed)))
        else:
            self.debug("Loaded seed: {} {}".format(seed, len(seed)))
        return seed

    def get_addr(self):
        """Get an iota address"""
        if self.CONFIG['index'] is None:
            self.CONFIG['index'] = 0

        from iota import Iota
        try:
            api = Iota(self.CONFIG['node'], self.CONFIG['seed'],'utf-8')
            d = api.get_new_addresses(index=self.CONFIG['index'], count=1)
            self.CONFIG['addr'] = str(d['addresses'][-1])
            self.debug("Address at index {}: {}".format(self.CONFIG['index'], self.CONFIG['addr']))
        except Exception as e:
            print(e)
            return False
        return True

    def generate_seed(self, length=81):
        """Generate an iota seed"""
        from random import SystemRandom

        alphabet = '9ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        generator = SystemRandom()

        # sum of digits of a random memory pointer to throw away a random number of randoms
        start = sum(list(map(int, str(id(generator)))))

        superset = list(generator.choice(alphabet) for _ in range(length+start))
        return ''.join(superset[start:start+length])

    def save(self):
        """write out any changes to config"""
        if self.CONFIG == self.CONFIG_ORIG:
            self.debug("No changes to config.")
        else:
            self.debug("Config changed, updating.")
            with open(self.config_file, 'w') as f:
                yaml.dump(self.CONFIG, f, default_flow_style=False)
                self.CONFIG_ORIG = dict(self.CONFIG) # for future saves
                self.debug("New config saved.")

    def get_message(self, encrypt=True):
        """return formatted message for iota transaction"""
        d = {}
        if self.ip:
            d['ip'] = self.ip
        if self.name:
            d['name'] = self.name
        if self.ns:
            d['ns'] = self.ns

        raw = json.dumps(d)
        if encrypt:
            return self.cipher.encrypt(raw)
        else:
            return raw

    def __repr__(self):
        string  = "IP Address: {}\n".format(self.ip)
        string += "name: {}\n".format(self.name)
        string += "NS:   {}\n".format(self.ns)
        string += "Node: {}\n".format(self.node)
        string += "URL:  {}\n".format(self.url)
        string += "Interval: {}\n".format(self.interval)
        string += "Forced Interval: {}\n".format(self.forced_interval)
        string += "Seed:  {}\n".format(self.seed)
        string += "Addr:  {}\n".format(self.addr)
        string += "Index: {}\n".format(self.index)
        string += "Message raw: {}\n".format(self.get_message(encrypt=False))
        string += "Message enc: {}".format(self.get_message())
        return string
 
    def debug(self, msg):
        """Handle verbose output"""
        #print msg
        return None


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, help="Config filename to load/save.", default="config.yaml")
    args = parser.parse_args()

    obj = Get_Data(config_file=args.config)
    print(obj)

