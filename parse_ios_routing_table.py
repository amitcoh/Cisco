# -*- coding: utf-8 -*-

import re, json
from netmiko import Netmiko

cisco3725 = {
    'device_type': 'cisco_ios',
    'ip':   '192.168.56.254',
    'username': 'cisco',
    'password': 'cisco'
    }

re_dictionary = {
    'nexthop': 'via (\d{1,3}(\.\d{1,3}){3})',
    'destination': '(\d{1,3}(\.\d{1,3}){3})(/\d{1,2})?',
    'admin_distance': '\[\d*/',
    'cost': '/\d*]',
    'interface': ', [a-zA-z]+\d{1,3}(/?\d{1,3})?(\.\d+)?'
}

def send_cmd(device, cmd_list):
    net_connect = Netmiko(**device)
    response = {}
    for command in cmd_list:
        response[command] = net_connect.send_command(command)
    return response


def strip_routing_table(routing_table):
    response = []
    if routing_table[0].startswith('Gateway of last'):
        routing_table.remove(routing_table[0])
    for line in routing_table:
        if len(line) > 0:
            if line[0] != ' ':
                response.append(line)
    return response


def routing_parser(routing_table):
    routing_table = strip_routing_table(routing_table)
    response = []
    for line in routing_table:
        # check destination
        destination = re.search(re_dictionary['destination'], line).group(0)
        if destination:
            destination.encode('ascii', 'ignore')
        # check interface
        iface = re.search(re_dictionary['interface'], line).group(0)
        if iface:
            iface.encode('ascii','ignore')
            iface = iface.strip(', ')
        # check connected
        connected = (line[0] == 'C')
        # if not directly connected continue checks
        if connected:
            admin_distance = 0
            cost = 0
            nexthop = None
        else:
            # check admin distance
            admin_distance = re.search(re_dictionary['admin_distance'], line).group(0)
            if admin_distance:
                admin_distance.encode('ascii', 'ignore')
                admin_distance = admin_distance.strip('[')
                admin_distance = admin_distance.strip('/')
            # check cost
            cost = re.search(re_dictionary['cost'], line).group(0)
            if cost:
                cost.encode('ascii', 'ignore')
                cost = cost.strip('/')
                cost = cost.strip(']')
            # check nexthop address
            nexthop = re.search(re_dictionary['nexthop'], line).group(0)
            if nexthop:
                nexthop.encode('ascii', 'ignore')
                nexthop = nexthop.strip('via ')
        # check default route
        default_route = (line[1] == '*')
        # build response
        if destination:
            response.append(dict(
                destination=destination,
                iface=iface,
                connected=connected,
                admin_distance=admin_distance,
                cost=cost,
                nexthop=nexthop,
                default_route=default_route
            ))
    return response


def main():
    cmd_list = ['show ip route | b Gateway of last']
    routing_table = send_cmd(cisco3725, cmd_list)[cmd_list[0]].split('\n')
    routing_table_list = routing_parser(routing_table)
    print json.dumps(routing_table_list, indent=2)



if __name__ == "__main__":
    main()