#!/usr/bin/env python

from iota import Iota,Address

api = Iota(
    adapter='https://field.carriota.com:443',
  )

def getaddr(address):
    try:
        latest = None
        hashes = api.find_transactions(addresses=[Address(address)])['hashes']
        print("hashes: {}".format(hashes))
        bundles = []
        for b in hashes:
            bundles.append(api.get_bundles(b)['bundles'])

        print("bundles: {}".format(bundles))
        for b in bundles:
            print("b: {}".format(b))
            for bb in b:
                try:
                    print('x')
                    if latest < bb.as_json_compatible()[0]['attachment_timestamp']:
                        latest = bb
                except Exception as e:
                    print(e)

        x = latest.get_messages()
        print(x)
        return x[0]
    except Exception as e:
        print("ERROR: {}".format(e))
        return latest


if __name__ == '__main__':

    import sys
    if len(sys.argv) > 1:
        addr = sys.argv[1]
    else:
        addr = 'YOUR9TEST9ADDRESS9GOES9HERE9NOT9THIS9RANDOM9THING9ADMICA9MADE9UP9SO9GO9CHANGE9ME9THANKYOU9'
    print("Getting latest message at {}".format(addr))
    print(getaddr(addr))
