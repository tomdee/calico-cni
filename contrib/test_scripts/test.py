import json
import netaddr
import os
import random
import string
from subprocess import check_call, check_output

import sys

def create_container():
    container_id = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for _ in
        range(10))
    netnspath = "/var/run/netns/" + container_id
    check_call("ip netns add " + container_id, shell=True)
    check_call("ip netns exec %s ip link set lo up " % container_id,
               shell=True)

    os.environ.update({"CNI_COMMAND": "ADD",
                       "CNI_CONTAINERID": container_id,
                       "CNI_NETNS": netnspath,
                       "CNI_IFNAME": "eth0",
                       "CNI_PATH": "/home/gulfstream/go/src/github.com/appc/cni/bin/"})

    plugin = ""
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
        plugin = data["type"]
    with open(sys.argv[1], 'r') as f:
        ip = json.loads(check_output(plugin, stdin=f, env=os.environ, shell=True))["ip4"]["ip"]
    return (container_id, netaddr.IPNetwork(ip).ip)

def delete_container(container_id):
    netnspath = "/var/run/netns/" + container_id
    os.environ.update({"CNI_COMMAND": "DEL",
                       "CNI_CONTAINERID": container_id,
                       "CNI_NETNS": netnspath,
                       "CNI_IFNAME": "eth0",
                       "CNI_PATH": "/home/gulfstream/go/src/github.com/appc/cni/bin/"})
    os.environ["CNI_COMMAND"] = "DEL"
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
        plugin = data["type"]

    with open(sys.argv[1], 'r') as f:
        check_call(plugin, stdin=f, env=os.environ, shell=True)
    check_call("ip netns delete %s" % container_id, shell=True)

def run_command(container_id, command):
    check_call("ip netns exec %s %s" % (container_id, command), shell=True)

cont1, ip = create_container()
cont2, _ = create_container()

run_command(cont1, "date")
run_command(cont1, "sleep 2")
run_command(cont2, "ping %s" % ip)

delete_container(cont1)
# delete_container(cont2)
