#!/usr/bin/env python3

import time
from datetime import datetime as dt
import shutil

hosts_path = "/etc/hosts.orig"
replacement_hosts_path = "/etc/hosts.replacement"
redirect = "127.0.0.1"

website_list = ["connect.facebook.net", "scorecardresearch.com", "chartbeat.net", "doubleclick.net", "nr-data.net",
                "technoratimedia.com"]


def block_sites():
    with open(hosts_path, 'r+') as hfile:
        hcontent = hfile.read()
        for site in website_list:
            if site in hcontent:
                pass
            else:
                hfile.write(redirect + " " + site + '\n')


def unblock_sites():
    with open(hosts_path, 'r') as hfile:
        hcontent = hfile.readlines()

    with open(replacement_hosts_path, 'w') as hfile:
        for line in hcontent:
            if not any(site in line for site in website_list):
                hfile.write(line)

    shutil.move(hosts_path, "{}.{:04d}{:02d}{:02d}".format(hosts_path, dt.now().year, dt.now().month, dt.now().day))
    shutil.move(replacement_hosts_path, hosts_path)
# Other options
#    hfile.seek(0)
#    hfile.truncate()


# while True:
if dt(dt.now().year, dt.now().month, dt.now().day, 10) \
        < dt.now() \
        < dt(dt.now().year, dt.now().month, dt.now().day, 16):
    print("Working hours...")
    block_sites()
else:
    print("Fun hours...")
    unblock_sites()
#    time.sleep(5)
