#!/usr/bin/env python

from iota import Iota,Address,ProposedTransaction,TryteString,Tag
from get_data import Get_Data
from time import sleep, time
import argparse

class Updater():

    def __init__(self, config=None):
        self.data = Get_Data(config_file=args.config)

    def update(self):
        try:
            api = Iota(
                adapter = self.data.node,
                seed = self.data.seed,
            )
            bundle = api.send_transfer(
                depth=7,
                transfers = [
                    ProposedTransaction(
                        address = Address(
                            self.data.addr
                        ),
                        value = 0,
                        tag = Tag(b'ADMICA'),
                        message = TryteString.from_string(self.data.get_message()),
                    ),
                ]
            )
        except Exception as e:
            print("ERROR: {}".format(e))
            return False
        return True


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, help="Config filename to load/save.", default="config.yaml")
    parser.add_argument("-d", action="store_true", dest="daemon", help="Run as a daemon in the background.", default=False)
    args = parser.parse_args()

    updater = Updater(args.config)
    if args.daemon:

        time_start = time()
        time_last = time_start
        time_sleep = updater.data.interval * 3600
        time_force = updater.data.forced_interval * 3600

        def do_update():
            print("Updating node: {}".format(updater.data.node))
            for x in range(0,updater.data.update_retries):
                if updater.update():
                    global time_last
                    time_last = time()
                    print("Updated {}".format(updater.data.addr))
                    break
                else:
                    print("Update failed.")

        # initial run
        do_update()

        while True:
            if updater.data.fetch():
                print(updater.data.get_message(encrypt=False))

                if updater.data.ip_changed():
                    do_update()
                    print("Checking IP in {} hours.".format(updater.data.interval))
                    sleep(time_sleep)

                t = int(time() - time_last)
                time_future = t + time_sleep

                if time_future > time_force:
                    short = time_future - time_force
                    print("Sleeping %s seconds before forced update." % short)
                    sleep(short)
                    do_update()                
                else:
                    print("Checking IP in {} hours.".format(updater.data.interval))
                    sleep(time_sleep)
            else:
                print("ERROR: Failed to fetch ip address.")

    # run once
    print(updater.data)
    print(updater.update())

